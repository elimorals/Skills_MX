"""Tests para mp_bitso/client.py."""

from __future__ import annotations

import pytest

from mp_bitso.client import BitsoClient
from shared.errors import ConfigError


@pytest.fixture
def client() -> BitsoClient:
    return BitsoClient()


# ---------- mode detection ----------


def test_default_es_mock(client: BitsoClient) -> None:
    assert client.is_mock is True
    assert client.environment == "production"


def test_con_credenciales_no_mock(monkeypatch) -> None:
    monkeypatch.setenv("BITSO_API_KEY", "demo")
    monkeypatch.setenv("BITSO_API_SECRET", "secret")
    c = BitsoClient()
    assert c.is_mock is False


def test_sandbox_env(monkeypatch) -> None:
    monkeypatch.setenv("BITSO_ENV", "sandbox")
    c = BitsoClient()
    assert c.environment == "sandbox"


def test_force_mock_override(monkeypatch) -> None:
    monkeypatch.setenv("BITSO_API_KEY", "demo")
    monkeypatch.setenv("BITSO_API_SECRET", "secret")
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    c = BitsoClient()
    assert c.is_mock is True


def test_require_creds_falla(client: BitsoClient) -> None:
    with pytest.raises(ConfigError):
        client._require_creds()


# ---------- public endpoints ----------


@pytest.mark.asyncio
async def test_get_ticker_mock(client: BitsoClient) -> None:
    r = await client.get_ticker("btc_mxn")
    assert r["simulated"] is True
    assert r["book"] == "btc_mxn"
    assert float(r["last"]) > 0


@pytest.mark.asyncio
async def test_get_ticker_usa_cache(client: BitsoClient) -> None:
    r1 = await client.get_ticker("eth_mxn")
    r2 = await client.get_ticker("eth_mxn")
    # Cache 30s → mismo created_at
    assert r1["created_at"] == r2["created_at"]


@pytest.mark.asyncio
async def test_get_order_book_mock(client: BitsoClient) -> None:
    r = await client.get_order_book("btc_mxn")
    assert r["simulated"] is True
    assert len(r["bids"]) > 0
    assert len(r["asks"]) > 0


@pytest.mark.asyncio
async def test_list_available_books_mock(client: BitsoClient) -> None:
    r = await client.list_available_books()
    assert r["simulated"] is True
    assert len(r["books"]) > 0


# ---------- private endpoints (mock) ----------


@pytest.mark.asyncio
async def test_account_status_mock(client: BitsoClient) -> None:
    r = await client.get_account_status()
    assert r["simulated"] is True
    assert r["country"] == "MX"


@pytest.mark.asyncio
async def test_balance_mock(client: BitsoClient) -> None:
    r = await client.get_balance()
    assert r["simulated"] is True
    assert len(r["balances"]) > 0


@pytest.mark.asyncio
async def test_fees_mock(client: BitsoClient) -> None:
    r = await client.get_fees()
    assert r["simulated"] is True


@pytest.mark.asyncio
async def test_ledger_mock(client: BitsoClient) -> None:
    r = await client.get_ledger(operations="trades,fees", limit=10)
    assert r["simulated"] is True
    assert len(r["ledger"]) > 0


@pytest.mark.asyncio
async def test_fundings_mock(client: BitsoClient) -> None:
    r = await client.list_fundings(limit=10)
    assert r["simulated"] is True
    # Verificar que hay un funding SPEI demo
    spei_demo = next((f for f in r["fundings"] if f["method"] == "spei"), None)
    assert spei_demo is not None


@pytest.mark.asyncio
async def test_withdrawals_mock(client: BitsoClient) -> None:
    r = await client.list_withdrawals()
    assert r["simulated"] is True


@pytest.mark.asyncio
async def test_open_orders_mock(client: BitsoClient) -> None:
    r = await client.list_open_orders()
    assert r["simulated"] is True
