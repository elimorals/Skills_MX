"""Cliente mp_tijuana_municipal.

- Predial (adeudo): pagos.tijuana.gob.mx exige cuenta del contribuyente (usuario +
  contraseña o Llave BC). No hay consulta pública → handoff humano.
- Programa de Protección Ciudadana ("vivienda asegurada"): consulta pública por
  clave catastral en PagosEnLinea/seguro/index.aspx (ASP.NET, postback del
  TextBox, sin CAPTCHA). Verificado 2026-10-14.
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
from shared.errors import UpstreamError, ValidationError, handle_httpx_error  # noqa: E402
from shared.handoff_humano import handoff_humano  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

NAMESPACE = "tijuana_mun"
URL_PAGOS = "https://pagos.tijuana.gob.mx/pagosEnLinea/index.aspx"
URL_SEGURO = "https://pagos.tijuana.gob.mx/PagosEnLinea/seguro/index.aspx"
_CAMPO = "ctl00$ContentPlaceHolder1$tbPredialSeguro"
_HEADERS = {"User-Agent": "Mozilla/5.0 (plugins-mx)"}


def _hidden_fields(page: str) -> dict[str, str]:
    campos = {}
    for tag in re.findall(r"<input[^>]+type=\"hidden\"[^>]*>", page):
        name = re.search(r'name="([^"]+)"', tag)
        value = re.search(r'value="([^"]*)"', tag)
        if name:
            campos[html.unescape(name.group(1))] = html.unescape(value.group(1)) if value else ""
    return campos


def parse_mensaje_seguro(page: str) -> str:
    m = re.search(r'id="ContentPlaceHolder1_lbMsjSeguro"[^>]*>(.*?)</span>', page, re.S)
    if not m:
        raise UpstreamError("Tijuana seguro: no se encontró lbMsjSeguro (¿cambió el portal?)", {"url": URL_SEGURO})
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))).strip()


class TijuanaMunClient:
    def __init__(self, bitacora: Bitacora | None = None, http: httpx.Client | None = None) -> None:
        self.bitacora = bitacora or Bitacora(NAMESPACE)
        self._http = http

    def consultar_predial(self, clave_catastral: str) -> dict[str, Any]:
        self.bitacora.log("consultar_predial", success=True, params_summary={})
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"clave_catastral": clave_catastral, "adeudo_total_mxn": 980.0})
        return handoff_humano(
            portal=URL_PAGOS,
            motivo="login",
            detalle="El adeudo de predial en Tijuana solo se muestra con cuenta del contribuyente.",
            pasos=[
                f"Abrir {URL_PAGOS}",
                "Ingresar con usuario/contraseña del portal o con Llave BC",
                f"Buscar la clave catastral {clave_catastral} y leer el adeudo",
            ],
        )

    def consultar_vivienda_asegurada(self, clave_catastral: str) -> dict[str, Any]:
        clave = (clave_catastral or "").strip().upper()
        if not re.fullmatch(r"[A-Z0-9-]{4,20}", clave):
            raise ValidationError("clave_catastral: 4-20 caracteres alfanuméricos.")
        self.bitacora.log("vivienda_asegurada", success=True,
                          params_summary={"clave_hash": Bitacora.hash_sensitive(clave)})
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"clave_catastral": clave, "asegurada": True})

        client = self._http or httpx.Client(timeout=30, headers=_HEADERS, follow_redirects=True)
        try:
            r = client.get(URL_SEGURO)
            r.raise_for_status()
            form = _hidden_fields(r.text)
            form["__EVENTTARGET"] = _CAMPO
            form[_CAMPO] = clave
            r2 = client.post(URL_SEGURO, data=form)
            r2.raise_for_status()
        except httpx.HTTPError as exc:
            raise handle_httpx_error(exc) from exc
        finally:
            if self._http is None:
                client.close()

        msg = parse_mensaje_seguro(r2.text)
        if not msg:
            raise UpstreamError("Tijuana seguro: mensaje vacío tras la consulta.", {"url": URL_SEGURO})
        return {
            "clave_catastral": clave,
            "asegurada": "no asegurada" not in msg.lower(),
            "mensaje_portal": msg,
            "fuente": URL_SEGURO,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "simulated": False,
        }
