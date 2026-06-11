"""Async client for Mercado Pago REST API.

Base URL (sandbox + production share base): https://api.mercadopago.com

Auth: Bearer access token. Sandbox tokens start with `TEST-`, production
with `APP_USR-`. The token alone determines which environment you hit;
there's no separate "env" flag like Facturama.

Tools implemented:
- create_preference (Checkout Pro link)
- get_preference
- list_payments (filtros: status, date range, external_reference)
- get_payment
- refund_payment (full or partial)
- cancel_payment (only pending)

Mock mode (no MERCADOPAGO_ACCESS_TOKEN) produces plausible synthetic
responses with `simulated: true` and stable IDs for testing.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

# Make shared/ importable
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import (  # noqa: E402
    ConfigError,
    McpError,
    NotFoundError,
    UpstreamError,
    handle_httpx_error,
)
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

NAMESPACE = "mercadopago_mcp"
MP_BASE_URL = "https://api.mercadopago.com"
SANDBOX_PUBLIC_CHECKOUT = "https://sandbox.mercadopago.com.mx/checkout/v1/redirect"
PROD_PUBLIC_CHECKOUT = "https://www.mercadopago.com.mx/checkout/v1/redirect"
REQUEST_TIMEOUT_S = 20.0


class MercadoPagoClient:
    """Async client over Mercado Pago API with mock + cache + bitácora."""

    def __init__(
        self,
        access_token: str | None = None,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        explicit = access_token is not None
        if access_token is None:
            access_token = os.environ.get("MERCADOPAGO_ACCESS_TOKEN") or None

        self._access_token = access_token
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

        if os.environ.get("PLUGINS_MX_MOCK") == "1":
            self._mock_mode = True
        elif explicit or self._access_token:
            self._mock_mode = False
        else:
            self._mock_mode = is_mock_mode(["MERCADOPAGO_ACCESS_TOKEN"])

    @property
    def is_mock(self) -> bool:
        return self._mock_mode

    @property
    def environment(self) -> str:
        """Sandbox vs production based on token prefix."""
        if not self._access_token:
            return "mock"
        if self._access_token.startswith("TEST-"):
            return "sandbox"
        if self._access_token.startswith("APP_USR-"):
            return "production"
        return "unknown"

    # ---------- preferences ----------

    async def create_preference(self, preference: dict[str, Any]) -> dict[str, Any]:
        """Create a checkout preference (returns a payable URL).

        Minimal preference payload:
            {
              "items": [{"title": "...", "quantity": 1, "unit_price": 100.0,
                         "currency_id": "MXN"}],
              "payer": {"email": "..."},
              "back_urls": {"success": "...", "failure": "...", "pending": "..."},
              "notification_url": "https://yourapp/webhook",
              "external_reference": "your_internal_id",
              "expires": true,
              "expiration_date_to": "2026-04-15T23:59:59.000-06:00"
            }

        Returns dict including preference_id + init_point + sandbox_init_point.
        """
        if self._mock_mode:
            response = self._mock_create_preference(preference)
            self._bitacora.log(
                "create_preference",
                success=True,
                params_summary={
                    "items_count": len(preference.get("items", [])),
                    "external_ref_hash": Bitacora.hash_sensitive(
                        preference.get("external_reference")
                    ),
                    "mode": "mock",
                },
                result_summary={"preference_id": response["preference_id"]},
            )
            return response

        self._require_token()
        url = f"{MP_BASE_URL}/checkout/preferences"
        start = _now_ms()
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.post(
                    url,
                    headers=self._headers(),
                    json=preference,
                )
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            err = handle_httpx_error(exc)
            self._bitacora.log(
                "create_preference",
                success=False,
                duration_ms=_now_ms() - start,
                error={"code": err.code, "message": err.message},
            )
            raise err from exc

        result = {
            "preference_id": body.get("id"),
            "init_point": body.get("init_point"),
            "sandbox_init_point": body.get("sandbox_init_point"),
            "client_id": body.get("client_id"),
            "collector_id": body.get("collector_id"),
            "external_reference": body.get("external_reference"),
            "date_created": body.get("date_created"),
            "expires": body.get("expires"),
            "expiration_date_to": body.get("expiration_date_to"),
            "simulated": False,
            "raw_response": body,
        }
        self._bitacora.log(
            "create_preference",
            success=True,
            duration_ms=_now_ms() - start,
            params_summary={
                "items_count": len(preference.get("items", [])),
                "external_ref_hash": Bitacora.hash_sensitive(
                    preference.get("external_reference")
                ),
            },
            result_summary={"preference_id": result["preference_id"]},
        )
        return result

    async def get_preference(self, preference_id: str) -> dict[str, Any]:
        """Read back a previously-created preference."""
        cache_key = f"preference_{preference_id}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        if self._mock_mode:
            response = mark_simulated(
                {
                    "preference_id": preference_id,
                    "init_point": f"{SANDBOX_PUBLIC_CHECKOUT}?pref_id={preference_id}",
                    "external_reference": "mock_ref",
                    "date_created": datetime.now(timezone.utc).isoformat(),
                }
            )
            self._cache.set(cache_key, response, ttl_minutes=15)
            return response

        self._require_token()
        url = f"{MP_BASE_URL}/checkout/preferences/{preference_id}"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=self._headers())
                if resp.status_code == 404:
                    raise NotFoundError(f"Preference {preference_id} no encontrada.")
                resp.raise_for_status()
                body = resp.json()
        except McpError:
            raise
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        response = {**body, "simulated": False}
        self._cache.set(cache_key, response, ttl_minutes=15)
        return response

    # ---------- payments ----------

    async def get_payment(self, payment_id: str | int) -> dict[str, Any]:
        """Get a payment by ID. Cache 2 min (status can change)."""
        cache_key = f"payment_{payment_id}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        if self._mock_mode:
            response = self._mock_payment(str(payment_id))
            self._cache.set(cache_key, response, ttl_minutes=2)
            return response

        self._require_token()
        url = f"{MP_BASE_URL}/v1/payments/{payment_id}"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=self._headers())
                if resp.status_code == 404:
                    raise NotFoundError(f"Pago {payment_id} no encontrado.")
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
        external_reference: str | None = None,
        status: str | None = None,
        fecha_desde: str | None = None,
        fecha_hasta: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Search payments by filters. Cache 1 min."""
        if self._mock_mode:
            return mark_simulated(
                {
                    "results": [],
                    "paging": {"total": 0, "limit": limit, "offset": offset},
                    "filters_applied": {
                        "external_reference": external_reference,
                        "status": status,
                        "fecha_desde": fecha_desde,
                        "fecha_hasta": fecha_hasta,
                    },
                },
                note="Búsqueda simulada — no devuelve resultados reales.",
            )

        self._require_token()
        url = f"{MP_BASE_URL}/v1/payments/search"
        params: dict[str, Any] = {"limit": str(limit), "offset": str(offset)}
        if external_reference:
            params["external_reference"] = external_reference
        if status:
            params["status"] = status
        if fecha_desde:
            params["begin_date"] = fecha_desde
        if fecha_hasta:
            params["end_date"] = fecha_hasta

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=self._headers(), params=params)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        return {**body, "simulated": False}

    # ---------- refunds ----------

    async def refund_payment(
        self,
        payment_id: str | int,
        amount: float | None = None,
    ) -> dict[str, Any]:
        """Refund a payment. amount=None → full refund.

        Returns the refund object with refund_id and status.
        """
        if self._mock_mode:
            response = mark_simulated(
                {
                    "id": int(secrets.randbits(31)),
                    "payment_id": int(payment_id) if str(payment_id).isdigit() else payment_id,
                    "amount": amount,  # None = full
                    "status": "approved",
                    "date_created": datetime.now(timezone.utc).isoformat(),
                    "source": {"name": "mock"},
                }
            )
            self._bitacora.log(
                "refund_payment",
                success=True,
                params_summary={
                    "payment_id_hash": Bitacora.hash_sensitive(str(payment_id)),
                    "is_partial": amount is not None,
                    "mode": "mock",
                },
                result_summary={"refund_id": response["id"], "status": response["status"]},
            )
            return response

        self._require_token()
        url = f"{MP_BASE_URL}/v1/payments/{payment_id}/refunds"
        body_data: dict[str, Any] = {}
        if amount is not None:
            body_data["amount"] = amount

        start = _now_ms()
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.post(
                    url,
                    headers=self._headers(),
                    json=body_data if body_data else None,
                )
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            err = handle_httpx_error(exc)
            self._bitacora.log(
                "refund_payment",
                success=False,
                duration_ms=_now_ms() - start,
                params_summary={
                    "payment_id_hash": Bitacora.hash_sensitive(str(payment_id)),
                    "is_partial": amount is not None,
                },
                error={"code": err.code, "message": err.message},
            )
            raise err from exc

        # Invalidate the payment cache — its status will change
        self._cache.invalidate(f"payment_{payment_id}")

        self._bitacora.log(
            "refund_payment",
            success=True,
            duration_ms=_now_ms() - start,
            params_summary={
                "payment_id_hash": Bitacora.hash_sensitive(str(payment_id)),
                "is_partial": amount is not None,
            },
            result_summary={"refund_id": body.get("id"), "status": body.get("status")},
        )
        return {**body, "simulated": False}

    # ---------- cancel ----------

    async def cancel_payment(self, payment_id: str | int) -> dict[str, Any]:
        """Cancel a pending payment. Only works on status=pending."""
        if self._mock_mode:
            response = mark_simulated(
                {
                    "id": payment_id,
                    "status": "cancelled",
                    "date_last_updated": datetime.now(timezone.utc).isoformat(),
                }
            )
            self._bitacora.log(
                "cancel_payment",
                success=True,
                params_summary={
                    "payment_id_hash": Bitacora.hash_sensitive(str(payment_id)),
                    "mode": "mock",
                },
            )
            return response

        self._require_token()
        url = f"{MP_BASE_URL}/v1/payments/{payment_id}"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.put(
                    url,
                    headers=self._headers(),
                    json={"status": "cancelled"},
                )
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        self._cache.invalidate(f"payment_{payment_id}")
        return {**body, "simulated": False}

    # ---------- helpers ----------

    def _headers(self) -> dict[str, str]:
        if not self._access_token:
            raise ConfigError(
                "Mercado Pago: configura MERCADOPAGO_ACCESS_TOKEN. "
                "Sandbox: registra app en https://www.mercadopago.com.mx/developers."
            )
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _require_token(self) -> None:
        if not self._access_token:
            raise ConfigError(
                "Mercado Pago: configura MERCADOPAGO_ACCESS_TOKEN. "
                "Sandbox: registra app en https://www.mercadopago.com.mx/developers."
            )

    # ---------- mock helpers ----------

    @staticmethod
    def _mock_create_preference(preference: dict) -> dict[str, Any]:
        """Generate a deterministic mock preference response.

        preference_id is sha256(payload sorted) → same payload always
        yields the same preference_id, useful for tests.
        """
        import json

        canonical = json.dumps(preference, sort_keys=True, ensure_ascii=False, default=str)
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        pref_id = f"{digest[:7]}-{digest[7:15]}"
        return mark_simulated(
            {
                "preference_id": pref_id,
                "init_point": f"{SANDBOX_PUBLIC_CHECKOUT}?pref_id={pref_id}",
                "sandbox_init_point": f"{SANDBOX_PUBLIC_CHECKOUT}?pref_id={pref_id}",
                "external_reference": preference.get("external_reference"),
                "client_id": "mock_client",
                "collector_id": 0,
                "date_created": datetime.now(timezone.utc).isoformat(),
                "expires": preference.get("expires", False),
                "expiration_date_to": preference.get("expiration_date_to"),
            },
            note="Preference SIMULADA — el init_point no carga un checkout real.",
        )

    @staticmethod
    def _mock_payment(payment_id: str) -> dict[str, Any]:
        """Generate a plausible mock payment in 'approved' state.

        Status is deterministic per payment_id (so tests can assert specific
        states by choosing the right id). All ids ending in odd digit → approved,
        even digit → pending. id="reject" → rejected. Just enough variety for tests.
        """
        if payment_id == "reject":
            status = "rejected"
            status_detail = "cc_rejected_other_reason"
        elif payment_id == "pending":
            status = "pending"
            status_detail = "pending_contingency"
        elif payment_id.isdigit() and int(payment_id) % 2 == 0:
            status = "pending"
            status_detail = "pending_contingency"
        else:
            status = "approved"
            status_detail = "accredited"

        return mark_simulated(
            {
                "id": payment_id if not payment_id.isdigit() else int(payment_id),
                "status": status,
                "status_detail": status_detail,
                "transaction_amount": 100.0,
                "currency_id": "MXN",
                "external_reference": "mock_ref",
                "date_created": datetime.now(timezone.utc).isoformat(),
                "date_approved": (
                    datetime.now(timezone.utc).isoformat() if status == "approved" else None
                ),
                "payment_method_id": "visa",
                "payment_type_id": "credit_card",
                "payer": {"id": "mock_payer", "email": "test@example.com"},
            },
            note="Pago SIMULADO — no representa una transacción real.",
        )


def _now_ms() -> float:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return loop.time() * 1000
    except RuntimeError:
        pass
    return 0.0
