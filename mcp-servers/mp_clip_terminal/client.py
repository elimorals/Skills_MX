"""Cliente Clip — transacciones, reembolsos, depósitos y PinPad.

Doc oficial: https://developer.clip.mx (índice: https://developer.clip.mx/llms.txt)
Auth: token `Basic base64(api_key:clave_secreta)` creado en el Panel de Desarrollador de Clip;
va en `Authorization` o en `x-api-key` según la API. Cada API vive en un host distinto:
- Transacciones y depósitos: https://api-gw.payclip.com
- Reembolsos: https://api.payclip.com
- PinPad: https://api.payclip.io
"""

from __future__ import annotations

import base64
import os
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import httpx

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import ConfigError, NotFoundError, handle_httpx_error  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402


NAMESPACE = "clip_terminal_mcp"
GW = "https://api-gw.payclip.com"
REFUNDS = "https://api.payclip.com"
PINPAD = "https://api.payclip.io"
CRED_VARS = ["CLIP_API_KEY", "CLIP_SECRET_KEY"]
REQUEST_TIMEOUT_S = 20.0


class ClipTerminalClient:
    def __init__(self, bitacora: Bitacora | None = None, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)
        self._transport = transport

    @property
    def is_mock(self) -> bool:
        return is_mock_mode(CRED_VARS)

    def _token(self) -> str:
        key, secret = (os.environ.get(v, "").strip() for v in CRED_VARS)
        if not (key and secret):
            raise ConfigError("Faltan CLIP_API_KEY / CLIP_SECRET_KEY (Panel de Desarrollador de Clip).")
        return "Basic " + base64.b64encode(f"{key}:{secret}".encode()).decode()

    async def _call(self, method: str, url: str, header: str = "Authorization", **kw: Any) -> Any:
        token = self._token()
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S, transport=self._transport) as c:
                r = await c.request(method, url, headers={header: token, "Accept": "application/json"}, **kw)
                r.raise_for_status()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
        return r.json() if r.content else {}

    def _log(self, op: str, params: dict[str, Any]) -> None:
        self._bitacora.log(op, success=True, params_summary=params)

    async def list_charges(
        self, fecha_desde: str | None = None, limit: int = 50, status: str | None = None
    ) -> dict[str, Any]:
        """Transacciones en un rango (GET /payments). Por defecto, de `fecha_desde` (o hace 7 días) a hoy."""
        self._log("list_charges", {"fecha_desde": fecha_desde, "limit": limit, "status": status})
        if self.is_mock:
            return mark_simulated({"charges": [], "total_count": 0})
        desde = fecha_desde or (date.today() - timedelta(days=7)).isoformat()
        params = {"from": desde, "to": date.today().isoformat(), "limit": limit, "status": status}
        body = await self._call("GET", f"{GW}/payments", params={k: v for k, v in params.items() if v is not None})
        return {**body, "simulated": False} if isinstance(body, dict) else {"charges": body, "simulated": False}

    async def get_charge(self, charge_id: str) -> dict[str, Any]:
        """Transacción por número de recibo (GET /payments/receipt-no/{receipt_no})."""
        self._log("get_charge", {"charge_id": charge_id})
        if self.is_mock:
            return mark_simulated({"receipt_no": charge_id})
        return {**await self._call("GET", f"{GW}/payments/receipt-no/{charge_id}"), "simulated": False}

    async def refund_charge(self, charge_id: str, amount_mxn: float | None = None, reason: str = "Solicitud del cliente") -> dict[str, Any]:
        """Reembolso total o parcial de un recibo (POST /refunds). Sin monto = total de la transacción."""
        self._log("refund_charge", {"charge_id": charge_id, "amount_mxn": amount_mxn})
        if self.is_mock:
            return mark_simulated({"charge_id": charge_id, "amount_mxn": amount_mxn})
        if amount_mxn is None:
            cargo = await self.get_charge(charge_id)
            amount_mxn = cargo.get("amount")
            if amount_mxn is None:
                raise NotFoundError(f"No se pudo leer el monto del recibo {charge_id} para reembolso total")
        body = {"amount": amount_mxn, "reason": reason, "reference": {"type": "receipt", "id": charge_id}}
        return {**await self._call("POST", f"{REFUNDS}/refunds", json=body), "simulated": False}

    async def get_terminal_status(self, terminal_id: str) -> dict[str, Any]:
        """Estado de un PinPad por número de serie (GET /f2f/pinpad/v1/devices/status)."""
        self._log("get_terminal_status", {"terminal_id": terminal_id})
        if self.is_mock:
            return mark_simulated({"serial_number": terminal_id, "status": "active"})
        for d in await self._call("GET", f"{PINPAD}/f2f/pinpad/v1/devices/status") or []:
            if d.get("serial_number") == terminal_id:
                return {**d, "simulated": False}
        raise NotFoundError(f"PinPad {terminal_id} no está registrado en la cuenta")

    async def get_settlement(self, fecha: str) -> dict[str, Any]:
        """Depósitos del día (GET /settlements?from=&to=, header x-api-key)."""
        self._log("get_settlement", {"fecha": fecha})
        if self.is_mock:
            return mark_simulated({"fecha": fecha, "settlements": []})
        body = await self._call("GET", f"{GW}/settlements", header="x-api-key", params={"from": fecha, "to": fecha})
        return {"fecha": fecha, "settlements": body, "simulated": False}
