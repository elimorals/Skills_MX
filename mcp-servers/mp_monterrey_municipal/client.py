"""Cliente mp_monterrey_municipal — predial real de Monterrey (asp.monterrey.gob.mx).

Portal ASP.NET WebForms sin CAPTCHA (verificado 2026-10-14): GET para obtener
__VIEWSTATE/__EVENTVALIDATION y POST con `txt_buscar` (expediente catastral de 8
dígitos) + `btn_buscar`. El adeudo viene en el GridView `grv_Adeudos`; cada fila
trae `lbl_Totales_empty` (total sin bonificación) y `lbl_Totales_bnf` (con
bonificación por pago total). Expediente inexistente → `lbl_warning`.
"""

from __future__ import annotations

import html
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import NotFoundError, UpstreamError, ValidationError, handle_httpx_error  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

from mp_monterrey_municipal.catalogos import MUNICIPIOS_AMM  # noqa: E402

NAMESPACE = "monterrey_municipal_mcp"
URL_PREDIAL = "https://asp.monterrey.gob.mx/predial/"
_P = "ctl00$ContentPlaceHolder1$"
_HEADERS = {"User-Agent": "Mozilla/5.0 (plugins-mx)"}


def _text(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def _monto(txt: str) -> float | None:
    limpio = re.sub(r"[^\d.]", "", txt)
    return float(limpio) if limpio else None


def _hidden_fields(page: str) -> dict[str, str]:
    campos = {}
    for tag in re.findall(r"<input[^>]+type=\"hidden\"[^>]*>", page):
        name = re.search(r'name="([^"]+)"', tag)
        value = re.search(r'value="([^"]*)"', tag)
        if name:
            campos[html.unescape(name.group(1))] = html.unescape(value.group(1)) if value else ""
    return campos


def parse_resultado(page: str) -> dict[str, Any]:
    """Extrae adeudos del HTML de respuesta. Lanza NotFoundError/UpstreamError."""
    warn = re.search(r'id="ctl00_ContentPlaceHolder1_lbl_warning"[^>]*>(.*?)</span>', page, re.S)
    if warn and _text(warn.group(1)):
        msg = _text(warn.group(1))
        if "no existe" in msg.lower():
            raise NotFoundError(f"Predial Monterrey: {msg}")
        raise UpstreamError(f"Predial Monterrey: {msg}")

    grid = re.search(r'<table[^>]+id="[^"]*grv_Adeudos"[^>]*>(.*?)</table>', page, re.S)
    if not grid:
        raise UpstreamError(
            "Predial Monterrey: respuesta sin grv_Adeudos ni aviso (¿cambió el portal?)",
            {"url": URL_PREDIAL},
        )
    conceptos = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", grid.group(1), re.S):
        total = re.search(r'id="[^"]*lbl_Totales_empty"[^>]*>(.*?)</span>', row, re.S)
        if not total:
            continue
        bnf = re.search(r'id="[^"]*lbl_Totales_bnf"[^>]*>(.*?)</span>', row, re.S)
        celdas = [_text(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        conceptos.append({
            "celdas": [c for c in celdas if c],
            "total_mxn": _monto(_text(total.group(1))),
            "total_con_bonificacion_mxn": _monto(_text(bnf.group(1))) if bnf else None,
        })
    adeudo = round(sum(c["total_mxn"] or 0 for c in conceptos), 2)
    return {
        "estatus": "con_adeudo" if adeudo > 0 else "al_corriente",
        "adeudo_total_mxn": adeudo,
        "conceptos": conceptos,
    }


class MonterreyMunicipalClient:
    def __init__(self, bitacora: Bitacora | None = None, http: httpx.Client | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)
        self._http = http

    def consultar_predial(self, municipio: str, expediente: str) -> dict[str, Any]:
        if municipio not in MUNICIPIOS_AMM:
            raise ValidationError(
                f"Municipio '{municipio}' no soportado. Soportados: {', '.join(MUNICIPIOS_AMM)}"
            )
        expediente = re.sub(r"\D", "", expediente or "")
        self._bitacora.log("predial", success=True, params_summary={
            "municipio": municipio, "expediente_hash": Bitacora.hash_sensitive(expediente)})
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"municipio": municipio, "expediente": expediente,
                                   "estatus": "con_adeudo", "adeudo_total_mxn": 1500.0})
        if municipio != "Monterrey":
            raise UpstreamError(
                f"Predial de {municipio}: portal municipal aún no verificado; solo Monterrey es real.",
                {"municipio": municipio},
            )
        if len(expediente) != 8:
            raise ValidationError("El expediente catastral de Monterrey tiene 8 dígitos (ej. 09009009).")

        client = self._http or httpx.Client(timeout=30, headers=_HEADERS, follow_redirects=True)
        try:
            r = client.get(URL_PREDIAL)
            r.raise_for_status()
            form = _hidden_fields(r.text)
            if "__VIEWSTATE" not in form:
                raise UpstreamError("Predial Monterrey: el formulario no trae __VIEWSTATE.", {"url": URL_PREDIAL})
            form[_P + "txt_buscar"] = expediente
            form[_P + "btn_buscar"] = " Buscar "
            r2 = client.post(URL_PREDIAL, data=form)
            r2.raise_for_status()
        except httpx.HTTPError as exc:
            raise handle_httpx_error(exc) from exc
        finally:
            if self._http is None:
                client.close()

        return {
            "municipio": municipio,
            "expediente": expediente,
            **parse_resultado(r2.text),
            "fuente": URL_PREDIAL,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "simulated": False,
        }
