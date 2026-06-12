"""Tests mp_amazon_mx_seller."""

from __future__ import annotations

import pytest

from mp_amazon_mx_seller.client import AmazonMxSellerClient
from mp_amazon_mx_seller.server import (
    FeesEstimateInput,
    ListListingsInput,
    ListOrdersInput,
    OrderIdInput,
    SkuInput,
    UpdateInventoryInput,
    amazon_mx_get_fees_estimate,
    amazon_mx_get_listing,
    amazon_mx_get_order,
    amazon_mx_list_listings,
    amazon_mx_list_orders,
    amazon_mx_listar_catalogos,
    amazon_mx_update_inventory,
)


@pytest.fixture
def client() -> AmazonMxSellerClient:
    return AmazonMxSellerClient()


def test_default_mock(client: AmazonMxSellerClient) -> None:
    assert client.is_mock is True


@pytest.mark.asyncio
async def test_list_listings(client: AmazonMxSellerClient) -> None:
    r = await client.list_listings(limit=5)
    assert "listings" in r


@pytest.mark.asyncio
async def test_get_listing(client: AmazonMxSellerClient) -> None:
    r = await client.get_listing("SKU-DEMO-001")
    assert r["sku"] == "SKU-DEMO-001"
    assert "comision_amazon_mxn" in r


@pytest.mark.asyncio
async def test_update_inventory(client: AmazonMxSellerClient) -> None:
    r = await client.update_inventory("SKU-DEMO-001", quantity=12)
    assert r["new_quantity"] == 12


@pytest.mark.asyncio
async def test_list_orders(client: AmazonMxSellerClient) -> None:
    r = await client.list_orders(limit=5)
    assert "orders" in r


@pytest.mark.asyncio
async def test_get_order(client: AmazonMxSellerClient) -> None:
    r = await client.get_order("701-1234567-1234567")
    assert "items" in r


@pytest.mark.asyncio
async def test_fees_estimate(client: AmazonMxSellerClient) -> None:
    r = await client.get_fees_estimate("SKU-DEMO-001", price_mxn=499.0)
    assert "comision_referral_mxn" in r
    assert "neto_seller_mxn" in r
    assert r["neto_seller_mxn"] < 499.0


@pytest.mark.asyncio
async def test_list_tool() -> None:
    r = await amazon_mx_list_listings(ListListingsInput(limit=5))
    assert "listings" in r


@pytest.mark.asyncio
async def test_get_listing_tool() -> None:
    r = await amazon_mx_get_listing(SkuInput(sku="SKU-DEMO-001"))
    assert r["sku"] == "SKU-DEMO-001"


@pytest.mark.asyncio
async def test_update_inventory_tool() -> None:
    r = await amazon_mx_update_inventory(
        UpdateInventoryInput(sku="SKU-DEMO-001", quantity=8)
    )
    assert r["new_quantity"] == 8


@pytest.mark.asyncio
async def test_list_orders_tool() -> None:
    r = await amazon_mx_list_orders(ListOrdersInput(limit=5))
    assert "orders" in r


@pytest.mark.asyncio
async def test_get_order_tool() -> None:
    r = await amazon_mx_get_order(OrderIdInput(amazon_order_id="701-1234567-1234567"))
    assert "items" in r


@pytest.mark.asyncio
async def test_fees_tool() -> None:
    r = await amazon_mx_get_fees_estimate(
        FeesEstimateInput(sku="SKU-DEMO-001", price_mxn=750.0)
    )
    assert r["price_mxn"] == 750.0


@pytest.mark.asyncio
async def test_catalogos() -> None:
    r = await amazon_mx_listar_catalogos()
    assert r["marketplace_id_mx"] == "A1AM78C64UM0Y8"
    assert "comisiones_categoria" in r
