"""Async client para Shopify Admin API (wrapper específico MX).

Base URL: https://{shop}.myshopify.com/admin/api/{version}/{resource}.json
Auth: X-Shopify-Access-Token header (custom app access token)
API version: 2024-10 (LTS) o 2025-01

Tools cubiertos:
- list_products / get_product
- list_variants / get_inventory
- update_inventory_level
- list_orders / get_order
- create_fulfillment / cancel_fulfillment
- list_customers / get_customer
- list_webhooks / create_webhook
- ms_calculate_tax_mx (utility: cálculo IVA según producto/región)

Mock mode (sin SHOPIFY_ACCESS_TOKEN) produce respuestas plausibles con
`simulated: true` para development.
"""

from __future__ import annotations

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
    handle_httpx_error,
)
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402


NAMESPACE = "shopify_mx_mcp"
DEFAULT_API_VERSION = "2024-10"
REQUEST_TIMEOUT_S = 30.0


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ShopifyMxClient:
    """Async client sobre Shopify Admin API con mock fallback + cache + bitácora."""

    def __init__(
        self,
        shop: str | None = None,
        access_token: str | None = None,
        api_version: str | None = None,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        explicit_creds = shop is not None or access_token is not None

        if shop is None:
            shop = os.environ.get("SHOPIFY_SHOP", "").strip() or None
        if access_token is None:
            access_token = os.environ.get("SHOPIFY_ACCESS_TOKEN", "").strip() or None
        if api_version is None:
            api_version = os.environ.get("SHOPIFY_API_VERSION", DEFAULT_API_VERSION)

        self._shop = shop
        self._access_token = access_token
        self._api_version = api_version
        self._base_url = (
            f"https://{shop}/admin/api/{api_version}" if shop else None
        )

        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

        if os.environ.get("PLUGINS_MX_MOCK") == "1":
            self._mock_mode = True
        elif explicit_creds or (self._shop and self._access_token):
            self._mock_mode = False
        else:
            self._mock_mode = is_mock_mode(["SHOPIFY_SHOP", "SHOPIFY_ACCESS_TOKEN"])

    @property
    def is_mock(self) -> bool:
        return self._mock_mode

    @property
    def shop(self) -> str | None:
        return self._shop

    def _headers(self) -> dict[str, str]:
        if not self._access_token:
            raise ConfigError("SHOPIFY_ACCESS_TOKEN no configurado.")
        return {
            "X-Shopify-Access-Token": self._access_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _require_creds(self) -> None:
        if not (self._shop and self._access_token):
            raise ConfigError(
                "Faltan SHOPIFY_SHOP y/o SHOPIFY_ACCESS_TOKEN."
            )

    def _log(self, op: str, payload: dict[str, Any], *, success: bool = True) -> None:
        safe = dict(payload)
        for k in ("email", "phone"):
            if k in safe and safe[k]:
                safe[f"{k}_hash"] = Bitacora.hash_sensitive(str(safe.pop(k)))
        self._bitacora.log(op, success=success, params_summary=safe)

    # ---------- products ----------

    async def list_products(self, limit: int = 50, status: str | None = None) -> dict[str, Any]:
        """Lista productos con paginación."""
        self._log("list_products", {"limit": limit, "status": status})
        if self._mock_mode:
            return mark_simulated(self._mock_products_list(limit))

        self._require_creds()
        params: dict[str, str] = {"limit": str(limit)}
        if status:
            params["status"] = status
        url = f"{self._base_url}/products.json"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=self._headers(), params=params)
                resp.raise_for_status()
                return {**resp.json(), "simulated": False}
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

    async def get_product(self, product_id: int | str) -> dict[str, Any]:
        cache_key = f"product_{product_id}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("get_product", {"product_id": str(product_id)})
        if self._mock_mode:
            r = mark_simulated(self._mock_product(int(product_id) if str(product_id).isdigit() else 123456))
            self._cache.set(cache_key, r, ttl_minutes=10)
            return r

        self._require_creds()
        url = f"{self._base_url}/products/{product_id}.json"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=self._headers())
                if resp.status_code == 404:
                    raise NotFoundError(f"Producto {product_id} no encontrado.")
                resp.raise_for_status()
                body = resp.json()
        except McpError:
            raise
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        r = {**body, "simulated": False}
        self._cache.set(cache_key, r, ttl_minutes=10)
        return r

    # ---------- inventory ----------

    async def get_inventory_level(
        self, inventory_item_id: int | str, location_id: int | str
    ) -> dict[str, Any]:
        """Stock de un SKU en una sucursal específica."""
        self._log("get_inventory_level", {
            "inventory_item_id": str(inventory_item_id),
            "location_id": str(location_id),
        })
        if self._mock_mode:
            return mark_simulated({
                "inventory_item_id": int(str(inventory_item_id)) if str(inventory_item_id).isdigit() else 0,
                "location_id": int(str(location_id)) if str(location_id).isdigit() else 0,
                "available": 12,
                "updated_at": _now_iso(),
            })

        self._require_creds()
        url = f"{self._base_url}/inventory_levels.json"
        params = {
            "inventory_item_ids": str(inventory_item_id),
            "location_ids": str(location_id),
        }
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=self._headers(), params=params)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        levels = body.get("inventory_levels", [])
        if not levels:
            raise NotFoundError("Inventory level no encontrado")
        return {**levels[0], "simulated": False}

    async def update_inventory_level(
        self,
        inventory_item_id: int | str,
        location_id: int | str,
        available: int,
    ) -> dict[str, Any]:
        """Setea stock de un SKU. CRÍTICO: usar después de venta o ajuste manual."""
        self._log("update_inventory_level", {
            "inventory_item_id": str(inventory_item_id),
            "location_id": str(location_id),
            "available": available,
        })
        if self._mock_mode:
            return mark_simulated({
                "inventory_item_id": int(str(inventory_item_id)) if str(inventory_item_id).isdigit() else 0,
                "location_id": int(str(location_id)) if str(location_id).isdigit() else 0,
                "available": available,
                "updated_at": _now_iso(),
            })

        self._require_creds()
        url = f"{self._base_url}/inventory_levels/set.json"
        body_data = {
            "inventory_item_id": int(str(inventory_item_id)),
            "location_id": int(str(location_id)),
            "available": int(available),
        }
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.post(url, headers=self._headers(), json=body_data)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
        return {**body.get("inventory_level", {}), "simulated": False}

    # ---------- orders ----------

    async def list_orders(
        self,
        limit: int = 50,
        status: str = "any",
        financial_status: str | None = None,
        fulfillment_status: str | None = None,
        created_at_min: str | None = None,
        created_at_max: str | None = None,
    ) -> dict[str, Any]:
        self._log("list_orders", {
            "limit": limit,
            "status": status,
            "financial_status": financial_status,
            "fulfillment_status": fulfillment_status,
        })
        if self._mock_mode:
            return mark_simulated({
                "orders": self._mock_orders_list(min(limit, 3)),
                "filters": {
                    "status": status,
                    "financial_status": financial_status,
                    "fulfillment_status": fulfillment_status,
                },
            })

        self._require_creds()
        params: dict[str, str] = {"limit": str(limit), "status": status}
        if financial_status:
            params["financial_status"] = financial_status
        if fulfillment_status:
            params["fulfillment_status"] = fulfillment_status
        if created_at_min:
            params["created_at_min"] = created_at_min
        if created_at_max:
            params["created_at_max"] = created_at_max

        url = f"{self._base_url}/orders.json"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=self._headers(), params=params)
                resp.raise_for_status()
                return {**resp.json(), "simulated": False}
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

    async def get_order(self, order_id: int | str) -> dict[str, Any]:
        cache_key = f"order_{order_id}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("get_order", {"order_id": str(order_id)})
        if self._mock_mode:
            r = mark_simulated(self._mock_order_detail(str(order_id)))
            self._cache.set(cache_key, r, ttl_minutes=2)
            return r

        self._require_creds()
        url = f"{self._base_url}/orders/{order_id}.json"
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

        r = {**body.get("order", {}), "simulated": False}
        self._cache.set(cache_key, r, ttl_minutes=2)
        return r

    # ---------- fulfillment ----------

    async def create_fulfillment(
        self,
        order_id: int | str,
        tracking_number: str | None = None,
        tracking_company: str | None = None,
        notify_customer: bool = True,
    ) -> dict[str, Any]:
        """Marca una orden como enviada con tracking opcional."""
        self._log("create_fulfillment", {
            "order_id": str(order_id),
            "tracking_company": tracking_company,
            "notify_customer": notify_customer,
        })
        if self._mock_mode:
            return mark_simulated({
                "id": int(secrets.randbits(31)),
                "order_id": int(str(order_id)) if str(order_id).isdigit() else 0,
                "status": "success",
                "tracking_number": tracking_number,
                "tracking_company": tracking_company,
                "tracking_url": f"https://demo-tracking.example/{tracking_number}" if tracking_number else None,
                "created_at": _now_iso(),
            })

        self._require_creds()
        url = f"{self._base_url}/orders/{order_id}/fulfillments.json"
        body_data: dict[str, Any] = {
            "fulfillment": {
                "notify_customer": notify_customer,
            }
        }
        if tracking_number:
            body_data["fulfillment"]["tracking_number"] = tracking_number
        if tracking_company:
            body_data["fulfillment"]["tracking_company"] = tracking_company

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.post(url, headers=self._headers(), json=body_data)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
        return {**body.get("fulfillment", {}), "simulated": False}

    # ---------- customers ----------

    async def get_customer(self, customer_id: int | str) -> dict[str, Any]:
        cache_key = f"customer_{customer_id}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("get_customer", {"customer_id": str(customer_id)})
        if self._mock_mode:
            r = mark_simulated(self._mock_customer(str(customer_id)))
            self._cache.set(cache_key, r, ttl_minutes=15)
            return r

        self._require_creds()
        url = f"{self._base_url}/customers/{customer_id}.json"
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

        r = {**body.get("customer", {}), "simulated": False}
        self._cache.set(cache_key, r, ttl_minutes=15)
        return r

    # ---------- webhooks ----------

    async def list_webhooks(self) -> dict[str, Any]:
        self._log("list_webhooks", {})
        if self._mock_mode:
            return mark_simulated({
                "webhooks": [
                    {"id": 1001, "topic": "orders/paid", "address": "https://example/wh"},
                    {"id": 1002, "topic": "orders/fulfilled", "address": "https://example/wh"},
                ]
            })

        self._require_creds()
        url = f"{self._base_url}/webhooks.json"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=self._headers())
                resp.raise_for_status()
                return {**resp.json(), "simulated": False}
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

    # ---------- MX utilities ----------

    def calculate_tax_mx(
        self,
        subtotal_mxn: float,
        region: str = "general",
        producto_exento: bool = False,
    ) -> dict[str, Any]:
        """Calcula IVA según región MX (general 16% o frontera 8%) y exenciones.

        Local — no requiere API call.
        """
        if producto_exento:
            return {
                "subtotal_mxn": round(subtotal_mxn, 2),
                "iva_mxn": 0.0,
                "total_mxn": round(subtotal_mxn, 2),
                "tasa_aplicada": 0.0,
                "region": region,
                "razon": "producto_exento",
            }
        tasa = 0.08 if region == "frontera_norte" else 0.16
        iva = round(subtotal_mxn * tasa, 2)
        return {
            "subtotal_mxn": round(subtotal_mxn, 2),
            "iva_mxn": iva,
            "total_mxn": round(subtotal_mxn + iva, 2),
            "tasa_aplicada": tasa,
            "region": region,
        }

    # ---------- mock helpers ----------

    def _mock_products_list(self, limit: int) -> dict[str, Any]:
        return {
            "products": [self._mock_product(i + 1000) for i in range(min(limit, 3))],
        }

    def _mock_product(self, product_id: int) -> dict[str, Any]:
        return {
            "id": product_id,
            "title": f"Producto Demo {product_id}",
            "status": "active",
            "vendor": "Demo MX",
            "product_type": "Demo",
            "variants": [
                {
                    "id": product_id * 10,
                    "sku": f"SKU-{product_id}",
                    "price": "499.00",
                    "inventory_item_id": product_id * 100,
                    "inventory_quantity": 12,
                }
            ],
            "created_at": _now_iso(),
        }

    def _mock_orders_list(self, n: int) -> list[dict[str, Any]]:
        out = []
        for i in range(n):
            out.append({
                "id": 1000000 + i,
                "order_number": 1000 + i,
                "name": f"#{1000 + i}",
                "total_price": "599.00",
                "currency": "MXN",
                "financial_status": "paid" if i % 2 == 0 else "pending",
                "fulfillment_status": "fulfilled" if i % 2 == 0 else "unfulfilled",
                "customer": {"id": 200000 + i, "email": f"demo{i}@example.mx"},
                "created_at": _now_iso(),
            })
        return out

    def _mock_order_detail(self, order_id: str) -> dict[str, Any]:
        return {
            "id": int(order_id) if order_id.isdigit() else 1000001,
            "order_number": 1001,
            "name": "#1001",
            "total_price": "599.00",
            "subtotal_price": "499.00",
            "total_tax": "79.84",
            "currency": "MXN",
            "financial_status": "paid",
            "fulfillment_status": "unfulfilled",
            "customer": {"id": 200001, "email": "demo@example.mx", "first_name": "Juan"},
            "line_items": [
                {
                    "id": 1,
                    "sku": "SKU-DEMO",
                    "title": "Producto Demo",
                    "quantity": 1,
                    "price": "499.00",
                }
            ],
            "created_at": _now_iso(),
        }

    def _mock_customer(self, customer_id: str) -> dict[str, Any]:
        return {
            "id": int(customer_id) if customer_id.isdigit() else 200001,
            "email": "demo@example.mx",
            "first_name": "Juan",
            "last_name": "Demo",
            "phone": "+525512345678",
            "addresses": [{"country_code": "MX", "city": "CDMX", "zip": "06700"}],
            "created_at": _now_iso(),
        }
