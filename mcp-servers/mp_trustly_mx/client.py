"""Cliente Trustly MX — open banking.

API: https://api.trustly.com (versión global, MX sandbox separado)
Auth: API Key + HMAC sobre body.

Mock-first sin TRUSTLY_API_KEY.
"""

from __future__ import annotations

import os
import secrets
import sys
from datetime import datetime, timedelta, timezone
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


NAMESPACE = "trustly_mx_mcp"
TRUSTLY_SANDBOX_URL = "https://test.api.trustly.com"
TRUSTLY_PROD_URL = "https://api.trustly.com"
REQUEST_TIMEOUT_S = 20.0


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class TrustlyMxClient:
    def __init__(
        self,
        api_key: str | None = None,
        environment: str | None = None,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        explicit = api_key is not None
        if api_key is None:
            api_key = os.environ.get("TRUSTLY_API_KEY", "").strip() or None
        if environment is None:
            environment = os.environ.get("TRUSTLY_ENV", "sandbox").lower()

        self._api_key = api_key
        self._environment = environment
        self._base_url = (
            TRUSTLY_PROD_URL if environment == "production" else TRUSTLY_SANDBOX_URL
        )

        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

        if os.environ.get("PLUGINS_MX_MOCK") == "1":
            self._mock = True
        elif explicit or api_key:
            self._mock = False
        else:
            self._mock = is_mock_mode(["TRUSTLY_API_KEY"])

    @property
    def is_mock(self) -> bool:
        return self._mock

    @property
    def environment(self) -> str:
        return self._environment

    def _require_key(self) -> None:
        if not self._api_key:
            raise ConfigError("TRUSTLY_API_KEY no configurado.")

    def _headers(self) -> dict[str, str]:
        if not self._api_key:
            raise ConfigError("TRUSTLY_API_KEY no configurado.")
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _log(self, op: str, params: dict[str, Any]) -> None:
        safe = dict(params)
        for k in ("clabe", "email"):
            if k in safe and safe[k]:
                safe[f"{k}_hash"] = Bitacora.hash_sensitive(str(safe.pop(k)))
        self._bitacora.log(op, success=True, params_summary=safe)

    # ---------- tools ----------

    async def create_payment_request(
        self,
        amount_mxn: float,
        external_reference: str,
        customer_email: str,
        description: str = "",
    ) -> dict[str, Any]:
        """Crea solicitud de pago — cliente recibe link/QR para autorizar en su banco."""
        self._log("create_payment", {
            "amount_mxn": amount_mxn,
            "external_reference": external_reference,
            "email": customer_email,
        })

        if self._mock:
            payment_id = f"trustly_demo_{secrets.token_hex(8)}"
            return mark_simulated({
                "payment_id": payment_id,
                "external_reference": external_reference,
                "amount_mxn": amount_mxn,
                "currency": "MXN",
                "status": "pending",
                "checkout_url": f"https://pay-demo.trustly.com/checkout/{payment_id}",
                "expires_at": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
                "supported_banks_count": 8,
                "created_at": _now_iso(),
            })

        self._require_key()
        url = f"{self._base_url}/v1/payments"
        body = {
            "amount": amount_mxn,
            "currency": "MXN",
            "external_reference": external_reference,
            "customer": {"email": customer_email},
            "description": description,
        }
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.post(url, headers=self._headers(), json=body)
                resp.raise_for_status()
                return {**resp.json(), "simulated": False}
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

    async def get_payment_status(self, payment_id: str) -> dict[str, Any]:
        cache_key = f"payment_{payment_id}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("get_payment", {"payment_id": payment_id})

        if self._mock:
            response = mark_simulated({
                "payment_id": payment_id,
                "status": "completed" if payment_id.startswith("trustly_demo_paid_") else "pending",
                "amount_mxn": 1500.00,
                "currency": "MXN",
                "external_reference": "demo_ref",
                "completed_at": _now_iso() if payment_id.startswith("trustly_demo_paid_") else None,
            })
            self._cache.set(cache_key, response, ttl_minutes=2)
            return response

        self._require_key()
        url = f"{self._base_url}/v1/payments/{payment_id}"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=self._headers())
                if resp.status_code == 404:
                    raise NotFoundError(f"Payment {payment_id} no encontrado.")
                resp.raise_for_status()
                body = resp.json()
        except McpError:
            raise
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        response = {**body, "simulated": False}
        self._cache.set(cache_key, response, ttl_minutes=2)
        return response

    async def list_payments(
        self,
        status: str | None = None,
        limit: int = 25,
    ) -> dict[str, Any]:
        self._log("list_payments", {"status": status, "limit": limit})
        if self._mock:
            return mark_simulated({
                "payments": [
                    {
                        "payment_id": f"trustly_demo_{i}",
                        "amount_mxn": 1500.00 * (i + 1),
                        "status": "completed" if i % 2 == 0 else "pending",
                        "created_at": _now_iso(),
                    }
                    for i in range(min(limit, 3))
                ],
                "filters": {"status": status},
            })

        self._require_key()
        params: dict[str, str] = {"limit": str(limit)}
        if status:
            params["status"] = status
        url = f"{self._base_url}/v1/payments"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=self._headers(), params=params)
                resp.raise_for_status()
                return {**resp.json(), "simulated": False}
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

    async def refund_payment(
        self, payment_id: str, amount_mxn: float | None = None
    ) -> dict[str, Any]:
        self._log("refund_payment", {"payment_id": payment_id, "amount": amount_mxn})

        if self._mock:
            return mark_simulated({
                "refund_id": f"refund_{secrets.token_hex(8)}",
                "payment_id": payment_id,
                "amount_mxn": amount_mxn,
                "status": "approved",
                "created_at": _now_iso(),
            })

        self._require_key()
        url = f"{self._base_url}/v1/payments/{payment_id}/refunds"
        body = {}
        if amount_mxn is not None:
            body["amount"] = amount_mxn
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.post(url, headers=self._headers(), json=body or None)
                resp.raise_for_status()
                return {**resp.json(), "simulated": False}
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
