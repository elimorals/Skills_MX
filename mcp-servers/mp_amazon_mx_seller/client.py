"""Cliente Amazon MX Selling Partner API.

Auth real: LWA refresh token → access token + AWS Signature V4.
Mock-first sin AMAZON_SP_REFRESH_TOKEN.

⚠ Path real es complejo (~80-120h desarrollo). Implementación HTTP completa
fuera del alcance default. El skeleton aquí soporta mock.
"""

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


NAMESPACE = "amazon_mx_seller_mcp"
SP_API_BASE = "https://sellingpartnerapi-na.amazon.com"  # NA region incluye MX
REQUEST_TIMEOUT_S = 30.0


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AmazonMxSellerClient:
    def __init__(
        self,
        refresh_token: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        explicit = refresh_token is not None
        if refresh_token is None:
            refresh_token = os.environ.get("AMAZON_SP_REFRESH_TOKEN", "").strip() or None
        if client_id is None:
            client_id = os.environ.get("AMAZON_SP_CLIENT_ID", "").strip() or None
        if client_secret is None:
            client_secret = os.environ.get("AMAZON_SP_CLIENT_SECRET", "").strip() or None

        self._refresh_token = refresh_token
        self._client_id = client_id
        self._client_secret = client_secret

        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

        if os.environ.get("PLUGINS_MX_MOCK") == "1":
            self._mock = True
        elif explicit or refresh_token:
            self._mock = False
        else:
            self._mock = is_mock_mode([
                "AMAZON_SP_REFRESH_TOKEN",
                "AMAZON_SP_CLIENT_ID",
            ])

    @property
    def is_mock(self) -> bool:
        return self._mock

    def _require_creds(self) -> None:
        if not (self._refresh_token and self._client_id and self._client_secret):
            raise ConfigError(
                "Faltan AMAZON_SP_REFRESH_TOKEN + AMAZON_SP_CLIENT_ID + AMAZON_SP_CLIENT_SECRET"
            )

    def _log(self, op: str, params: dict[str, Any]) -> None:
        self._bitacora.log(op, success=True, params_summary=params)

    # ---------- tools (path real no implementado completamente) ----------

    async def list_listings(self, limit: int = 25, status: str | None = None) -> dict[str, Any]:
        self._log("list_listings", {"limit": limit, "status": status})

        if self._mock:
            return mark_simulated({
                "listings": [
                    {
                        "asin": f"B0{i:08d}MX",
                        "sku": f"SKU-DEMO-{i:03d}",
                        "title": f"Producto Demo {i}",
                        "status": "ACTIVE" if i % 3 != 0 else "INCOMPLETE",
                        "price_mxn": 199.00 * (i + 1),
                        "stock_quantity": 25 - i * 3,
                        "fulfillment_channel": "AFN" if i % 2 == 0 else "MFN",
                        "category": "electronics" if i % 2 == 0 else "home_kitchen",
                    }
                    for i in range(min(limit, 3))
                ],
                "total_count": 87,
            })

        self._require_creds()
        raise McpError(
            "Path real Amazon SP-API requiere implementación LWA + AWS Sig V4 (no implementado).",
            {"estado": "no_implementado", "esfuerzo_requerido": "~80-120h"},
        )

    async def get_listing(self, sku: str) -> dict[str, Any]:
        cache_key = f"listing_{sku}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("get_listing", {"sku": sku})

        if self._mock:
            r = mark_simulated({
                "sku": sku,
                "asin": "B0DEMO0001MX",
                "title": "Producto Demo MX",
                "status": "ACTIVE",
                "price_mxn": 499.00,
                "stock_quantity": 17,
                "fulfillment_channel": "AFN",
                "category": "electronics",
                "comision_amazon_porcentaje": 0.08,
                "comision_amazon_mxn": 39.92,
                "fba_fee_mxn": 55.00,
                "neto_estimado_mxn": 404.08,
                "rating_promedio": 4.5,
                "reviews_count": 47,
                "updated_at": _now_iso(),
            })
            self._cache.set(cache_key, r, ttl_minutes=10)
            return r

        self._require_creds()
        raise McpError("Path real Amazon SP-API no implementado.", {"estado": "no_implementado"})

    async def update_inventory(self, sku: str, quantity: int) -> dict[str, Any]:
        self._log("update_inventory", {"sku": sku, "quantity": quantity})

        if self._mock:
            return mark_simulated({
                "sku": sku,
                "previous_quantity": 17,
                "new_quantity": quantity,
                "status": "updated",
                "updated_at": _now_iso(),
            })

        self._require_creds()
        raise McpError("Path real Amazon SP-API no implementado.", {"estado": "no_implementado"})

    async def list_orders(
        self, limit: int = 25, status: str | None = None
    ) -> dict[str, Any]:
        self._log("list_orders", {"limit": limit, "status": status})

        if self._mock:
            return mark_simulated({
                "orders": [
                    {
                        "amazon_order_id": f"701-{i:07d}-1234567",
                        "purchase_date": _now_iso(),
                        "order_status": "Unshipped" if i % 2 == 0 else "Shipped",
                        "fulfillment_channel": "AFN" if i % 3 == 0 else "MFN",
                        "items_count": 1 + (i % 3),
                        "total_mxn": 1500.00 * (i + 1),
                    }
                    for i in range(min(limit, 3))
                ],
                "total_count": 145,
            })

        self._require_creds()
        raise McpError("Path real Amazon SP-API no implementado.", {"estado": "no_implementado"})

    async def get_order(self, amazon_order_id: str) -> dict[str, Any]:
        cache_key = f"order_{amazon_order_id}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("get_order", {"amazon_order_id": amazon_order_id})

        if self._mock:
            r = mark_simulated({
                "amazon_order_id": amazon_order_id,
                "purchase_date": _now_iso(),
                "order_status": "Unshipped",
                "fulfillment_channel": "MFN",
                "items": [
                    {"sku": "SKU-DEMO-001", "quantity": 2, "price_mxn": 250.00},
                ],
                "subtotal_mxn": 500.00,
                "tax_mxn": 80.00,
                "shipping_mxn": 50.00,
                "total_mxn": 630.00,
                "buyer_info_redacted": True,
                "ship_address": {"city": "CDMX", "postal_code": "06700"},
            })
            self._cache.set(cache_key, r, ttl_minutes=5)
            return r

        self._require_creds()
        raise McpError("Path real Amazon SP-API no implementado.", {"estado": "no_implementado"})

    async def get_fees_estimate(self, sku: str, price_mxn: float) -> dict[str, Any]:
        """Estima comisiones Amazon + FBA para un SKU al precio dado."""
        self._log("get_fees_estimate", {"sku": sku, "price_mxn": price_mxn})

        if self._mock:
            # 8% para electronics como demo
            commission = price_mxn * 0.08
            fba_fee = 55.00 if price_mxn < 1000 else 95.00
            return mark_simulated({
                "sku": sku,
                "price_mxn": price_mxn,
                "comision_referral_porcentaje": 0.08,
                "comision_referral_mxn": round(commission, 2),
                "fba_fulfillment_fee_mxn": fba_fee,
                "fba_storage_fee_estimado_mensual_mxn": 12.00,
                "total_fees_mxn": round(commission + fba_fee, 2),
                "neto_seller_mxn": round(price_mxn - commission - fba_fee, 2),
                "margen_seller_porcentaje": round(
                    (price_mxn - commission - fba_fee) / price_mxn, 4
                ),
            })

        self._require_creds()
        raise McpError("Path real no implementado.", {"estado": "no_implementado"})
