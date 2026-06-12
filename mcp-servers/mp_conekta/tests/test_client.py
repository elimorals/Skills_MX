"""Tests para mp_conekta/client.py — modo mock."""

from __future__ import annotations

import pytest

from mp_conekta.client import ConektaClient
from mp_conekta.tests.conftest import DEMO_CUSTOMER
from shared.errors import ConfigError


@pytest.fixture
def client() -> ConektaClient:
    return ConektaClient()


# ---------- mode detection ----------


def test_default_es_mock(client: ConektaClient) -> None:
    assert client.is_mock is True
    assert client.environment == "mock"


def test_con_test_key_es_sandbox(monkeypatch) -> None:
    monkeypatch.setenv("CONEKTA_API_KEY", "key_test_abc123")
    c = ConektaClient()
    assert c.is_mock is False
    assert c.environment == "sandbox"


def test_con_live_key_es_produccion(monkeypatch) -> None:
    monkeypatch.setenv("CONEKTA_API_KEY", "key_live_abc123")
    c = ConektaClient()
    assert c.is_mock is False
    assert c.environment == "production"


def test_force_mock_override(monkeypatch) -> None:
    monkeypatch.setenv("CONEKTA_API_KEY", "key_live_xyz")
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    c = ConektaClient()
    assert c.is_mock is True


# ---------- orders ----------


@pytest.mark.asyncio
async def test_create_order_mock_devuelve_id(client: ConektaClient) -> None:
    r = await client.create_order(
        {
            "line_items": [{"name": "Producto", "unit_price": 50000, "quantity": 2}],
            "currency": "MXN",
            "customer_info": DEMO_CUSTOMER,
        }
    )
    assert r["simulated"] is True
    assert r["id"].startswith("ord_")
    assert r["payment_status"] == "pending_payment"
    assert r["amount"] == 100000  # 2 × 50000


@pytest.mark.asyncio
async def test_get_order_mock(client: ConektaClient) -> None:
    r = await client.get_order("ord_demo123")
    assert r["simulated"] is True
    assert r["id"] == "ord_demo123"


@pytest.mark.asyncio
async def test_get_order_usa_cache(client: ConektaClient) -> None:
    r1 = await client.get_order("ord_cached")
    r2 = await client.get_order("ord_cached")
    # Mismo orden → debería retornar mismo payload del cache
    assert r1["created_at"] == r2["created_at"]


@pytest.mark.asyncio
async def test_list_orders_mock(client: ConektaClient) -> None:
    r = await client.list_orders(limit=10, payment_status="paid")
    assert r["simulated"] is True
    assert r["data"] == []


# ---------- charges ----------


@pytest.mark.asyncio
async def test_create_charge_oxxo_devuelve_referencia(client: ConektaClient) -> None:
    r = await client.create_charge_on_order(
        "ord_demo", {"payment_method": {"type": "oxxo_cash"}}
    )
    assert r["simulated"] is True
    assert r["status"] == "pending_payment"
    assert r["payment_method"]["type"] == "oxxo_cash"
    assert "reference" in r["payment_method"]


@pytest.mark.asyncio
async def test_create_charge_card_es_paid_mock(client: ConektaClient) -> None:
    r = await client.create_charge_on_order(
        "ord_demo", {"payment_method": {"type": "card", "token_id": "tok_xxx"}}
    )
    assert r["simulated"] is True
    assert r["status"] == "paid"
    assert r["payment_method"]["last4"] == "4242"


@pytest.mark.asyncio
async def test_create_charge_spei_pending(client: ConektaClient) -> None:
    r = await client.create_charge_on_order(
        "ord_demo", {"payment_method": {"type": "spei"}}
    )
    assert r["status"] == "pending_payment"
    assert "reference" in r["payment_method"]


# ---------- refunds ----------


@pytest.mark.asyncio
async def test_refund_total_mock(client: ConektaClient) -> None:
    r = await client.refund_charge("ord_demo")
    assert r["simulated"] is True
    assert r["status"] == "refunded"
    assert r["amount"] is None


@pytest.mark.asyncio
async def test_refund_parcial_mock(client: ConektaClient) -> None:
    r = await client.refund_charge("ord_demo", amount=25000, reason="duplicate")
    assert r["amount"] == 25000
    assert r["reason"] == "duplicate"


# ---------- customers ----------


@pytest.mark.asyncio
async def test_create_customer_mock(client: ConektaClient) -> None:
    r = await client.create_customer(DEMO_CUSTOMER)
    assert r["simulated"] is True
    assert r["id"].startswith("cus_")
    assert r["email"] == DEMO_CUSTOMER["email"]


@pytest.mark.asyncio
async def test_get_customer_mock(client: ConektaClient) -> None:
    r = await client.get_customer("cus_xyz")
    assert r["simulated"] is True
    assert r["id"] == "cus_xyz"


# ---------- payment links ----------


@pytest.mark.asyncio
async def test_payment_link_mock(client: ConektaClient) -> None:
    r = await client.create_payment_link("Consultoría", 150000, "MXN")
    assert r["simulated"] is True
    assert r["amount"] == 150000
    assert r["url"].startswith("https://pay.conekta.com/link/")


# ---------- subscriptions ----------


@pytest.mark.asyncio
async def test_subscription_create_mock(client: ConektaClient) -> None:
    r = await client.subscription_create("cus_x", "plan_basic")
    assert r["simulated"] is True
    assert r["status"] == "active"


@pytest.mark.asyncio
async def test_subscription_cancel_mock(client: ConektaClient) -> None:
    r = await client.subscription_cancel("cus_x")
    assert r["simulated"] is True
    assert r["status"] == "canceled"


# ---------- config errors ----------


def test_require_key_falla_sin_credenciales() -> None:
    c = ConektaClient()
    with pytest.raises(ConfigError):
        c._require_key()


def test_headers_falla_sin_key() -> None:
    c = ConektaClient()
    with pytest.raises(ConfigError):
        c._headers()


def test_headers_ok_con_key(monkeypatch) -> None:
    monkeypatch.setenv("CONEKTA_API_KEY", "key_test_xxx")
    c = ConektaClient()
    h = c._headers()
    assert h["Authorization"].startswith("Basic ")
    assert "conekta-v2.1.0" in h["Accept"]


# ---------- bitácora ----------


@pytest.mark.asyncio
async def test_bitacora_hashea_email(client: ConektaClient, tmp_path) -> None:
    """El email del customer NO debe escribirse en claro en el audit log."""
    await client.create_order(
        {
            "line_items": [{"name": "X", "unit_price": 1000, "quantity": 1}],
            "currency": "MXN",
            "customer_info": DEMO_CUSTOMER,
        }
    )
    candidates = list((tmp_path / "audit").rglob("*.jsonl"))
    assert candidates, "No se generó archivo de bitácora"
    content = candidates[0].read_text()
    assert DEMO_CUSTOMER["email"] not in content
    assert "create_order" in content
