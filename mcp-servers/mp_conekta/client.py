"""Async client para Conekta REST API.

Base URL: https://api.conekta.io
API version: 2.1.0 (header `Accept: application/vnd.conekta-v2.1.0+json`)
Auth: HTTP Basic con API key como user (sin password).

Sandbox vs producción se determinan por la API key:
- Sandbox: empieza con `key_test_` o tiene `test` en el prefijo
- Producción: empieza con `key_live_` o `key_`

Tools cubiertos:
- create_order
- get_order
- list_orders
- create_charge_on_order
- refund_charge
- create_customer
- get_customer
- create_payment_link (vía Conekta Checkout)
- subscription_create / update / cancel

Mock mode (sin CONEKTA_API_KEY) produce respuestas sintéticas con
`simulated: true` y IDs estables para tests.
"""

from __future__ import annotations

import base64
import os
import secrets
import sys
from datetime import datetime, timedelta, timezone
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


NAMESPACE = "conekta_mcp"
CONEKTA_BASE_URL = "https://api.conekta.io"
CONEKTA_API_VERSION = "2.1.0"
REQUEST_TIMEOUT_S = 20.0


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _now_ms() -> float:
    import time

    return time.time() * 1000


class ConektaClient:
    """Async client sobre Conekta API con mock + cache + bitácora."""

    def __init__(
        self,
        api_key: str | None = None,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        explicit = api_key is not None
        if api_key is None:
            api_key = os.environ.get("CONEKTA_API_KEY") or None

        self._api_key = api_key
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

        if os.environ.get("PLUGINS_MX_MOCK") == "1":
            self._mock_mode = True
        elif explicit or self._api_key:
            self._mock_mode = False
        else:
            self._mock_mode = is_mock_mode(["CONEKTA_API_KEY"])

    @property
    def is_mock(self) -> bool:
        return self._mock_mode

    @property
    def environment(self) -> str:
        """Sandbox vs production según prefijo de la key."""
        if not self._api_key:
            return "mock"
        if "test" in self._api_key.lower():
            return "sandbox"
        if self._api_key.startswith("key_live_") or self._api_key.startswith("key_"):
            return "production"
        return "unknown"

    def _headers(self) -> dict[str, str]:
        if not self._api_key:
            raise ConfigError("CONEKTA_API_KEY no configurado.")
        # HTTP Basic: usuario = api_key, password vacío
        creds = base64.b64encode(f"{self._api_key}:".encode("utf-8")).decode("ascii")
        return {
            "Authorization": f"Basic {creds}",
            "Accept": f"application/vnd.conekta-v{CONEKTA_API_VERSION}+json",
            "Content-Type": "application/json",
            "Accept-Language": "es",
        }

    def _require_key(self) -> None:
        if not self._api_key:
            raise ConfigError(
                "CONEKTA_API_KEY no configurado — usar PLUGINS_MX_MOCK=1 para forzar mock."
            )

    # ---------- orders ----------

    async def create_order(self, order: dict[str, Any]) -> dict[str, Any]:
        """Crea una orden con line items y opcionalmente charges asociados.

        Payload típico:
            {
              "line_items": [{"name": "Producto", "unit_price": 50000, "quantity": 2}],
              "currency": "MXN",
              "customer_info": {"name": "Juan", "email": "juan@x.com", "phone": "+52..."},
              "charges": [{"payment_method": {"type": "oxxo_cash", "expires_at": 1234567890}}]
            }

        ⚠ Los precios en Conekta son ENTEROS en centavos. $500.00 MXN = 50000.
        """
        if self._mock_mode:
            response = self._mock_order(order)
            self._bitacora.log(
                "create_order",
                success=True,
                params_summary={
                    "line_items_count": len(order.get("line_items", [])),
                    "currency": order.get("currency", "MXN"),
                    "email_hash": Bitacora.hash_sensitive(
                        (order.get("customer_info") or {}).get("email")
                    ),
                    "mode": "mock",
                },
                result_summary={"order_id": response["id"], "status": response["payment_status"]},
            )
            return response

        self._require_key()
        url = f"{CONEKTA_BASE_URL}/orders"
        start = _now_ms()
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.post(url, headers=self._headers(), json=order)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            err = handle_httpx_error(exc)
            self._bitacora.log(
                "create_order",
                success=False,
                duration_ms=_now_ms() - start,
                error={"code": err.code, "message": err.message},
            )
            raise err from exc

        self._bitacora.log(
            "create_order",
            success=True,
            duration_ms=_now_ms() - start,
            params_summary={
                "line_items_count": len(order.get("line_items", [])),
                "currency": order.get("currency", "MXN"),
                "email_hash": Bitacora.hash_sensitive(
                    (order.get("customer_info") or {}).get("email")
                ),
            },
            result_summary={
                "order_id": body.get("id"),
                "status": body.get("payment_status"),
            },
        )
        return {**body, "simulated": False}

    async def get_order(self, order_id: str) -> dict[str, Any]:
        """Lee una orden. Cache 2 min porque status puede cambiar."""
        cache_key = f"order_{order_id}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        if self._mock_mode:
            response = mark_simulated(self._mock_order_fetch(order_id))
            self._cache.set(cache_key, response, ttl_minutes=2)
            return response

        self._require_key()
        url = f"{CONEKTA_BASE_URL}/orders/{order_id}"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=self._headers())
                if resp.status_code == 404:
                    raise NotFoundError(f"Orden {order_id} no encontrada.")
                resp.raise_for_status()
                body = resp.json()
        except McpError:
            raise
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        response = {**body, "simulated": False}
        self._cache.set(cache_key, response, ttl_minutes=2)
        return response

    async def list_orders(
        self,
        limit: int = 25,
        next_id: str | None = None,
        payment_status: str | None = None,
    ) -> dict[str, Any]:
        """Lista órdenes con paginación cursor-based (Conekta usa `next`/`previous`)."""
        if self._mock_mode:
            return mark_simulated(
                {
                    "data": [],
                    "has_more": False,
                    "next_page_url": None,
                    "filters_applied": {
                        "payment_status": payment_status,
                        "limit": limit,
                    },
                },
                note="Búsqueda simulada — no devuelve órdenes reales.",
            )

        self._require_key()
        params: dict[str, Any] = {"limit": str(limit)}
        if next_id:
            params["next"] = next_id
        if payment_status:
            params["payment_status"] = payment_status
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(
                    f"{CONEKTA_BASE_URL}/orders",
                    headers=self._headers(),
                    params=params,
                )
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
        return {**body, "simulated": False}

    # ---------- charges ----------

    async def create_charge_on_order(
        self,
        order_id: str,
        charge: dict[str, Any],
    ) -> dict[str, Any]:
        """Crea un charge sobre una orden existente.

        Payload típico de charge:
            {"payment_method": {"type": "oxxo_cash", "expires_at": <unix>}}
            o {"payment_method": {"type": "card", "token_id": "tok_xxx"}}
            o {"payment_method": {"type": "spei"}}
        """
        if self._mock_mode:
            response = self._mock_charge(order_id, charge)
            self._bitacora.log(
                "create_charge_on_order",
                success=True,
                params_summary={
                    "order_id_hash": Bitacora.hash_sensitive(order_id),
                    "payment_type": (charge.get("payment_method") or {}).get("type"),
                    "mode": "mock",
                },
                result_summary={"charge_id": response["id"], "status": response["status"]},
            )
            return response

        self._require_key()
        url = f"{CONEKTA_BASE_URL}/orders/{order_id}/charges"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.post(url, headers=self._headers(), json=charge)
                if resp.status_code == 404:
                    raise NotFoundError(f"Orden {order_id} no encontrada.")
                resp.raise_for_status()
                body = resp.json()
        except McpError:
            raise
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
        return {**body, "simulated": False}

    async def refund_charge(
        self,
        order_id: str,
        reason: str = "requested_by_client",
        amount: int | None = None,
    ) -> dict[str, Any]:
        """Refund total o parcial de una orden.

        Conekta refunda a nivel ORDEN, no charge individual.
        amount en centavos. None = refund total.
        """
        if self._mock_mode:
            response = mark_simulated(
                {
                    "id": f"refund_{secrets.token_hex(8)}",
                    "order_id": order_id,
                    "amount": amount,
                    "reason": reason,
                    "status": "refunded",
                    "created_at": _now_iso(),
                }
            )
            self._bitacora.log(
                "refund_charge",
                success=True,
                params_summary={
                    "order_id_hash": Bitacora.hash_sensitive(order_id),
                    "is_partial": amount is not None,
                    "reason": reason,
                    "mode": "mock",
                },
                result_summary={"refund_id": response["id"], "status": response["status"]},
            )
            return response

        self._require_key()
        url = f"{CONEKTA_BASE_URL}/orders/{order_id}/refunds"
        body_data: dict[str, Any] = {"reason": reason}
        if amount is not None:
            body_data["amount"] = amount
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.post(url, headers=self._headers(), json=body_data)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
        return {**body, "simulated": False}

    # ---------- customers ----------

    async def create_customer(self, customer: dict[str, Any]) -> dict[str, Any]:
        """Crea un cliente. Mínimos: name, email, phone."""
        if self._mock_mode:
            return mark_simulated(self._mock_customer(customer))

        self._require_key()
        url = f"{CONEKTA_BASE_URL}/customers"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.post(url, headers=self._headers(), json=customer)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
        return {**body, "simulated": False}

    async def get_customer(self, customer_id: str) -> dict[str, Any]:
        cache_key = f"customer_{customer_id}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        if self._mock_mode:
            response = mark_simulated(self._mock_customer_fetch(customer_id))
            self._cache.set(cache_key, response, ttl_minutes=15)
            return response

        self._require_key()
        url = f"{CONEKTA_BASE_URL}/customers/{customer_id}"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=self._headers())
                if resp.status_code == 404:
                    raise NotFoundError(f"Customer {customer_id} no encontrado.")
                resp.raise_for_status()
                body = resp.json()
        except McpError:
            raise
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        response = {**body, "simulated": False}
        self._cache.set(cache_key, response, ttl_minutes=15)
        return response

    # ---------- payment links (Conekta Checkout) ----------

    async def create_payment_link(
        self,
        name: str,
        amount: int,
        currency: str = "MXN",
        expires_at: int | None = None,
        allowed_payment_methods: list[str] | None = None,
        success_url: str | None = None,
        failure_url: str | None = None,
    ) -> dict[str, Any]:
        """Crea un Checkout Link (orden + URL hospedada por Conekta).

        amount en centavos. methods válidos: ["card", "cash", "bank_transfer"].
        """
        if self._mock_mode:
            return mark_simulated(self._mock_payment_link(name, amount, currency))

        self._require_key()
        payload: dict[str, Any] = {
            "name": name,
            "type": "PaymentLink",
            "recurrent": False,
            "needs_shipping_contact": False,
            "order_template": {
                "currency": currency,
                "line_items": [
                    {"name": name, "unit_price": amount, "quantity": 1}
                ],
            },
            "allowed_payment_methods": allowed_payment_methods
            or ["card", "cash", "bank_transfer"],
        }
        if expires_at:
            payload["expires_at"] = expires_at
        if success_url:
            payload["success_url"] = success_url
        if failure_url:
            payload["failure_url"] = failure_url

        url = f"{CONEKTA_BASE_URL}/checkouts"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.post(url, headers=self._headers(), json=payload)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
        return {**body, "simulated": False}

    # ---------- subscriptions ----------

    async def subscription_create(
        self,
        customer_id: str,
        plan_id: str,
        card_id: str | None = None,
    ) -> dict[str, Any]:
        """Crea una suscripción del customer a un plan."""
        if self._mock_mode:
            return mark_simulated(
                {
                    "id": f"sub_{secrets.token_hex(8)}",
                    "customer_id": customer_id,
                    "plan_id": plan_id,
                    "card_id": card_id,
                    "status": "active",
                    "created_at": _now_iso(),
                    "billing_cycle_start": _now_iso(),
                }
            )

        self._require_key()
        body_data: dict[str, Any] = {"plan_id": plan_id}
        if card_id:
            body_data["card_id"] = card_id
        url = f"{CONEKTA_BASE_URL}/customers/{customer_id}/subscription"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.post(url, headers=self._headers(), json=body_data)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
        return {**body, "simulated": False}

    async def subscription_update(
        self,
        customer_id: str,
        plan_id: str | None = None,
        card_id: str | None = None,
    ) -> dict[str, Any]:
        """Update suscripción (cambio de plan o tarjeta)."""
        if self._mock_mode:
            return mark_simulated(
                {
                    "id": f"sub_{secrets.token_hex(8)}",
                    "customer_id": customer_id,
                    "plan_id": plan_id or "plan_existing",
                    "card_id": card_id,
                    "status": "active",
                    "updated_at": _now_iso(),
                }
            )

        self._require_key()
        body_data: dict[str, Any] = {}
        if plan_id:
            body_data["plan_id"] = plan_id
        if card_id:
            body_data["card_id"] = card_id
        url = f"{CONEKTA_BASE_URL}/customers/{customer_id}/subscription"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.put(url, headers=self._headers(), json=body_data)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
        return {**body, "simulated": False}

    async def subscription_cancel(self, customer_id: str) -> dict[str, Any]:
        """Cancela suscripción activa del customer."""
        if self._mock_mode:
            return mark_simulated(
                {
                    "id": f"sub_{secrets.token_hex(8)}",
                    "customer_id": customer_id,
                    "status": "canceled",
                    "canceled_at": _now_iso(),
                }
            )

        self._require_key()
        url = f"{CONEKTA_BASE_URL}/customers/{customer_id}/subscription/cancel"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.post(url, headers=self._headers())
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
        return {**body, "simulated": False}

    # ---------- mock helpers ----------

    def _mock_order(self, order: dict[str, Any]) -> dict[str, Any]:
        order_id = f"ord_{secrets.token_hex(8)}"
        total_centavos = sum(
            (it.get("unit_price", 0) * it.get("quantity", 1))
            for it in order.get("line_items", [])
        )
        return mark_simulated(
            {
                "id": order_id,
                "object": "order",
                "currency": order.get("currency", "MXN"),
                "payment_status": "pending_payment",
                "amount": total_centavos,
                "amount_refunded": 0,
                "created_at": _now_iso(),
                "updated_at": _now_iso(),
                "customer_info": order.get("customer_info"),
                "line_items": {"data": order.get("line_items", [])},
                "charges": {"data": []},
                "livemode": False,
            }
        )

    def _mock_order_fetch(self, order_id: str) -> dict[str, Any]:
        return {
            "id": order_id,
            "object": "order",
            "currency": "MXN",
            "payment_status": "pending_payment",
            "amount": 50000,
            "amount_refunded": 0,
            "created_at": _now_iso(),
            "livemode": False,
        }

    def _mock_charge(self, order_id: str, charge: dict[str, Any]) -> dict[str, Any]:
        payment_type = (charge.get("payment_method") or {}).get("type", "card")
        # Para offline (OXXO/SPEI) status pending_payment con referencia
        if payment_type in {"oxxo_cash", "spei", "cashi"}:
            return mark_simulated(
                {
                    "id": f"charge_{secrets.token_hex(8)}",
                    "object": "charge",
                    "status": "pending_payment",
                    "order_id": order_id,
                    "payment_method": {
                        "object": "payment_method",
                        "type": payment_type,
                        "reference": "9320" + secrets.token_hex(7).upper(),
                        "expires_at": int(
                            (datetime.now(timezone.utc) + timedelta(days=3)).timestamp()
                        ),
                    },
                    "created_at": _now_iso(),
                    "livemode": False,
                }
            )
        # Para card: paid mock inmediato
        return mark_simulated(
            {
                "id": f"charge_{secrets.token_hex(8)}",
                "object": "charge",
                "status": "paid",
                "order_id": order_id,
                "payment_method": {
                    "object": "payment_method",
                    "type": "card",
                    "last4": "4242",
                    "brand": "visa",
                },
                "paid_at": _now_iso(),
                "created_at": _now_iso(),
                "livemode": False,
            }
        )

    def _mock_customer(self, customer: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": f"cus_{secrets.token_hex(8)}",
            "object": "customer",
            "name": customer.get("name"),
            "email": customer.get("email"),
            "phone": customer.get("phone"),
            "created_at": _now_iso(),
            "livemode": False,
        }

    def _mock_customer_fetch(self, customer_id: str) -> dict[str, Any]:
        return {
            "id": customer_id,
            "object": "customer",
            "name": "Cliente Demo",
            "email": "demo@example.mx",
            "phone": "+525512345678",
            "created_at": _now_iso(),
            "livemode": False,
        }

    def _mock_payment_link(self, name: str, amount: int, currency: str) -> dict[str, Any]:
        checkout_id = f"chk_{secrets.token_hex(8)}"
        return {
            "id": checkout_id,
            "object": "checkout",
            "name": name,
            "type": "PaymentLink",
            "url": f"https://pay.conekta.com/link/{checkout_id}",
            "amount": amount,
            "currency": currency,
            "status": "Issued",
            "created_at": _now_iso(),
            "expires_at": int(
                (datetime.now(timezone.utc) + timedelta(days=30)).timestamp()
            ),
        }
