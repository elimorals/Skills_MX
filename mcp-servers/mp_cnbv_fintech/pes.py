"""Padrón de Entidades Supervisadas (PES) de la CNBV — https://pes.cnbv.gob.mx/

Formulario GET (verificado 2026-10-14):
    GET /Consulta/ConsultaEntidad?entidad=<razón social>&nombreCorto=<n>&subsectorName=<SECTOR|NULL>
Respuesta HTML (grid DevExpress, sin paginación): filas
`GridViewEntidad_DXDataRowN` con CASFIM, razón social, nombre corto, sector y
link `/DetalleEntidad?q=...`. El PES **no publica RFC**.
"""

from __future__ import annotations

import html
import re
from typing import Any

import httpx

from shared.errors import UpstreamError, handle_httpx_error
from shared.http_helpers import build_ssl_verify, default_user_agent

BASE = "https://pes.cnbv.gob.mx"
SECTOR_IFPE = "INSTITUCIONES DE FONDOS DE PAGO ELECTRÓNICO"
SECTOR_IFC = "INSTITUCIONES DE FINANCIAMIENTO COLECTIVO"
SECTOR_A_TIPO = {SECTOR_IFPE: "ifpe", SECTOR_IFC: "ifc"}

_ROW = re.compile(r'<tr id="GridViewEntidad_DXDataRow\d+".*?</tr>', re.S)
_TD = re.compile(r"<td[^>]*>(.*?)</td>", re.S)
_HREF = re.compile(r'href="(/DetalleEntidad\?q=[^"&]+)')


def _limpio(fragmento: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragmento))).strip()


def parsear(html_text: str) -> list[dict[str, Any]]:
    if "GridViewEntidad" not in html_text:
        raise UpstreamError("PES no devolvió el grid de entidades; el portal cambió.", {"url": BASE})
    out = []
    for row in _ROW.findall(html_text):
        celdas = [_limpio(c) for c in _TD.findall(row)]
        if len(celdas) < 4:
            continue
        href = _HREF.search(row)
        out.append({
            "casfim": celdas[0],
            "razon_social": celdas[1],
            "nombre_corto": celdas[2],
            "sector": celdas[3],
            "detalle_url": BASE + html.unescape(href.group(1)) if href else None,
        })
    return out


def consultar(entidad: str = "", nombre_corto: str = "", sector: str = "NULL") -> list[dict[str, Any]]:
    params = {"entidad": entidad, "nombreCorto": nombre_corto, "subsectorName": sector}
    try:
        with httpx.Client(
            timeout=60.0, verify=build_ssl_verify(), follow_redirects=True,
            headers={"User-Agent": default_user_agent("mp_cnbv_fintech")},
        ) as c:
            r = c.get(f"{BASE}/Consulta/ConsultaEntidad", params=params)
            r.raise_for_status()
    except httpx.HTTPError as exc:
        raise handle_httpx_error(exc) from exc
    return parsear(r.text)
