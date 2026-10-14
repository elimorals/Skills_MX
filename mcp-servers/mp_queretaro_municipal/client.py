"""Cliente mp_queretaro_municipal — predial real vía webservices consultaLC v2.

Flujo descubierto 2026-10-14 en `main.ncc.js` del portal oficial:
  1. POST agenda_digital.php?validate=1&clave_catastral=…&letras_nombre=…
     → {"codigo":"000","datos":"{\"status\":201|200|1|894,…}"}  (valida dueño)
  2. GET functions.php?clave_catastral=…&tpobus=L&periodo_calculo=NULL
     → {"errmsg"?, "periodos", "direccion", "importe", "fechavigen", "lineacap", …}
Sin CAPTCHA. Se respeta el paso 1 (validación de 4 letras del propietario) igual
que el portal: no se consulta el adeudo si el portal rechaza al propietario.
"""

from __future__ import annotations

import json
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
from shared.errors import (  # noqa: E402
    NotFoundError,
    UpstreamError,
    ValidationError,
    handle_httpx_error,
)
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

NAMESPACE = "queretaro_mun"
BASE_URL = "https://webservices.municipiodequeretaro.gob.mx/consultaLC/v2/"
_HEADERS = {"User-Agent": "Mozilla/5.0 (plugins-mx)", "X-Requested-With": "XMLHttpRequest"}


def _json(resp: httpx.Response) -> dict[str, Any]:
    try:
        return resp.json()
    except ValueError as exc:
        raise UpstreamError(
            "consultaLC respondió algo que no es JSON (¿cambió el portal?)",
            {"url": str(resp.url), "body_preview": resp.text[:200]},
        ) from exc


def _monto(txt: Any) -> float | None:
    if txt in (None, ""):
        return None
    try:
        return float(re.sub(r"[^\d.]", "", str(txt)))
    except ValueError:
        return None


class QueretaroMunClient:
    def __init__(self, bitacora: Bitacora | None = None, http: httpx.Client | None = None) -> None:
        self.bitacora = bitacora or Bitacora(NAMESPACE)
        self._http = http

    def _client(self) -> httpx.Client:
        return self._http or httpx.Client(timeout=30, headers=_HEADERS, follow_redirects=True)

    def consultar_predial(self, clave_catastral: str, letras_propietario: str) -> dict[str, Any]:
        clave = re.sub(r"\D", "", clave_catastral or "")
        letras = (letras_propietario or "").strip().upper()
        if len(clave) != 15:
            raise ValidationError("La clave catastral de Querétaro tiene 15 dígitos.")
        if not re.fullmatch(r"[A-ZÑ]{4}", letras):
            raise ValidationError("letras_propietario: 4 letras del nombre del propietario.")
        self.bitacora.log(
            "consultar_predial", success=True,
            params_summary={"clave_hash": Bitacora.hash_sensitive(clave)},
        )
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"clave_catastral": clave, "estatus": "con_adeudo", "importe_mxn": 1234.0})

        client = self._client()
        try:
            r1 = client.post(
                BASE_URL + "agenda_digital.php",
                params={"validate": "1", "clave_catastral": clave, "letras_nombre": letras},
            )
            r1.raise_for_status()
            agenda = _json(r1)
            if agenda.get("codigo") != "000":
                raise UpstreamError(
                    f"consultaLC agenda_digital falló: {agenda.get('mensaje')}", {"respuesta": agenda}
                )
            datos = json.loads(agenda.get("datos") or "{}")
            if datos.get("status") == 201:
                raise NotFoundError(
                    "El portal no encontró el predio con esa clave y letras del propietario.",
                    {"mensaje_portal": datos.get("message")},
                )
            r2 = client.get(
                BASE_URL + "functions.php",
                params={"clave_catastral": clave, "tpobus": "L", "periodo_calculo": "NULL"},
            )
            r2.raise_for_status()
            data = _json(r2)
        except httpx.HTTPError as exc:
            raise handle_httpx_error(exc) from exc
        finally:
            if self._http is None:
                client.close()

        msg = (data.get("errmsg") or "").strip()
        base = {
            "clave_catastral": clave,
            "fuente": BASE_URL,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "simulated": False,
        }
        if msg:
            low = msg.lower()
            if "sin adeudo" in low or "cancelado" in low:
                return {**base, "estatus": "al_corriente", "importe_mxn": 0.0, "mensaje_portal": msg}
            if "no existe" in low:
                raise NotFoundError(f"consultaLC: {msg}", {"clave_catastral": clave})
            raise UpstreamError(f"consultaLC: {msg}", {"clave_catastral": clave})
        importe = _monto(data.get("importe"))
        if importe is None:
            raise UpstreamError("consultaLC no devolvió importe (¿cambió el portal?)", {"llaves": list(data)})
        return {
            **base,
            "estatus": "con_adeudo" if importe > 0 else "al_corriente",
            "importe_mxn": importe,
            "direccion": data.get("direccion"),
            "periodos": data.get("periodos") or [],
            "fecha_vigencia": data.get("fechavigen"),
            "linea_captura": data.get("lineacap"),
            "url_pago": data.get("urlpagoenlinea"),
        }
