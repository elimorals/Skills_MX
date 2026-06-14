"""Cliente mp_donatarias_sat — Padrón donatarias autorizadas SAT.

Tools:
1. **consultar_donataria(rfc)** — Verifica si un RFC está autorizado como donataria
2. **buscar_donatarias(razon_social, [entidad])** — Búsqueda fuzzy por nombre
3. **listar_por_entidad(entidad)** — Lista donatarias de un estado
4. **estadisticas_padron()** — Stats del padrón completo

Cache 30 días — el padrón se actualiza anualmente (Anexo 14 RMF) + boletines mensuales DOF.

Modo mock por default. Real: setear MP_DONATARIAS_SAT_REAL=1 con cache local del Excel
descargado (path real requiere descarga del XLSX que está detrás de Akamai Bot Manager).
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
from shared.errors import McpError, NotFoundError, ValidationError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402


NAMESPACE = "donatarias_sat"

# RFC: PM 12 chars, PF 13 chars
RFC_REGEX = re.compile(r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$")

URL_DIRECTORIO_SAT = (
    "https://www.sat.gob.mx/consultas/27717/conoce-el-directorio-de-donatarias-autorizadas"
)
URL_EXCEL_BASE = "https://omawww.sat.gob.mx/cifras_sat/Documents/"

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
        return is_mock_mode(credential_env_vars=[])

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

        cache_key = f"donataria_{rfc_norm}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("consultar_donataria", {"rfc": rfc_norm})

        if self._is_mock():
            resultado = self._mock_donataria(rfc_norm)
        else:
            resultado = self._consultar_real(rfc_norm)

        self._cache.set(cache_key, resultado, ttl_days=30)
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
        cache_key = "stats_padron"
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

        self._cache.set(cache_key, resultado, ttl_days=30)
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
    # Path real (TODO: implementar parser XLSX)
    # ============================================================

    def _consultar_real(self, rfc: str) -> dict[str, Any]:
        raise McpError(
            "Path real requiere descarga del Excel del padrón (Akamai bloquea bots). "
            "Recomendación: descargar manualmente XLSX y montar como cache local. "
            f"Anexo 14 RMF: {URL_DIRECTORIO_SAT}",
            {"hint": "implementar pipeline XLSX → SQLite local"},
        )

    def _buscar_real(self, razon_norm, entidad, limite):
        raise McpError("Path real pendiente — usar mock o cache local.")

    def _listar_real(self, entidad):
        raise McpError("Path real pendiente — usar mock o cache local.")

    def _stats_real(self):
        raise McpError("Path real pendiente — usar mock o cache local.")
