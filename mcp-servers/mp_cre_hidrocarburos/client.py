"""Cliente mp_cre_hidrocarburos — permisos de expendio (real) + controles volumétricos.

Contexto 2025-2026: la CRE se extinguió y sus atribuciones pasaron a la Comisión
Nacional de Energía (CNE). Los permisos nuevos ya se emiten como `CNE/PL/...`.

Consulta real: el padrón público de estaciones de servicio que la CRE/CNE publica
para el programa de precios de combustibles,
https://publicacionexterna.azurewebsites.net/publicaciones/places (XML, ~15k
estaciones con nombre, permiso `cre_id` y coordenadas). Solo cubre **expendio al
público en estaciones de servicio** (ES/ESA); otros permisos (transporte,
almacenamiento, comercialización) no tienen consulta pública equivalente → handoff.

Mock solo con PLUGINS_MX_MOCK=1. Upstream caído → UpstreamError.
"""
from __future__ import annotations

import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import UpstreamError, ValidationError, handle_httpx_error  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402
from shared.portal_handoff import armar_handoff  # noqa: E402


NAMESPACE = "cre_hidrocarburos"
URL_PLACES = "https://publicacionexterna.azurewebsites.net/publicaciones/places"
URL_CNE = "https://www.gob.mx/cne"
URL_SAT_VOLUMETRICOS = "https://www.sat.gob.mx/minisitio/ControlesVolumetricos/index.html"

# Regla 2.6.1.2 RMF (en relación con el Art. 28 fr. I apartado B CFF): sujetos sin
# permiso obligados a controles volumétricos si consumen ≥ 75,714 L de petrolíferos
# en al menos un mes, o > 5,000 GJ/año de gas natural. Cifras tal como las resume
# PwC México, "Controles volumétricos" (25-nov-2025). El texto de la regla en la
# RMF 2026 (DOF 28-12-2025) no se pudo descargar del SAT para cotejarlo (2026-10-14).
UMBRAL_PETROLIFEROS_LITROS_MES = 75_714.0
UMBRAL_GAS_NATURAL_GJ_ANIO = 5_000.0

TIPOS_PERMISO = {
    "comercializacion_petroliferos": "Comercialización de petrolíferos (gasolina, diésel)",
    "comercializacion_gas_lp": "Comercialización de gas LP",
    "comercializacion_gas_natural": "Comercialización de gas natural",
    "expendio_publico": "Expendio al público (gasolinera)",
    "transporte": "Transporte por ducto/auto-tanque",
    "almacenamiento": "Almacenamiento",
}

NUM_PERMISO_RE = re.compile(r"^(CNE/)?[A-Z]{1,3}/\d{1,6}/[A-Z/]+/\d{4}$")


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return " ".join(s.upper().split())


def parse_places(xml_text: str) -> list[dict[str, Any]]:
    try:
        root = ET.fromstring(xml_text.lstrip("﻿"))
    except ET.ParseError as e:
        raise UpstreamError("XML de estaciones CRE/CNE ilegible", {"raw": str(e)}) from e
    out = []
    for p in root.iter("place"):
        loc = p.find("location")
        out.append({
            "place_id": p.get("place_id"),
            "nombre": (p.findtext("name") or "").strip(),
            "permiso": (p.findtext("cre_id") or "").strip(),
            "lon": float(loc.findtext("x")) if loc is not None and loc.findtext("x") else None,
            "lat": float(loc.findtext("y")) if loc is not None and loc.findtext("y") else None,
        })
    if not out:
        raise UpstreamError("El padrón de estaciones vino vacío", {"url": URL_PLACES})
    return out


class CREClient:
    def __init__(self, bitacora: Bitacora | None = None, cache: FileCache | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)
        self._cache = cache or FileCache(NAMESPACE)

    def _estaciones(self) -> list[dict[str, Any]]:
        cached = self._cache.get("places")
        if cached is not None:
            return cached
        try:
            r = httpx.get(URL_PLACES, timeout=60.0, follow_redirects=True)
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise handle_httpx_error(e) from e
        estaciones = parse_places(r.content.decode("utf-8-sig"))
        self._cache.set("places", estaciones, ttl_hours=24)
        return estaciones

    def consultar_permiso(self, identificador: str) -> dict[str, Any]:
        """Busca estaciones por número de permiso exacto o por razón social (parcial)."""
        ident = (identificador or "").strip()
        if len(ident) < 4:
            raise ValidationError(f"identificador inválido: {identificador!r}")

        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"identificador": ident, "encontrado": True,
                                   "estaciones": [{"nombre": "ESTACION DEMO SA DE CV",
                                                   "permiso": "PL/0000/EXP/ES/2015"}]})

        estaciones = self._estaciones()
        q = _norm(ident)
        por_permiso = bool(NUM_PERMISO_RE.match(ident.upper()))
        if por_permiso:
            hits = [e for e in estaciones if e["permiso"].upper() == ident.upper()]
        else:
            hits = [e for e in estaciones if q in _norm(e["nombre"])]
        self._bitacora.log("consultar_permiso", success=True,
                           params_summary={"por_permiso": por_permiso, "hits": len(hits)})
        out: dict[str, Any] = {
            "identificador": ident,
            "buscado_por": "permiso" if por_permiso else "razon_social",
            "encontrado": bool(hits),
            "total": len(hits),
            "estaciones": hits[:50],
            "alcance": "Solo expendio al público en estaciones de servicio (padrón de precios CRE/CNE).",
            "fuente": URL_PLACES,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "simulated": False,
        }
        if not hits:
            out["nota"] = ("No aparece en el padrón de estaciones. Eso NO prueba que el permiso no "
                           "exista o no esté vigente: otros tipos de permiso no se publican aquí. "
                           "Confirmar con la CNE.")
            out["handoff"] = armar_handoff(motivo="sin_consulta_publica", url=URL_CNE,
                                           pasos=["Solicitar constancia/estatus del permiso a la CNE."])
        return out

    def calendar_reporte_mensual(self, anio: int, mes_actual: int) -> dict[str, Any]:
        """Periodos mensuales a reportar. Las fechas límite dependen del título de permiso
        y de las disposiciones de la CNE: no se inventan aquí."""
        if anio < 2020 or anio > 2099:
            raise ValidationError("anio fuera de rango")
        if mes_actual < 1 or mes_actual > 12:
            raise ValidationError("mes_actual debe ser 1-12")
        periodos = []
        a, m = anio, mes_actual
        for _ in range(12):
            periodos.append({"periodo": f"{a}-{m:02d}",
                             "obligacion": "Reporte mensual de volúmenes/precios al regulador "
                                           "(ceros si no hubo actividad)"})
            a, m = (a + 1, 1) if m == 12 else (a, m + 1)
        return {
            "anio_inicio": anio,
            "mes_inicio": mes_actual,
            "periodos": periodos,
            "fecha_limite": None,
            "nota": ("La fecha límite la fija el título de permiso / disposiciones administrativas "
                     "de la CNE (antes CRE); revisarla ahí. Sin actividad se reportan ceros."),
            "fuente": URL_CNE,
        }

    def evaluar_anexo30(self, litros_mes_max: float, tiene_permiso_cre: bool,
                        gas_natural_gj_anio: float = 0.0) -> dict[str, Any]:
        """¿Obligado a controles volumétricos (Art. 28 fr. I-B CFF, regla 2.6.1.2 RMF)?"""
        if litros_mes_max < 0 or gas_natural_gj_anio < 0:
            raise ValidationError("volúmenes negativos")
        por_litros = litros_mes_max >= UMBRAL_PETROLIFEROS_LITROS_MES
        por_gas = gas_natural_gj_anio > UMBRAL_GAS_NATURAL_GJ_ANIO
        motivos = []
        if tiene_permiso_cre:
            motivos.append("Tiene permiso CNE/CRE o de importación SENER")
        if por_litros:
            motivos.append(f"Consumo ≥ {UMBRAL_PETROLIFEROS_LITROS_MES:,.0f} L de petrolíferos en un mes")
        if por_gas:
            motivos.append(f"Gas natural para autoconsumo > {UMBRAL_GAS_NATURAL_GJ_ANIO:,.0f} GJ/año")
        return {
            "litros_mes_max_consumo": litros_mes_max,
            "gas_natural_gj_anio": gas_natural_gj_anio,
            "umbral_litros_mes": UMBRAL_PETROLIFEROS_LITROS_MES,
            "umbral_gas_natural_gj_anio": UMBRAL_GAS_NATURAL_GJ_ANIO,
            "tiene_permiso_cre": tiene_permiso_cre,
            "aplica_anexo30_sat": bool(motivos),
            "motivos": motivos,
            "obligaciones_si_aplica": [
                "Controles volumétricos conforme a Anexo 30 RMF",
                "Certificación de correcto funcionamiento (Anexo 31)",
                "Dictámenes de tipo y calidad del producto (Anexo 32)",
                "Reportes de controles volumétricos al SAT",
            ],
            "base_legal": "Art. 28 fr. I apartado B CFF; regla 2.6.1.2 RMF; Anexos 30-32 RMF",
            "verificacion": ("Umbrales según resumen PwC México 25-nov-2025; texto RMF 2026 "
                             "no cotejado directamente."),
            "fuente": URL_SAT_VOLUMETRICOS,
        }

    def reportar_zeros(self, num_permiso: str, periodo: str) -> dict[str, Any]:
        """Nunca envía nada: devuelve los pasos para que una persona presente el reporte."""
        if not NUM_PERMISO_RE.match((num_permiso or "").upper()):
            raise ValidationError(f"num_permiso inválido: {num_permiso!r}")
        if not re.match(r"^\d{4}-\d{2}$", periodo):
            raise ValidationError(f"periodo debe ser YYYY-MM: {periodo!r}")
        return armar_handoff(
            motivo="accion_del_titular",
            detalle="Presentar reportes ante el regulador es una acción con efectos legales; "
                    "este MCP es de solo lectura.",
            pasos=[
                "Entrar a la Oficialía de Partes Electrónica / sistema de reportes de la CNE con la e.firma del permisionario.",
                f"Seleccionar el permiso {num_permiso} y el periodo {periodo}.",
                "Capturar volúmenes en cero y firmar; conservar el acuse.",
            ],
            url=URL_CNE,
            num_permiso=num_permiso,
            periodo=periodo,
            enviado=False,
        )

    def listar_tipos_permiso(self) -> dict[str, Any]:
        return {
            "total": len(TIPOS_PERMISO),
            "tipos": [{"clave": k, "descripcion": v} for k, v in TIPOS_PERMISO.items()],
        }
