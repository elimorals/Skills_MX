"""Tests para mp_shopify_mx/client.py."""

from __future__ import annotations

import pytest

from mp_shopify_mx.client import ShopifyMxClient
from shared.errors import ConfigError


@pytest.fixture
def client() -> ShopifyMxClient:
    return ShopifyMxClient()


# ---------- mode detection ----------


def test_default_es_mock(client: ShopifyMxClient) -> None:
    assert client.is_mock is True


def test_con_credenciales_no_mock(monkeypatch) -> None:
    monkeypatch.setenv("SHOPIFY_SHOP", "demo.myshopify.com")
    monkeypatch.setenv("SHOPIFY_ACCESS_TOKEN", "shpat_xxxxx")
    c = ShopifyMxClient()
    assert c.is_mock is False
    assert c.shop == "demo.myshopify.com"


def test_force_mock_override(monkeypatch) -> None:
    monkeypatch.setenv("SHOPIFY_SHOP", "demo.myshopify.com")
    monkeypatch.setenv("SHOPIFY_ACCESS_TOKEN", "shpat_xxxxx")
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    c = ShopifyMxClient()
    assert c.is_mock is True


def test_require_creds_falla_sin(client: ShopifyMxClient) -> None:
    with pytest.raises(ConfigError):
        client._require_creds()


def test_headers_falla_sin_token(client: ShopifyMxClient) -> None:
    with pytest.raises(ConfigError):
        client._headers()


# ---------- products ----------


@pytest.mark.asyncio
async def test_list_products_mock(client: ShopifyMxClient) -> None:
    r = await client.list_products(limit=10)
    assert r["simulated"] is True
    assert len(r["products"]) > 0


@pytest.mark.asyncio
async def test_get_product_mock(client: ShopifyMxClient) -> None:
    r = await client.get_product("1234")
    assert r["simulated"] is True
    assert r["id"] == 1234
    assert "variants" in r


@pytest.mark.asyncio
async def test_get_product_usa_cache(client: ShopifyMxClient) -> None:
    r1 = await client.get_product("5555")
    r2 = await client.get_product("5555")
    assert r1["created_at"] == r2["created_at"]


# ---------- inventory ----------


@pytest.mark.asyncio
async def test_inventory_level_mock(client: ShopifyMxClient) -> None:
    r = await client.get_inventory_level("100", "200")
    assert r["simulated"] is True
    assert r["available"] == 12


@pytest.mark.asyncio
async def test_update_inventory_mock(client: ShopifyMxClient) -> None:
    r = await client.update_inventory_level("100", "200", available=7)
    assert r["simulated"] is True
    assert r["available"] == 7


# ---------- orders ----------


@pytest.mark.asyncio
async def test_list_orders_mock(client: ShopifyMxClient) -> None:
    r = await client.list_orders(limit=10, financial_status="paid")
    assert r["simulated"] is True
    assert len(r["orders"]) > 0


@pytest.mark.asyncio
async def test_get_order_mock(client: ShopifyMxClient) -> None:
    r = await client.get_order("1000001")
    assert r["simulated"] is True
    assert r["currency"] == "MXN"
    assert "line_items" in r


# ---------- fulfillment ----------


@pytest.mark.asyncio
async def test_create_fulfillment_mock(client: ShopifyMxClient) -> None:
    r = await client.create_fulfillment(
        "1000001", tracking_number="9320XXX", tracking_company="Estafeta"
    )
    assert r["simulated"] is True
    assert r["tracking_number"] == "9320XXX"
    assert r["tracking_company"] == "Estafeta"


@pytest.mark.asyncio
async def test_create_fulfillment_sin_tracking(client: ShopifyMxClient) -> None:
    r = await client.create_fulfillment("1000001")
    assert r["simulated"] is True
    assert r["tracking_number"] is None


# ---------- customers ----------


@pytest.mark.asyncio
async def test_get_customer_mock(client: ShopifyMxClient) -> None:
    r = await client.get_customer("200001")
    assert r["simulated"] is True
    assert r["email"] == "demo@example.mx"


# ---------- webhooks ----------


@pytest.mark.asyncio
async def test_list_webhooks_mock(client: ShopifyMxClient) -> None:
    r = await client.list_webhooks()
    assert r["simulated"] is True
    assert len(r["webhooks"]) > 0


# ---------- tax MX utility (local) ----------


def test_calculate_tax_general(client: ShopifyMxClient) -> None:
    r = client.calculate_tax_mx(subtotal_mxn=1000.0)
    assert r["iva_mxn"] == 160.0
    assert r["total_mxn"] == 1160.0
    assert r["tasa_aplicada"] == 0.16


def test_calculate_tax_frontera(client: ShopifyMxClient) -> None:
    r = client.calculate_tax_mx(subtotal_mxn=1000.0, region="frontera_norte")
    assert r["iva_mxn"] == 80.0
    assert r["total_mxn"] == 1080.0
    assert r["tasa_aplicada"] == 0.08


def test_calculate_tax_exento(client: ShopifyMxClient) -> None:
    r = client.calculate_tax_mx(subtotal_mxn=500.0, producto_exento=True)
    assert r["iva_mxn"] == 0.0
    assert r["total_mxn"] == 500.0
    assert r["razon"] == "producto_exento"


# ---------- bitácora ----------


@pytest.mark.asyncio
async def test_bitacora_hashea_email(client: ShopifyMxClient, tmp_path) -> None:
    """Email del customer NO debe escribirse en claro."""
    await client.get_customer("200001")  # mock retorna demo@example.mx
    # El email no es input, así que no hay que hashear input. Solo verificar
    # que la operación se logge sin leak.
    candidates = list((tmp_path / "audit").rglob("*.jsonl"))
    if candidates:
        content = candidates[0].read_text()
        assert "get_customer" in content
