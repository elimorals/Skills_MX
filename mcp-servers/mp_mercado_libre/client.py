"""Async client for Mercado Libre REST API.

Endpoints used:
- GET /users/me                         — identify the seller
- GET /users/{seller_id}/items/search   — list seller's items
- GET /items/{item_id}                  — item detail
- PUT /items/{item_id}                  — update item (price, stock, status)
- GET /orders/search                    — list orders by seller
- GET /orders/{order_id}                — order detail
- GET /messages/packs/{pack_id}/sellers/{seller_id}   — messages in a pack
- POST /messages/packs/{pack_id}/sellers/{seller_id}  — send a message
- GET /questions/search                 — questions on listings
- POST /answers                         — answer a question
- GET /users/{seller_id}/reputation     — seller reputation

Rate limits: ~5000 req/hour per app. Pagination via limit + offset.

Mock mode (no app/secret/refresh) produces plausible deterministic responses.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_mercado_libre.auth import MeliTokenManager  # noqa: E402
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

NAMESPACE = "mercadolibre_mcp"
ML_BASE_URL = "https://api.mercadolibre.com"
REQUEST_TIMEOUT_S = 20.0


class MercadoLibreClient:
    """Async client over Mercado Libre API with OAuth refresh + cache + mock."""

    def __init__(
        self,
        app_id: str | None = None,
        secret: str | None = None,
        refresh_token: str | None = None,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        # Resolve credentials from env if not given explicitly
        explicit = any(v is not None for v in (app_id, secret, refresh_token))

        if app_id is None:
            app_id = os.environ.get("ML_APP_ID") or None
        if secret is None:
            secret = os.environ.get("ML_SECRET") or None
        if refresh_token is None:
            refresh_token = os.environ.get("ML_REFRESH_TOKEN") or None

        self._app_id = app_id
        self._secret = secret
        self._refresh_token = refresh_token
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

        # Mock decision
        if os.environ.get("PLUGINS_MX_MOCK") == "1":
            self._mock_mode = True
        elif explicit or (app_id and secret and refresh_token):
            self._mock_mode = False
        else:
            self._mock_mode = is_mock_mode(["ML_APP_ID", "ML_REFRESH_TOKEN"])

        # Lazily build the token manager only when needed (avoids ConfigError in mock)
        self._token_manager: MeliTokenManager | None = None

    @property
    def is_mock(self) -> bool:
        return self._mock_mode

    def _ensure_token_manager(self) -> MeliTokenManager:
        if self._token_manager is None:
            if not (self._app_id and self._secret and self._refresh_token):
                raise ConfigError(
                    "Mercado Libre: configura ML_APP_ID, ML_SECRET y ML_REFRESH_TOKEN. "
                    "Registra la app en https://developers.mercadolibre.com.mx y obtén el "
                    "refresh_token vía el flujo OAuth authorize.",
                )
            # Use a short hash of the refresh_token as cache prefix so multiple
            # sellers can coexist without overwriting each other's access_token.
            prefix = hashlib.sha256(self._refresh_token.encode()).hexdigest()[:8]
            self._token_manager = MeliTokenManager(
                app_id=self._app_id,
                secret=self._secret,
                refresh_token=self._refresh_token,
                cache=self._cache,
                cache_key_prefix=prefix,
            )
        return self._token_manager

    async def _auth_headers(self) -> dict[str, str]:
        tm = self._ensure_token_manager()
        token = await tm.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

    # ---------- seller ----------

    async def get_me(self) -> dict[str, Any]:
        """Identify the seller (whose refresh_token we hold)."""
        cache_key = "me"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        if self._mock_mode:
            response = mark_simulated(
                {
                    "id": 999999999,
                    "nickname": "MOCK_SELLER",
                    "site_id": "MLM",
                    "country_id": "MX",
                    "email": "mock-seller@example.com",
                }
            )
            self._cache.set(cache_key, response, ttl_hours=24)
            return response

        headers = await self._auth_headers()
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(f"{ML_BASE_URL}/users/me", headers=headers)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        response = {**body, "simulated": False}
        self._cache.set(cache_key, response, ttl_hours=24)
        return response

    # ---------- items ----------

    async def list_items(
        self,
        seller_id: int | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List the seller's items. Pagination via limit + offset."""
        if self._mock_mode:
            return self._mock_list_items(seller_id, status, limit, offset)

        sid = seller_id if seller_id is not None else (await self.get_me())["id"]
        url = f"{ML_BASE_URL}/users/{sid}/items/search"
        params: dict[str, Any] = {"limit": str(limit), "offset": str(offset)}
        if status:
            params["status"] = status

        headers = await self._auth_headers()
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=headers, params=params)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        return {**body, "simulated": False}

    async def get_item(self, item_id: str) -> dict[str, Any]:
        """Get full detail of a single item. Cache 5 min (prices change)."""
        cache_key = f"item_{item_id}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        if self._mock_mode:
            response = self._mock_item(item_id)
            self._cache.set(cache_key, response, ttl_minutes=5)
            return response

        headers = await self._auth_headers()
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(f"{ML_BASE_URL}/items/{item_id}", headers=headers)
                if resp.status_code == 404:
                    raise NotFoundError(f"Item {item_id} no encontrado.")
                resp.raise_for_status()
                body = resp.json()
        except McpError:
            raise
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        response = {**body, "simulated": False}
        self._cache.set(cache_key, response, ttl_minutes=5)
        return response

    async def update_item(self, item_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        """Update a subset of fields on an item.

        Commonly used keys: price, available_quantity, status, condition.
        ML uses PUT for partial updates here.
        """
        if not fields:
            raise UpstreamError("update_item called without any fields to change.")

        if self._mock_mode:
            response = mark_simulated(
                {
                    "id": item_id,
                    "updated_fields": list(fields.keys()),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    **fields,
                }
            )
            self._bitacora.log(
                "update_item",
                success=True,
                params_summary={
                    "item_id_hash": Bitacora.hash_sensitive(item_id),
                    "fields": list(fields.keys()),
                    "mode": "mock",
                },
            )
            # Invalidate cache for this item
            self._cache.invalidate(f"item_{item_id}")
            return response

        headers = await self._auth_headers()
        headers["Content-Type"] = "application/json"

        start = _now_ms()
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.put(
                    f"{ML_BASE_URL}/items/{item_id}",
                    headers=headers,
                    json=fields,
                )
                if resp.status_code == 404:
                    raise NotFoundError(f"Item {item_id} no encontrado.")
                resp.raise_for_status()
                body = resp.json()
        except McpError:
            raise
        except Exception as exc:
            err = handle_httpx_error(exc)
            self._bitacora.log(
                "update_item",
                success=False,
                duration_ms=_now_ms() - start,
                params_summary={
                    "item_id_hash": Bitacora.hash_sensitive(item_id),
                    "fields": list(fields.keys()),
                },
                error={"code": err.code, "message": err.message},
            )
            raise err from exc

        self._cache.invalidate(f"item_{item_id}")
        self._bitacora.log(
            "update_item",
            success=True,
            duration_ms=_now_ms() - start,
            params_summary={
                "item_id_hash": Bitacora.hash_sensitive(item_id),
                "fields": list(fields.keys()),
            },
        )
        return {**body, "simulated": False}

    # ---------- orders ----------

    async def list_orders(
        self,
        seller_id: int | None = None,
        status: str | None = None,
        fecha_desde: str | None = None,
        fecha_hasta: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Search orders for the seller."""
        if self._mock_mode:
            return self._mock_list_orders(status, limit, offset)

        sid = seller_id if seller_id is not None else (await self.get_me())["id"]
        url = f"{ML_BASE_URL}/orders/search"
        params: dict[str, Any] = {
            "seller": str(sid),
            "limit": str(limit),
            "offset": str(offset),
        }
        if status:
            params["order.status"] = status
        if fecha_desde:
            params["order.date_created.from"] = fecha_desde
        if fecha_hasta:
            params["order.date_created.to"] = fecha_hasta

        headers = await self._auth_headers()
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=headers, params=params)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        return {**body, "simulated": False}

    async def get_order(self, order_id: int | str) -> dict[str, Any]:
        """Order detail. Cache 2 min (status can change)."""
        cache_key = f"order_{order_id}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        if self._mock_mode:
            response = self._mock_order(str(order_id))
            self._cache.set(cache_key, response, ttl_minutes=2)
            return response

        headers = await self._auth_headers()
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(
                    f"{ML_BASE_URL}/orders/{order_id}", headers=headers
                )
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

    # ---------- messages ----------

    async def list_messages(
        self,
        pack_id: str,
        seller_id: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List messages in a post-sale conversation."""
        if self._mock_mode:
            return mark_simulated(
                {
                    "messages": [],
                    "paging": {"total": 0, "limit": limit, "offset": offset},
                    "pack_id": pack_id,
                }
            )

        sid = seller_id if seller_id is not None else (await self.get_me())["id"]
        url = f"{ML_BASE_URL}/messages/packs/{pack_id}/sellers/{sid}"
        headers = await self._auth_headers()
        params = {"limit": str(limit), "offset": str(offset)}
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=headers, params=params)
                if resp.status_code == 404:
                    raise NotFoundError(f"Pack {pack_id} no encontrado.")
                resp.raise_for_status()
                body = resp.json()
        except McpError:
            raise
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        return {**body, "simulated": False}

    async def send_message(
        self,
        pack_id: str,
        buyer_id: int,
        text: str,
        seller_id: int | None = None,
    ) -> dict[str, Any]:
        """Send a message to the buyer in a pack."""
        if self._mock_mode:
            response = mark_simulated(
                {
                    "id": "mock-msg-id",
                    "pack_id": pack_id,
                    "from": {"user_id": seller_id or 999999999},
                    "to": {"user_id": buyer_id},
                    "text": text,
                    "date_created": datetime.now(timezone.utc).isoformat(),
                }
            )
            self._bitacora.log(
                "send_message",
                success=True,
                params_summary={
                    "pack_id_hash": Bitacora.hash_sensitive(pack_id),
                    "buyer_id_hash": Bitacora.hash_sensitive(str(buyer_id)),
                    "text_len": len(text),
                    "mode": "mock",
                },
            )
            return response

        sid = seller_id if seller_id is not None else (await self.get_me())["id"]
        url = f"{ML_BASE_URL}/messages/packs/{pack_id}/sellers/{sid}"
        headers = await self._auth_headers()
        headers["Content-Type"] = "application/json"
        payload = {"from": {"user_id": sid}, "to": {"user_id": buyer_id}, "text": text}

        start = _now_ms()
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            err = handle_httpx_error(exc)
            self._bitacora.log(
                "send_message",
                success=False,
                duration_ms=_now_ms() - start,
                error={"code": err.code, "message": err.message},
            )
            raise err from exc

        self._bitacora.log(
            "send_message",
            success=True,
            duration_ms=_now_ms() - start,
            params_summary={
                "pack_id_hash": Bitacora.hash_sensitive(pack_id),
                "buyer_id_hash": Bitacora.hash_sensitive(str(buyer_id)),
                "text_len": len(text),
            },
        )
        return {**body, "simulated": False}

    # ---------- questions ----------

    async def list_questions(
        self,
        item_id: str | None = None,
        status: str = "UNANSWERED",
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List pre-sale questions on the seller's items."""
        if self._mock_mode:
            return mark_simulated(
                {
                    "questions": [],
                    "total": 0,
                    "limit": limit,
                    "offset": offset,
                    "filters_applied": {"item_id": item_id, "status": status},
                }
            )

        url = f"{ML_BASE_URL}/questions/search"
        headers = await self._auth_headers()
        params: dict[str, Any] = {
            "status": status,
            "limit": str(limit),
            "offset": str(offset),
        }
        if item_id:
            params["item"] = item_id

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=headers, params=params)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        return {**body, "simulated": False}

    async def answer_question(self, question_id: int | str, text: str) -> dict[str, Any]:
        """Answer a pre-sale question."""
        if self._mock_mode:
            response = mark_simulated(
                {
                    "id": question_id,
                    "text": "(question)",
                    "status": "ANSWERED",
                    "answer": {
                        "text": text,
                        "date_created": datetime.now(timezone.utc).isoformat(),
                        "status": "ACTIVE",
                    },
                }
            )
            self._bitacora.log(
                "answer_question",
                success=True,
                params_summary={
                    "question_id_hash": Bitacora.hash_sensitive(str(question_id)),
                    "text_len": len(text),
                    "mode": "mock",
                },
            )
            return response

        url = f"{ML_BASE_URL}/answers"
        headers = await self._auth_headers()
        headers["Content-Type"] = "application/json"
        payload = {"question_id": question_id, "text": text}

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        return {**body, "simulated": False}

    # ---------- metrics ----------

    async def get_seller_reputation(self, seller_id: int | None = None) -> dict[str, Any]:
        """Get seller's reputation (level, transactions, claims, etc.). Cache 30 min."""
        sid = seller_id if seller_id is not None else None
        cache_key = f"reputation_{sid or 'me'}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        if self._mock_mode:
            response = mark_simulated(
                {
                    "level_id": "5_green",
                    "power_seller_status": "platinum",
                    "transactions": {
                        "total": 1234,
                        "completed": 1200,
                        "canceled": 30,
                        "ratings": {"positive": 0.98, "negative": 0.01, "neutral": 0.01},
                    },
                    "metrics": {
                        "claims": {"rate": 0.005},
                        "delayed_handling_time": {"rate": 0.01},
                        "cancellations": {"rate": 0.025},
                    },
                }
            )
            self._cache.set(cache_key, response, ttl_minutes=30)
            return response

        if sid is None:
            sid = (await self.get_me())["id"]
        url = f"{ML_BASE_URL}/users/{sid}/reputation"
        headers = await self._auth_headers()
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        response = {**body, "simulated": False}
        self._cache.set(cache_key, response, ttl_minutes=30)
        return response

    # ---------- mock helpers ----------

    @staticmethod
    def _mock_list_items(
        seller_id: int | None,
        status: str | None,
        limit: int,
        offset: int,
    ) -> dict[str, Any]:
        items = [
            {
                "id": f"MLM{i:010d}",
                "title": f"Producto Mock {i}",
                "price": 100.0 + i * 10,
                "available_quantity": 10,
                "status": status or "active",
                "permalink": f"https://articulo.mercadolibre.com.mx/MLM-{i:010d}",
            }
            for i in range(offset, min(offset + limit, offset + 3))
        ]
        return mark_simulated(
            {
                "seller_id": seller_id or 999999999,
                "results": [item["id"] for item in items],
                "paging": {"total": 3, "limit": limit, "offset": offset},
                "items_preview": items,
            }
        )

    @staticmethod
    def _mock_item(item_id: str) -> dict[str, Any]:
        # Status determinístico: terminado con dígito par → paused, impar → active
        last = item_id[-1] if item_id else "0"
        if last.isdigit():
            status = "active" if int(last) % 2 == 1 else "paused"
        else:
            status = "active"
        # Numeric tail as seed for price/stock so different ids produce different data
        tail_digits = "".join(c for c in item_id if c.isdigit())[-3:] or "0"
        seed = int(tail_digits)

        return mark_simulated(
            {
                "id": item_id,
                "title": f"Producto Mock {item_id}",
                "category_id": "MLM5726",
                "price": 100.0 + seed,
                "currency_id": "MXN",
                "available_quantity": 10 + (seed % 50),
                "sold_quantity": seed % 20,
                "status": status,
                "condition": "new",
                "permalink": f"https://articulo.mercadolibre.com.mx/{item_id}",
                "thumbnail": "https://mock.example/thumb.jpg",
                "shipping": {"mode": "me2", "free_shipping": True},
            }
        )

    @staticmethod
    def _mock_list_orders(
        status: str | None, limit: int, offset: int
    ) -> dict[str, Any]:
        return mark_simulated(
            {
                "results": [],
                "paging": {"total": 0, "limit": limit, "offset": offset},
                "filters_applied": {"status": status},
            }
        )

    @staticmethod
    def _mock_order(order_id: str) -> dict[str, Any]:
        # Status determinístico parecido a mp_mercado_pago
        if order_id == "cancelled":
            status = "cancelled"
        elif order_id.isdigit() and int(order_id) % 2 == 0:
            status = "payment_required"
        else:
            status = "paid"

        return mark_simulated(
            {
                "id": order_id if not order_id.isdigit() else int(order_id),
                "status": status,
                "date_created": datetime.now(timezone.utc).isoformat(),
                "date_closed": datetime.now(timezone.utc).isoformat()
                if status == "paid"
                else None,
                "total_amount": 250.0,
                "currency_id": "MXN",
                "buyer": {"id": 1111111, "nickname": "MOCKBUYER"},
                "order_items": [
                    {
                        "item": {"id": "MLM0000000001", "title": "Producto mock"},
                        "quantity": 1,
                        "unit_price": 250.0,
                    }
                ],
                "shipping": {"id": int(order_id) * 7 if order_id.isdigit() else 0},
            }
        )


def _now_ms() -> float:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return loop.time() * 1000
    except RuntimeError:
        pass
    return 0.0
