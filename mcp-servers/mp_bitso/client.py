"""Async client para Bitso API (exchange cripto-fiat MX).

Endpoints públicos (sin auth):
- ticker, order_book, trades, available_books

Endpoints privados (HMAC auth):
- account_status, balance, fees, ledger
- open_orders, place_order, cancel_order
- fundings, withdrawals

Sandbox: https://stage.bitso.com (testnet)
Producción: https://api.bitso.com

Mock mode (sin BITSO_API_KEY) produce respuestas sintéticas plausibles.
"""

from __future__ import annotations

import json
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

from mp_bitso.auth import build_signature  # noqa: E402


NAMESPACE = "bitso_mcp"
BITSO_PROD_URL = "https://api.bitso.com"
BITSO_SANDBOX_URL = "https://stage.bitso.com"
REQUEST_TIMEOUT_S = 20.0


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class BitsoClient:
    """Async client sobre Bitso API con mock + cache + bitácora."""

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        environment: str | None = None,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        explicit_creds = api_key is not None or api_secret is not None
        if api_key is None:
            api_key = os.environ.get("BITSO_API_KEY", "").strip() or None
        if api_secret is None:
            api_secret = os.environ.get("BITSO_API_SECRET", "").strip() or None
        if environment is None:
            environment = os.environ.get("BITSO_ENV", "production").lower()

        self._api_key = api_key
        self._api_secret = api_secret
        self._environment = environment if environment in {"production", "sandbox"} else "production"
        self._base_url = (
            BITSO_PROD_URL if self._environment == "production" else BITSO_SANDBOX_URL
        )

        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

        if os.environ.get("PLUGINS_MX_MOCK") == "1":
            self._mock_mode = True
        elif explicit_creds or (self._api_key and self._api_secret):
            self._mock_mode = False
        else:
            self._mock_mode = is_mock_mode(["BITSO_API_KEY", "BITSO_API_SECRET"])

    @property
    def is_mock(self) -> bool:
        return self._mock_mode

    @property
    def environment(self) -> str:
        return self._environment

    def _require_creds(self) -> None:
        if not (self._api_key and self._api_secret):
            raise ConfigError("BITSO_API_KEY y BITSO_API_SECRET requeridos.")

    def _log(self, op: str, payload: dict[str, Any], *, success: bool = True) -> None:
        safe = dict(payload)
        # No hashea book (público) pero sí monto si lo hay
        self._bitacora.log(op, success=success, params_summary=safe)

    # ---------- public endpoints (sin auth) ----------

    async def get_ticker(self, book: str = "btc_mxn") -> dict[str, Any]:
        """Precio actual de un par. Cache 30s."""
        cache_key = f"ticker_{book}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("get_ticker", {"book": book})
        if self._mock_mode:
            r = mark_simulated(self._mock_ticker(book))
            self._cache.set(cache_key, r, ttl_minutes=0.5)
            return r

        url = f"{self._base_url}/v3/ticker/?book={book}"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        r = {**body.get("payload", {}), "simulated": False}
        self._cache.set(cache_key, r, ttl_minutes=0.5)
        return r

    async def get_order_book(self, book: str = "btc_mxn", aggregate: bool = True) -> dict[str, Any]:
        """Order book (bids + asks). Cache 5s."""
        cache_key = f"book_{book}_{aggregate}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("get_order_book", {"book": book, "aggregate": aggregate})
        if self._mock_mode:
            return mark_simulated(self._mock_order_book(book))

        url = f"{self._base_url}/v3/order_book/?book={book}&aggregate={str(aggregate).lower()}"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        r = {**body.get("payload", {}), "simulated": False}
        return r

    async def list_available_books(self) -> dict[str, Any]:
        """Lista todos los pares disponibles en Bitso."""
        self._log("list_available_books", {})
        if self._mock_mode:
            return mark_simulated({
                "books": [
                    {"book": "btc_mxn", "min_amount": "0.000001", "max_amount": "1000.0"},
                    {"book": "eth_mxn", "min_amount": "0.0001", "max_amount": "5000.0"},
                    {"book": "usdt_mxn", "min_amount": "1.0", "max_amount": "1000000.0"},
                ]
            })

        url = f"{self._base_url}/v3/available_books/"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
        return {**body.get("payload", {}), "simulated": False}

    # ---------- private endpoints (requieren auth) ----------

    async def get_account_status(self) -> dict[str, Any]:
        self._log("get_account_status", {})
        if self._mock_mode:
            return mark_simulated({
                "client_id": "demo_user",
                "status": "active",
                "daily_limit_mxn": "1000000.00",
                "verification_level": 4,
                "country": "MX",
            })

        self._require_creds()
        path = "/v3/account_status/"
        return await self._signed_get(path)

    async def get_balance(self) -> dict[str, Any]:
        self._log("get_balance", {})
        if self._mock_mode:
            return mark_simulated({
                "balances": [
                    {"currency": "mxn", "available": "15000.00", "locked": "0.00", "total": "15000.00"},
                    {"currency": "btc", "available": "0.025", "locked": "0.00", "total": "0.025"},
                    {"currency": "eth", "available": "1.5", "locked": "0.00", "total": "1.5"},
                    {"currency": "usdt", "available": "500.00", "locked": "0.00", "total": "500.00"},
                ]
            })

        self._require_creds()
        return await self._signed_get("/v3/balance/")

    async def get_fees(self) -> dict[str, Any]:
        self._log("get_fees", {})
        if self._mock_mode:
            return mark_simulated({
                "fees": [
                    {"book": "btc_mxn", "fee_percent": "0.65", "taker_fee_percent": "0.65", "maker_fee_percent": "0.50"},
                    {"book": "eth_mxn", "fee_percent": "0.65", "taker_fee_percent": "0.65", "maker_fee_percent": "0.50"},
                ]
            })

        self._require_creds()
        return await self._signed_get("/v3/fees/")

    async def get_ledger(
        self,
        operations: str = "",  # comma-separated: "fundings,withdrawals,trades,fees"
        marker: str | None = None,
        limit: int = 25,
    ) -> dict[str, Any]:
        """Historial de movimientos. Útil para reporte fiscal MX."""
        self._log("get_ledger", {"operations": operations, "limit": limit})
        if self._mock_mode:
            return mark_simulated({
                "ledger": [
                    {
                        "eid": "abc123",
                        "operation": "trade",
                        "created_at": _now_iso(),
                        "balance_updates": [
                            {"currency": "mxn", "amount": "-100000.00"},
                            {"currency": "btc", "amount": "0.0123"},
                        ],
                        "details": {"order_id": "ord_demo_001", "fid": "fid_demo"},
                    },
                    {
                        "eid": "abc124",
                        "operation": "fee",
                        "created_at": _now_iso(),
                        "balance_updates": [{"currency": "mxn", "amount": "-650.00"}],
                    },
                ]
            })

        self._require_creds()
        params = []
        if operations:
            params.append(f"operations={operations}")
        if marker:
            params.append(f"marker={marker}")
        params.append(f"limit={limit}")
        path = "/v3/ledger/?" + "&".join(params)
        return await self._signed_get(path)

    async def list_fundings(self, limit: int = 25) -> dict[str, Any]:
        """Lista depósitos fiat + crypto recibidos."""
        self._log("list_fundings", {"limit": limit})
        if self._mock_mode:
            return mark_simulated({
                "fundings": [
                    {
                        "fid": "fid_demo_001",
                        "operation": "deposit",
                        "currency": "mxn",
                        "method": "spei",
                        "amount": "5000.00",
                        "status": "complete",
                        "created_at": _now_iso(),
                        "details": {"sender_name": "Demo Sender", "sender_clabe": "012180001234567890"},
                    },
                    {
                        "fid": "fid_demo_002",
                        "operation": "deposit",
                        "currency": "btc",
                        "method": "btc",
                        "amount": "0.005",
                        "status": "complete",
                        "created_at": _now_iso(),
                        "details": {"tx_hash": "abc...def", "confirmations": 6},
                    },
                ]
            })

        self._require_creds()
        return await self._signed_get(f"/v3/fundings/?limit={limit}")

    async def list_withdrawals(self, limit: int = 25) -> dict[str, Any]:
        """Lista retiros fiat + crypto."""
        self._log("list_withdrawals", {"limit": limit})
        if self._mock_mode:
            return mark_simulated({
                "withdrawals": [
                    {
                        "wid": "wid_demo_001",
                        "currency": "mxn",
                        "method": "spei",
                        "amount": "2000.00",
                        "status": "complete",
                        "created_at": _now_iso(),
                    },
                ]
            })

        self._require_creds()
        return await self._signed_get(f"/v3/withdrawals/?limit={limit}")

    async def list_open_orders(self) -> dict[str, Any]:
        """Lista órdenes abiertas en el book."""
        self._log("list_open_orders", {})
        if self._mock_mode:
            return mark_simulated({"orders": []})

        self._require_creds()
        return await self._signed_get("/v3/open_orders/")

    # ---------- internal helpers ----------

    async def _signed_get(self, path: str) -> dict[str, Any]:
        headers = build_signature(
            api_key=self._api_key,  # type: ignore[arg-type]
            api_secret=self._api_secret,  # type: ignore[arg-type]
            http_verb="GET",
            request_path=path,
        )
        url = f"{self._base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
        return {**body.get("payload", {}), "simulated": False}

    # ---------- mock helpers ----------

    def _mock_ticker(self, book: str) -> dict[str, Any]:
        # Precios indicativos demo (cambian constantemente en realidad)
        precios = {
            "btc_mxn": {"last": "1850000.00", "high": "1875000.00", "low": "1820000.00"},
            "eth_mxn": {"last": "75000.00", "high": "76500.00", "low": "73800.00"},
            "usdt_mxn": {"last": "18.05", "high": "18.20", "low": "17.90"},
            "sol_mxn": {"last": "4200.00", "high": "4350.00", "low": "4150.00"},
        }
        precio = precios.get(book, {"last": "100.00", "high": "105.00", "low": "95.00"})
        return {
            "book": book,
            "volume": "125.42",
            "high": precio["high"],
            "last": precio["last"],
            "low": precio["low"],
            "vwap": precio["last"],
            "ask": str(float(precio["last"]) + 50),
            "bid": str(float(precio["last"]) - 50),
            "created_at": _now_iso(),
        }

    def _mock_order_book(self, book: str) -> dict[str, Any]:
        ticker = self._mock_ticker(book)
        last = float(ticker["last"])
        bids = [
            {"price": str(last - i * 10), "amount": "0.5"} for i in range(1, 6)
        ]
        asks = [
            {"price": str(last + i * 10), "amount": "0.5"} for i in range(1, 6)
        ]
        return {
            "asks": asks,
            "bids": bids,
            "sequence": secrets.randbits(31),
            "updated_at": _now_iso(),
        }
