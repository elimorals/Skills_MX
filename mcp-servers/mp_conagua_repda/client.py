"""Cliente mp_conagua_repda — REPDA (consulta pública real) + derecho sobre agua LFD.

Consulta real: formulario ASP.NET público de CONAGUA
https://app.conagua.gob.mx/consultarepda.aspx (sin CAPTCHA, sin login). Se hace
GET para obtener __VIEWSTATE y POST con el titular o el número de título;
los resultados vienen en la tabla `ContentPlaceHolder1_GVRepda` (100 por página).

Cuotas: Ley Federal de Derechos, Art. 223 apartado A, "Cantidades actualizadas por
Resolución Miscelánea Fiscal DOF 28-12-2025" (texto vigente en
https://www.diputados.gob.mx/LeyesBiblio/pdf/LFD.pdf, última reforma DOF 07-11-2025,
consultado 2026-10-14).

Mock solo con PLUGINS_MX_MOCK=1. Si CONAGUA falla → UpstreamError.
"""
from __future__ import annotations

import html as html_lib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import UpstreamError, ValidationError, handle_httpx_error  # noqa: E402
from shared.http_helpers import build_ssl_verify  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402
from shared.portal_handoff import armar_handoff  # noqa: E402


NAMESPACE = "conagua_repda"
URL_REPDA = "https://www.gob.mx/conagua/acciones-y-programas/registro-publico-de-derechos-de-agua-repda"
URL_CONSULTA_REPDA = "https://app.conagua.gob.mx/consultarepda.aspx"
URL_LFD = "https://www.diputados.gob.mx/LeyesBiblio/pdf/LFD.pdf"

BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
)
_SIN_SELECCION = "Selecciona una opción"

Fuente = Literal["superficial", "subterranea"]

# LFD Art. 223 apartado A — cuota por m³, cantidades RMF 2026 (DOF 28-12-2025).
# Desde la reforma 2020 hay 4 zonas de disponibilidad (Art. 231), no 9.
CUOTA_LFD_2026_POR_M3: dict[int, dict[str, float]] = {
    1: {"superficial": 23.6460, "subterranea": 31.8622},
    2: {"superficial": 10.8860, "subterranea": 12.3333},
    3: {"superficial": 3.5694, "subterranea": 4.2944},
    4: {"superficial": 2.7295, "subterranea": 3.1215},
}

# Formatos vistos en el REPDA real: "11CHS158257/30EMDA26" y numéricos "874717".
NUM_TITULO_RE = re.compile(r"^\d{2}[A-Z]{3}\d{6}/\d{2}[A-Z]{4}\d{2}$|^\d{5,12}$")
RFC_RE = re.compile(r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$")

_COLUMNAS = [
    "titular", "num_titulo", "uso", "autoridad", "fecha_registro",
    "volumen_extraccion_m3_anual", "anexos_superficiales", "volumen_superficial_m3_anual",
    "anexos_subterraneos", "volumen_subterraneo_m3_anual", "anexos_descarga",
    "volumen_descarga_m3_dia", "anexos_zonas_federales", "superficie_zona_federal_m2",
]
_NUMERICAS = {c for c in _COLUMNAS if c.startswith(("volumen", "anexos", "superficie"))}


def _texto(celda: str) -> str:
    return " ".join(html_lib.unescape(re.sub(r"<[^>]+>", " ", celda)).split())


def _numero(s: str) -> float | int | None:
    s = s.replace(",", "").strip()
    if not s:
        return None
    try:
        return int(s) if re.fullmatch(r"-?\d+", s) else float(s)
    except ValueError:
        return None


def parse_resultados(page: str) -> dict[str, Any]:
    """Extrae total y filas de la tabla GVRepda. Lanza UpstreamError si no la reconoce."""
    m_total = re.search(r'LblConteo"><strong>Total de Registros</strong>:\s*([\d,]+)', page)
    if not m_total:
        raise UpstreamError(
            "La respuesta de CONAGUA no trae el conteo de REPDA; el formulario pudo cambiar.",
            {"url": URL_CONSULTA_REPDA},
        )
    total = int(m_total.group(1).replace(",", ""))
    filas: list[dict[str, Any]] = []
    m_tabla = re.search(r'id="ContentPlaceHolder1_GVRepda".*?</table>', page, re.S)
    if m_tabla:
        for tr in re.findall(r"<tr>(.*?)</tr>", m_tabla.group(0), re.S):
            celdas = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
            if len(celdas) != len(_COLUMNAS):
                continue  # encabezado o paginador
            fila = {}
            for col, raw in zip(_COLUMNAS, celdas):
                val = _texto(raw)
                fila[col] = _numero(val) if col in _NUMERICAS else (val or None)
            filas.append(fila)
    return {"total_registros": total, "registros": filas}


class CONAGUARepdaClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    # ── consulta real ──────────────────────────────────────────────────────
    def _buscar(self, titular: str = "", num_titulo: str = "") -> dict[str, Any]:
        try:
            with httpx.Client(
                verify=build_ssl_verify(),
                timeout=60.0,
                follow_redirects=True,
                headers={"User-Agent": BROWSER_UA, "Accept-Language": "es-MX,es;q=0.9"},
            ) as client:
                r = client.get(URL_CONSULTA_REPDA)
                r.raise_for_status()
                data = {
                    k: html_lib.unescape(v)
                    for k, v in re.findall(
                        r'<input type="hidden" name="([^"]+)" id="[^"]*" value="([^"]*)"', r.text
                    )
                }
                if "__VIEWSTATE" not in data:
                    raise UpstreamError(
                        "El formulario REPDA no trae __VIEWSTATE; el portal pudo cambiar.",
                        {"url": URL_CONSULTA_REPDA},
                    )
                data.update({
                    "ctl00$ContentPlaceHolder1$RB": "1",  # búsqueda básica
                    "ctl00$ContentPlaceHolder1$txtTitular": titular,
                    "ctl00$ContentPlaceHolder1$txtTitulo": num_titulo,
                    "ctl00$ContentPlaceHolder1$CboEstado": _SIN_SELECCION,
                    "ctl00$ContentPlaceHolder1$CboMunicipio": _SIN_SELECCION,
                    "ctl00$ContentPlaceHolder1$CboUsoB": _SIN_SELECCION,
                    "ctl00$ContentPlaceHolder1$BtnBuscar": "Consultar",
                })
                r2 = client.post(URL_CONSULTA_REPDA, data=data)
                r2.raise_for_status()
        except httpx.HTTPError as e:
            raise handle_httpx_error(e) from e
        return parse_resultados(r2.text)

    def consultar_titular(self, identificador: str) -> dict[str, Any]:
        """Busca en el REPDA por nombre del titular (parcial) o número de título completo."""
        identificador = (identificador or "").strip()
        if len(identificador) < 5:
            raise ValidationError(f"identificador inválido: {identificador!r}")
        es_titulo = bool(NUM_TITULO_RE.match(identificador.upper()))
        if not es_titulo and RFC_RE.match(identificador.upper()):
            raise ValidationError(
                "La consulta pública REPDA no busca por RFC: usa el nombre del titular "
                "o el número de título completo."
            )

        if is_mock_mode([], default_when_no_creds=False):
            return self._mock_titular(identificador)

        res = (self._buscar(num_titulo=identificador.upper()) if es_titulo
               else self._buscar(titular=identificador))
        self._bitacora.log("consultar_titular", success=True,
                           params_summary={"id_hash": self._bitacora.hash_sensitive(identificador)})
        return {
            "identificador": identificador,
            "buscado_por": "num_titulo" if es_titulo else "titular",
            **res,
            "registros_en_pagina": len(res["registros"]),
            "nota": "El portal pagina de 100 en 100; se devuelve la primera página.",
            "fuente": URL_CONSULTA_REPDA,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "simulated": False,
        }

    def consultar_vigencia(self, num_titulo: str) -> dict[str, Any]:
        """¿El título está inscrito en el REPDA? La consulta pública no publica la vigencia."""
        if not NUM_TITULO_RE.match((num_titulo or "").upper()):
            raise ValidationError(f"num_titulo inválido: {num_titulo!r}")
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"num_titulo": num_titulo, "inscrito_repda": True})
        res = self._buscar(num_titulo=num_titulo.upper())
        registro = res["registros"][0] if res["registros"] else None
        return {
            "num_titulo": num_titulo,
            "inscrito_repda": registro is not None,
            "registro": registro,
            "vigencia_publicada": False,
            "nota": ("La consulta pública REPDA no expone la fecha de vencimiento del título; "
                     "consúltala en el propio título o en el Organismo de Cuenca."),
            "fuente": URL_CONSULTA_REPDA,
            "simulated": False,
        }

    # ── obligaciones / cálculos locales con base legal verificada ──────────
    def estado_reporte_semestral(self, num_titulo: str, periodo: str) -> dict[str, Any]:
        """Calendario de la declaración trimestral (Art. 226 LFD). No hay consulta pública
        de si se presentó: se devuelve handoff humano."""
        if not NUM_TITULO_RE.match((num_titulo or "").upper()):
            raise ValidationError(f"num_titulo inválido: {num_titulo!r}")
        vencimientos = {
            "T1": "último día hábil de abril",
            "T2": "último día hábil de julio",
            "T3": "último día hábil de octubre",
            "T4": "último día hábil de enero del año siguiente",
        }
        if periodo not in vencimientos:
            raise ValidationError("periodo debe ser T1, T2, T3 o T4 (la declaración es trimestral)")
        return armar_handoff(
            motivo="sin_consulta_publica",
            detalle="No existe consulta pública del cumplimiento; revisar acuses del contribuyente.",
            pasos=[
                "Revisar el acuse de la declaración trimestral del derecho sobre agua (SAT / e5cinco).",
                "Si no se presentó, declarar y pagar con actualización y recargos.",
            ],
            num_titulo=num_titulo,
            periodo=periodo,
            fecha_limite=vencimientos[periodo],
            presentado=None,
            base_legal="Art. 226 LFD: cálculo trimestral, pago a más tardar el último día hábil "
                       "de enero, abril, julio y octubre.",
            fuente=URL_LFD,
        )

    def calcular_pago_lfd(self, num_titulo: str, m3_extraidos: float,
                          zona_disponibilidad: int,
                          fuente: Fuente = "subterranea") -> dict[str, Any]:
        """Derecho sobre agua, régimen general (Art. 223 apartado A LFD, cuotas 2026)."""
        if not NUM_TITULO_RE.match((num_titulo or "").upper()):
            raise ValidationError(f"num_titulo inválido: {num_titulo!r}")
        if m3_extraidos < 0:
            raise ValidationError("m3 negativos")
        if zona_disponibilidad not in CUOTA_LFD_2026_POR_M3:
            raise ValidationError("zona_disponibilidad debe ser 1-4 (Art. 231 LFD)")
        if fuente not in ("superficial", "subterranea"):
            raise ValidationError("fuente debe ser 'superficial' o 'subterranea'")

        cuota_m3 = CUOTA_LFD_2026_POR_M3[zona_disponibilidad][fuente]
        return {
            "num_titulo": num_titulo,
            "m3_extraidos": m3_extraidos,
            "zona_disponibilidad": zona_disponibilidad,
            "fuente_agua": fuente,
            "cuota_m3_mxn": cuota_m3,
            "derecho_mxn": round(m3_extraidos * cuota_m3, 2),
            "alcance": ("Régimen general (apartado A). No aplica a uso agua potable "
                        "(apartado B, cuota por millar), hidroeléctrico, ni exenciones del Art. 224."),
            "base_legal": "Art. 223 apartado A LFD; cantidades RMF 2026 (DOF 28-12-2025)",
            "fuente": URL_LFD,
        }

    def requiere_medidor(self, volumen_anual_m3: float, tipo_uso: str | None = None) -> dict[str, Any]:
        """Art. 225 LFD: todo contribuyente del derecho sobre agua debe medir; no hay umbral."""
        if volumen_anual_m3 < 0:
            raise ValidationError("volumen negativo")
        indirecto = (tipo_uso or "").lower() in {"agricola", "agropecuario", "pecuario"}
        return {
            "volumen_anual_m3": volumen_anual_m3,
            "tipo_uso": tipo_uso,
            "requiere_medidor_obligatorio": True,
            "puede_usar_metodo_indirecto": indirecto,
            "nota": ("Uso agrícola/pecuario puede determinar volumen por métodos indirectos "
                     "(Art. 225 fr. III) mientras CONAGUA no instale medidor."
                     if indirecto else
                     "Debe instalar/conservar medidor conforme a reglas de CONAGUA (Art. 225 fr. I)."),
            "base_legal": "Art. 225 LFD (reforma DOF 19-12-2024)",
            "fuente": URL_LFD,
        }

    def listar_tipos_uso(self) -> dict[str, Any]:
        """Usos del catálogo de búsqueda avanzada del REPDA (consultado 2026-10-14)."""
        return {
            "tipos_uso": [
                "agricola", "agroindustrial", "domestico", "acuacultura", "servicios",
                "industrial", "pecuario", "publico_urbano", "diferentes_usos",
                "generacion_energia_electrica", "comercio", "otros", "conservacion_ecologica",
                "generacion_energia_servicio_publico", "generacion_energia_servicio_privado",
                "lavado_entarcamiento_terrenos", "turismo_recreacion_fines_terapeuticos",
            ],
            "fuente": URL_CONSULTA_REPDA,
        }

    # ── mock (solo PLUGINS_MX_MOCK=1) ──────────────────────────────────────
    def _mock_titular(self, identificador: str) -> dict[str, Any]:
        n = max(1, sum(ord(c) for c in identificador) % 4)
        return mark_simulated({
            "identificador": identificador,
            "total_registros": n,
            "registros": [
                {"titular": identificador.upper(), "num_titulo": f"02SON{100000 + i:06d}/{20 + i:02d}HSGS{i:02d}",
                 "uso": ["INDUSTRIAL", "AGRICOLA", "SERVICIOS"][i % 3],
                 "volumen_extraccion_m3_anual": 50_000 + i * 75_000}
                for i in range(n)
            ],
            "fuente": URL_CONSULTA_REPDA,
        })
