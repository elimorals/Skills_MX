"""Cliente Clip Terminal — POS MX."""

from __future__ import annotations

import os
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import ConfigError, McpError, NotFoundError, handle_httpx_error  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402


NAMESPACE = "clip_terminal_mcp"
CLIP_API_URL = "https://api.payclip.com"  # verificar 2026
REQUEST_TIMEOUT_S = 20.0


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ClipTerminalClient:
    def __init__(
        self,
        api_key: str | None = None,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        explicit = api_key is not None
        if api_key is None:
            api_key = os.environ.get("CLIP_API_KEY", "").strip() or None

        self._api_key = api_key
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

        if os.environ.get("PLUGINS_MX_MOCK") == "1":
            self._mock = True
        elif explicit or api_key:
            self._mock = False
        else:
            self._mock = is_mock_mode(["CLIP_API_KEY"])

    @property
    def is_mock(self) -> bool:
        return self._mock

    def _require_key(self) -> None:
        if not self._api_key:
            raise ConfigError("CLIP_API_KEY no configurado.")

    def _headers(self) -> dict[str, str]:
        self._require_key()
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def _log(self, op: str, params: dict[str, Any]) -> None:
        self._bitacora.log(op, success=True, params_summary=params)

    # ---------- tools ----------

    async def list_charges(
        self, fecha_desde: str | None = None, limit: int = 50, status: str | None = None
    ) -> dict[str, Any]:
        self._log("list_charges", {"fecha_desde": fecha_desde, "limit": limit, "status": status})

        if self._mock:
            return mark_simulated({
                "charges": [
                    {
                        "id": f"clip_charge_{i:06d}",
                        "amount_mxn": 250.00 * (i + 1),
                        "status": "approved" if i % 3 != 0 else "declined",
                        "payment_method": "card_visa",
                        "last4": "4242",
                        "created_at": _now_iso(),
                        "terminal_id": "TERM-001",
                    }
                    for i in range(min(limit, 5))
                ],
                "total_count": 247,
            })

        self._require_key()
        params: dict[str, str] = {"limit": str(limit)}
        if fecha_desde:
            params["from"] = fecha_desde
        if status:
            params["status"] = status
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(
                    f"{CLIP_API_URL}/v1/charges",
                    headers=self._headers(),
                    params=params,
                )
                resp.raise_for_status()
                return {**resp.json(), "simulated": False}
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

    async def get_charge(self, charge_id: str) -> dict[str, Any]:
        cache_key = f"charge_{charge_id}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("get_charge", {"charge_id": charge_id})

        if self._mock:
            r = mark_simulated({
                "id": charge_id,
                "amount_mxn": 580.00,
                "status": "approved",
                "payment_method": "card_master",
                "last4": "5555",
                "msi": "1_pago",
                "comision_porcentaje": 3.6,
                "comision_mxn": 20.88,
                "monto_neto_mxn": 559.12,
                "terminal_id": "TERM-001",
                "created_at": _now_iso(),
            })
            self._cache.set(cache_key, r, ttl_minutes=5)
            return r

        self._require_key()
        url = f"{CLIP_API_URL}/v1/charges/{charge_id}"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=self._headers())
                if resp.status_code == 404:
                    raise NotFoundError(f"Charge {charge_id} no encontrado.")
                resp.raise_for_status()
                body = resp.json()
        except McpError:
            raise
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        r = {**body, "simulated": False}
        self._cache.set(cache_key, r, ttl_minutes=5)
        return r

    async def refund_charge(
        self, charge_id: str, amount_mxn: float | None = None
    ) -> dict[str, Any]:
        self._log("refund_charge", {"charge_id": charge_id, "amount_mxn": amount_mxn})

        if self._mock:
            return mark_simulated({
                "refund_id": f"clip_refund_{secrets.token_hex(8)}",
                "charge_id": charge_id,
                "amount_mxn": amount_mxn,
                "status": "approved",
                "created_at": _now_iso(),
            })

        self._require_key()
        url = f"{CLIP_API_URL}/v1/charges/{charge_id}/refund"
        body = {"amount": amount_mxn} if amount_mxn is not None else {}
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.post(url, headers=self._headers(), json=body or None)
                resp.raise_for_status()
                return {**resp.json(), "simulated": False}
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

    async def get_terminal_status(self, terminal_id: str) -> dict[str, Any]:
        self._log("get_terminal_status", {"terminal_id": terminal_id})

        if self._mock:
            return mark_simulated({
                "terminal_id": terminal_id,
                "modelo": "Clip Pro",
                "status": "active",
                "ultima_transaccion": _now_iso(),
                "bateria_porcentaje": 78,
                "señal_wifi_porcentaje": 92,
                "transacciones_ultimas_24h": 47,
            })

        self._require_key()
        url = f"{CLIP_API_URL}/v1/terminals/{terminal_id}"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=self._headers())
                if resp.status_code == 404:
                    raise NotFoundError(f"Terminal {terminal_id} no encontrada.")
                resp.raise_for_status()
                return {**resp.json(), "simulated": False}
        except McpError:
            raise
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

    async def get_settlement(self, fecha: str) -> dict[str, Any]:
        """Liquidación del día (depósito a tu cuenta bancaria)."""
        self._log("get_settlement", {"fecha": fecha})

        if self._mock:
            return mark_simulated({
                "fecha_liquidacion": fecha,
                "total_brutos_mxn": 12450.00,
                "comisiones_mxn": 448.20,
                "retencion_iva_mxn": 71.71,
                "retencion_isr_mxn": 0.00,
                "total_neto_depositado_mxn": 11930.09,
                "transacciones_count": 47,
                "fecha_deposito_banco": fecha,
                "clabe_destino": "012180001234567890",
            })

        self._require_key()
        url = f"{CLIP_API_URL}/v1/settlements/{fecha}"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=self._headers())
                resp.raise_for_status()
                return {**resp.json(), "simulated": False}
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
