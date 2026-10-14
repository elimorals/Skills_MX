"""Cliente mp_donatarias_sat — Padrón donatarias autorizadas SAT.

Tools:
1. **consultar_donataria(rfc)** — Verifica si un RFC está autorizado como donataria
2. **buscar_donatarias(razon_social, [entidad])** — Búsqueda fuzzy por nombre
3. **listar_por_entidad(entidad)** — Lista donatarias de un estado
4. **estadisticas_padron()** — Stats del padrón completo

Fuente real (validada 2026-10-14): "Directorio de Donatarias Autorizadas" del
minisitio SAT. Se lee la página `padron_directorio.html`, se toma el XLSX más
reciente (`Dir_<año>.xlsx`, ~5.7 MB, ~15k filas / ~10k RFC) y se parsea con la
stdlib (zipfile + xml). El directorio refleja el Anexo 14 RMF publicado en el DOF
más las actualizaciones del SAT.

Real por default (fuente pública). Mock solo con PLUGINS_MX_MOCK=1. Si la descarga
falla → UpstreamError (sin fallback a mock). Directorio parseado en cache 7 días.
"""

from __future__ import annotations

import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Optional

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import McpError, NotFoundError, UpstreamError, ValidationError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402


NAMESPACE = "donatarias_sat"

# RFC: PM 12 chars, PF 13 chars
RFC_REGEX = re.compile(r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$")

URL_DIRECTORIO_SAT = "https://www.sat.gob.mx/minisitio/DonatariasAutorizadas/padron_directorio.html"
_RE_XLSX_DIRECTORIO = re.compile(r'href="(documentos/padron_donatarias/Dir_\d{4}[^"]*\.xlsx)"', re.I)
_NS_XLSX = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
CACHE_DIRECTORIO_DIAS = 7

# Estados MX para validación
ESTADOS_MX = {
    "AGS", "BC", "BCS", "CAMP", "CDMX", "CHIH", "CHIS", "COAH", "COL", "DGO",
    "EDOMEX", "GRO", "GTO", "HID", "JAL", "MICH", "MOR", "NAY", "NL", "OAX",
    "PUE", "QRO", "QROO", "SIN", "SLP", "SON", "TAB", "TAM", "TLAX", "VER",
    "YUC", "ZAC",
}

# Rubros de actividad (Art. 79 LISR fracc.)
RUBROS_DONATARIA = {
    "asistencia_social": "Asistencia o beneficencia (orfanatos, casas hogar, comedores)",
    "educacion": "Enseñanza (educación básica, media, superior, becas)",
    "investigacion_cientifica": "Investigación científica y tecnológica",
    "cultura": "Promoción y difusión de cultura, arte, historia",
    "ecologia": "Ecología y preservación del medio ambiente",
    "reproduccion_especies": "Reproducción de especies en protección",
    "apoyo_economico": "Apoyo a personas con recursos limitados",
    "desarrollo_social": "Desarrollo social",
    "obras_publicas": "Obras o servicios públicos",
    "bibliotecas_museos": "Bibliotecas, museos privados de servicio público",
    "becas": "Otorgamiento de becas (Art. 79 fracc. XVII y 83 LISR)",
    "convenio_eua": "Donativos deducibles en EUA (convenio fiscal México-EUA, Art. 82 LISR)",
}

# Letra de "ACTIVIDAD O FIN AUTORIZADO" en el directorio SAT → clave de rubro
RUBRO_POR_LETRA = {
    "A": "asistencia_social", "B": "educacion", "C": "investigacion_cientifica",
    "D": "cultura", "E": "becas", "F": "ecologia", "G": "reproduccion_especies",
    "H": "apoyo_economico", "I": "obras_publicas", "J": "bibliotecas_museos",
    "K": "bibliotecas_museos", "L": "desarrollo_social", "M": "convenio_eua",
}

# Nombre de entidad tal como viene en el directorio (normalizado) → clave
ENTIDAD_POR_NOMBRE = {
    "aguascalientes": "AGS", "baja california": "BC", "baja california sur": "BCS",
    "campeche": "CAMP", "ciudad de mexico": "CDMX", "chihuahua": "CHIH", "chiapas": "CHIS",
    "coahuila de zaragoza": "COAH", "colima": "COL", "durango": "DGO", "mexico": "EDOMEX",
    "guerrero": "GRO", "guanajuato": "GTO", "hidalgo": "HID", "jalisco": "JAL",
    "michoacan de ocampo": "MICH", "morelos": "MOR", "nayarit": "NAY", "nuevo leon": "NL",
    "oaxaca": "OAX", "puebla": "PUE", "queretaro": "QRO", "quintana roo": "QROO",
    "sinaloa": "SIN", "san luis potosi": "SLP", "sonora": "SON", "tabasco": "TAB",
    "tamaulipas": "TAM", "tlaxcala": "TLAX", "veracruz de ignacio de la llav": "VER",
    "yucatan": "YUC", "zacatecas": "ZAC",
}


def _normalizar(s: str) -> str:
    """NFKD + strip acentos + lower para matching robusto."""
    if not s:
        return ""
    nfkd = unicodedata.normalize("NFKD", s)
    sin_acentos = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sin_acentos.lower().strip()


class DonatariasSatClient:
    """Cliente padrón donatarias SAT."""

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _is_mock(self) -> bool:
        if os.environ.get("MP_DONATARIAS_SAT_REAL") == "1":
            return False
        return is_mock_mode(credential_env_vars=[], default_when_no_creds=False)

    def _log(self, op: str, params: dict[str, Any]) -> None:
        safe = dict(params)
        if "rfc" in safe and safe["rfc"]:
            safe["rfc_hash"] = Bitacora.hash_sensitive(str(safe.pop("rfc")))
        self._bitacora.log(op, success=True, params_summary=safe)

    # ============================================================
    # Tools principales
    # ============================================================

    def consultar_donataria(self, rfc: str) -> dict[str, Any]:
        """Verifica si un RFC está autorizado como donataria.

        Args:
            rfc: RFC persona moral (12) o física (13)

        Returns:
            {
              "rfc": str,
              "autorizada": bool,
              "razon_social": str | None,
              "entidad": str | None,
              "rubro": str | None,
              "fecha_autorizacion": str | None,  # YYYY-MM-DD
              "vigencia_anexo_14": str,           # año fiscal vigente
              "puede_emitir_recibo_deducible": bool,
              "advertencias": [...],
              "url_consultado": URL_DIRECTORIO_SAT,
              "simulated": bool
            }
        """
        rfc_norm = rfc.upper().strip()
        if not RFC_REGEX.match(rfc_norm):
            raise ValidationError(
                f"RFC '{rfc}' inválido. Formato: 12 chars (PM) o 13 chars (PF)."
            )

        cache_key = f"donataria_{'mock' if self._is_mock() else 'real'}_{rfc_norm}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("consultar_donataria", {"rfc": rfc_norm})

        if self._is_mock():
            resultado = self._mock_donataria(rfc_norm)
        else:
            resultado = self._consultar_real(rfc_norm)

        self._cache.set(cache_key, resultado, ttl_days=CACHE_DIRECTORIO_DIAS)
        return resultado

    def buscar_donatarias(
        self,
        razon_social: str,
        entidad: Optional[str] = None,
        limite: int = 20,
    ) -> dict[str, Any]:
        """Búsqueda fuzzy por razón social, opcionalmente filtrada por estado.

        Útil cuando NO se tiene el RFC.
        """
        if not razon_social or len(razon_social.strip()) < 3:
            raise ValidationError("razon_social debe tener al menos 3 caracteres.")
        if limite < 1 or limite > 100:
            raise ValidationError("limite entre 1 y 100.")
        if entidad and entidad.upper() not in ESTADOS_MX:
            raise ValidationError(
                f"Entidad '{entidad}' no válida. Use claves: {sorted(ESTADOS_MX)[:5]}..."
            )

        razon_norm = _normalizar(razon_social)
        self._log("buscar_donatarias", {
            "razon": razon_norm[:50], "entidad": entidad, "limite": limite,
        })

        if self._is_mock():
            return self._mock_busqueda(razon_norm, entidad, limite)
        return self._buscar_real(razon_norm, entidad, limite)

    def listar_por_entidad(self, entidad: str) -> dict[str, Any]:
        """Lista donatarias de una entidad federativa."""
        ent_norm = entidad.upper().strip()
        if ent_norm not in ESTADOS_MX:
            raise ValidationError(
                f"Entidad '{entidad}' no válida. Estados MX: {sorted(ESTADOS_MX)}"
            )

        self._log("listar_por_entidad", {"entidad": ent_norm})

        if self._is_mock():
            return mark_simulated({
                "entidad": ent_norm,
                "total": 250 if ent_norm == "CDMX" else 50,
                "donatarias": [
                    {
                        "rfc": f"DON{i:03d}010101AB{i:01d}"[:12],
                        "razon_social": f"FUNDACION MOCK {ent_norm} {i}",
                        "rubro": "asistencia_social",
                    }
                    for i in range(1, 11)
                ],
                "url_consultado": URL_DIRECTORIO_SAT,
                "nota": "Listado limitado a 10 en mock. Path real devuelve completo.",
            })

        return self._listar_real(ent_norm)

    def estadisticas_padron(self) -> dict[str, Any]:
        """Stats del padrón completo: total, por entidad, por rubro."""
        cache_key = f"stats_padron_{'mock' if self._is_mock() else 'real'}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("estadisticas_padron", {})

        if self._is_mock():
            resultado = mark_simulated({
                "total_donatarias": 10247,
                "anio_anexo_14": 2026,
                "por_entidad_top10": {
                    "CDMX": 3245, "JAL": 1024, "NL": 856, "EDOMEX": 743,
                    "PUE": 421, "GTO": 312, "MICH": 287, "VER": 265,
                    "QRO": 234, "BC": 201,
                },
                "por_rubro": {k: 600 + i * 100 for i, k in enumerate(RUBROS_DONATARIA)},
                "url_consultado": URL_DIRECTORIO_SAT,
            })
        else:
            resultado = self._stats_real()

        self._cache.set(cache_key, resultado, ttl_days=CACHE_DIRECTORIO_DIAS)
        return resultado

    def listar_rubros(self) -> dict[str, Any]:
        """Catálogo de rubros de actividad reconocidos por SAT."""
        return {
            "rubros": RUBROS_DONATARIA,
            "total": len(RUBROS_DONATARIA),
            "base_legal": "Art. 79 LISR, fracciones VI, X, XI, XII, XVII, XIX, XX, XXV",
        }

    # ============================================================
    # Mocks
    # ============================================================

    def _mock_donataria(self, rfc: str) -> dict[str, Any]:
        """Mock determinístico: RFCs que empiezan con 'X' o 'Z' = no autorizadas."""
        autorizada = rfc[0] not in ("X", "Z")
        if not autorizada:
            return mark_simulated({
                "rfc": rfc,
                "autorizada": False,
                "razon_social": None,
                "puede_emitir_recibo_deducible": False,
                "advertencias": [
                    "RFC no aparece en padrón de donatarias autorizadas SAT. "
                    "No puede emitir CFDI con uso D04 (Donativos)."
                ],
                "url_consultado": URL_DIRECTORIO_SAT,
            })

        return mark_simulated({
            "rfc": rfc,
            "autorizada": True,
            "razon_social": f"FUNDACION MOCK {rfc[:6]} AC",
            "entidad": "CDMX",
            "rubro": "asistencia_social",
            "rubro_descripcion": RUBROS_DONATARIA["asistencia_social"],
            "fecha_autorizacion": "2024-01-15",
            "vigencia_anexo_14": "2026",
            "puede_emitir_recibo_deducible": True,
            "advertencias": [],
            "url_consultado": URL_DIRECTORIO_SAT,
        })

    def _mock_busqueda(
        self, razon_norm: str, entidad: Optional[str], limite: int,
    ) -> dict[str, Any]:
        # Mock: 3-5 resultados sintéticos
        n = min(limite, 5)
        return mark_simulated({
            "razon_social_buscada": razon_norm,
            "entidad_filtro": entidad,
            "total_encontrados": n,
            "donatarias": [
                {
                    "rfc": f"FUN{i:03d}010101AB{i:01d}"[:12],
                    "razon_social": f"FUNDACION {razon_norm.upper()} {i}",
                    "entidad": entidad or "CDMX",
                    "rubro": "asistencia_social",
                    "autorizada": True,
                }
                for i in range(1, n + 1)
            ],
            "url_consultado": URL_DIRECTORIO_SAT,
        })

    # ============================================================
    # Path real — Directorio de Donatarias Autorizadas (XLSX SAT)
    # ============================================================

    def _directorio(self) -> dict[str, Any]:
        """{"publicacion", "url_xlsx", "donatarias": {rfc: registro}} (cache 7 días)."""
        cached = self._cache.get("directorio_v1")
        if cached is not None:
            return cached
        import httpx

        headers = {"User-Agent": "Mozilla/5.0 (plugins-mx mp_donatarias_sat)"}
        try:
            with httpx.Client(timeout=120, follow_redirects=True, headers=headers) as c:
                pagina = c.get(URL_DIRECTORIO_SAT)
                pagina.raise_for_status()
                m = _RE_XLSX_DIRECTORIO.search(pagina.text)
                if not m:
                    raise UpstreamError(
                        "La página del directorio SAT ya no enlaza un Dir_<año>.xlsx — revisar fuente.",
                        {"url": URL_DIRECTORIO_SAT},
                    )
                url_xlsx = str(pagina.url.join(m.group(1)))
                xlsx = c.get(url_xlsx)
                xlsx.raise_for_status()
        except httpx.HTTPError as exc:
            raise UpstreamError(
                f"No se pudo descargar el directorio de donatarias del SAT: {type(exc).__name__}",
                {"url": URL_DIRECTORIO_SAT},
            ) from exc
        directorio = parsear_directorio_xlsx(xlsx.content)
        directorio["url_xlsx"] = url_xlsx
        self._cache.set("directorio_v1", directorio, ttl_days=CACHE_DIRECTORIO_DIAS)
        return directorio

    def _real_base(self, directorio: dict[str, Any]) -> dict[str, Any]:
        return {
            "publicacion": directorio.get("publicacion"),
            "url_consultado": directorio.get("url_xlsx", URL_DIRECTORIO_SAT),
            "simulated": False,
        }

    def _consultar_real(self, rfc: str) -> dict[str, Any]:
        d = self._directorio()
        reg = d["donatarias"].get(rfc)
        base = self._real_base(d)
        if reg is None:
            return {
                **base,
                "rfc": rfc,
                "autorizada": False,
                "razon_social": None,
                "puede_emitir_recibo_deducible": False,
                "advertencias": [
                    "RFC no aparece en el Directorio de Donatarias Autorizadas del SAT. "
                    "Revisar también los listados de revocadas/pendientes de publicar en "
                    f"{URL_DIRECTORIO_SAT}.",
                ],
            }
        advertencias = []
        if (reg.get("estado_rfc") or "").lower() not in ("activo", "reactivado"):
            advertencias.append(f"Estado del contribuyente en el RFC: {reg.get('estado_rfc')}.")
        if (reg.get("estado_localizacion") or "").lower() == "no localizado":
            advertencias.append("Domicilio fiscal NO LOCALIZADO según el SAT.")
        return {
            **base,
            **reg,
            "autorizada": True,
            "rubro": reg["rubros"][0] if reg["rubros"] else None,
            "rubro_descripcion": RUBROS_DONATARIA.get(reg["rubros"][0]) if reg["rubros"] else None,
            "puede_emitir_recibo_deducible": True,
            "advertencias": advertencias,
        }

    def _buscar_real(self, razon_norm: str, entidad: Optional[str], limite: int) -> dict[str, Any]:
        d = self._directorio()
        ent = entidad.upper() if entidad else None
        hits = [
            r for r in d["donatarias"].values()
            if razon_norm in _normalizar(r["razon_social"]) and (ent is None or r["entidad"] == ent)
        ]
        return {
            **self._real_base(d),
            "razon_social_buscada": razon_norm,
            "entidad_filtro": entidad,
            "total_encontrados": len(hits),
            "donatarias": [{**r, "autorizada": True} for r in hits[:limite]],
        }

    def _listar_real(self, entidad: str, limite: int = 200) -> dict[str, Any]:
        d = self._directorio()
        hits = [r for r in d["donatarias"].values() if r["entidad"] == entidad]
        return {
            **self._real_base(d),
            "entidad": entidad,
            "total": len(hits),
            "donatarias": hits[:limite],
            "truncado_a": limite if len(hits) > limite else None,
        }

    def _stats_real(self) -> dict[str, Any]:
        from collections import Counter

        d = self._directorio()
        regs = list(d["donatarias"].values())
        por_entidad = Counter(r["entidad"] for r in regs)
        por_rubro = Counter(k for r in regs for k in set(r["rubros"]))
        return {
            **self._real_base(d),
            "total_donatarias": len(regs),
            "por_entidad_top10": dict(por_entidad.most_common(10)),
            "por_rubro": dict(por_rubro),
        }


# ============================================================
# Parser XLSX (stdlib)
# ============================================================


def _leer_xlsx(contenido: bytes) -> list[dict[str, str]]:
    """Filas de la primera hoja como {columna: valor}. Solo stdlib."""
    import io
    import zipfile
    import xml.etree.ElementTree as ET

    z = zipfile.ZipFile(io.BytesIO(contenido))
    compartidas: list[str] = []
    if "xl/sharedStrings.xml" in z.namelist():
        raiz = ET.parse(z.open("xl/sharedStrings.xml")).getroot()
        compartidas = ["".join(t.text or "" for t in si.iter(_NS_XLSX + "t")) for si in raiz.iter(_NS_XLSX + "si")]
    filas = []
    for _, el in ET.iterparse(z.open("xl/worksheets/sheet1.xml")):
        if el.tag != _NS_XLSX + "row":
            continue
        fila = {}
        for celda in el.iter(_NS_XLSX + "c"):
            v = celda.find(_NS_XLSX + "v")
            if v is None or v.text is None:
                continue
            col = re.sub(r"\d", "", celda.get("r", ""))
            fila[col] = compartidas[int(v.text)] if celda.get("t") == "s" else v.text
        filas.append(fila)
        el.clear()
    return filas


def _fecha_excel(serial: str | None) -> str | None:
    from datetime import date, timedelta

    try:
        return (date(1899, 12, 30) + timedelta(days=int(float(serial)))).isoformat()
    except (TypeError, ValueError):
        return None


def parsear_directorio_xlsx(contenido: bytes) -> dict[str, Any]:
    """Parsea el Directorio de Donatarias Autorizadas del SAT.

    Una fila por (RFC, actividad autorizada); se agrupa por RFC. Columnas
    (encabezado validado en Dir_2026.xlsx): A entidad, B ADSC, C actividad
    (letra A-M), D RFC, E razón social, F domicilio, G oficio, H fecha oficio
    (serial Excel), N estado de localización, O estado en el RFC.
    """
    filas = _leer_xlsx(contenido)
    try:
        idx = next(i for i, f in enumerate(filas) if (f.get("D") or "").strip().upper() == "RFC")
    except StopIteration:
        raise UpstreamError("El XLSX del directorio no tiene la columna RFC esperada — formato cambió.")
    publicacion = next(
        (f["A"] for f in filas[:idx] if "ANEXO 14" in (f.get("A") or "").upper()), None
    )
    donatarias: dict[str, dict[str, Any]] = {}
    for f in filas[idx + 1:]:
        rfc = (f.get("D") or "").strip().upper()
        if not rfc:
            continue
        reg = donatarias.get(rfc)
        if reg is None:
            nombre_ent = (f.get("A") or "").strip()
            reg = donatarias[rfc] = {
                "rfc": rfc,
                "razon_social": (f.get("E") or "").strip(),
                "entidad": ENTIDAD_POR_NOMBRE.get(_normalizar(nombre_ent)),
                "entidad_nombre": nombre_ent,
                "administracion_desconcentrada": f.get("B"),
                "domicilio_fiscal": f.get("F"),
                "oficio_autorizacion": f.get("G"),
                "fecha_autorizacion": _fecha_excel(f.get("H")),
                "actividades": [],
                "rubros": [],
                "estado_localizacion": f.get("N"),
                "estado_rfc": f.get("O"),
            }
        letra = (f.get("C") or "").strip().upper()
        if letra and letra not in reg["actividades"]:
            reg["actividades"].append(letra)
            rubro = RUBRO_POR_LETRA.get(letra)
            if rubro and rubro not in reg["rubros"]:
                reg["rubros"].append(rubro)
    return {"publicacion": publicacion, "donatarias": donatarias}
