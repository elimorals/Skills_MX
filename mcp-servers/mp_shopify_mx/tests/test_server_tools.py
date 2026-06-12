"""End-to-end tests para los tools FastMCP."""

from __future__ import annotations

import pytest

from mp_shopify_mx.server import (
    CalculateTaxInput,
    CreateFulfillmentInput,
    CustomerIdInput,
    InventoryLevelInput,
    ListOrdersInput,
    ListProductsInput,
    OrderIdInput,
    ProductIdInput,
    UpdateInventoryInput,
    shopify_calculate_tax_mx,
    shopify_create_fulfillment,
    shopify_get_customer,
    shopify_get_inventory_level,
    shopify_get_order,
    shopify_get_product,
    shopify_list_orders,
    shopify_list_products,
    shopify_list_webhooks,
    shopify_listar_catalogos,
    shopify_update_inventory_level,
)


@pytest.mark.asyncio
async def test_list_products() -> None:
    r = await shopify_list_products(ListProductsInput(limit=5))
    assert r["simulated"] is True


@pytest.mark.asyncio
async def test_get_product() -> None:
    r = await shopify_get_product(ProductIdInput(product_id="1234"))
    assert r["id"] == 1234


@pytest.mark.asyncio
async def test_get_inventory_level() -> None:
    r = await shopify_get_inventory_level(
        InventoryLevelInput(inventory_item_id="100", location_id="200")
    )
    assert r["available"] == 12


@pytest.mark.asyncio
async def test_update_inventory_level() -> None:
    r = await shopify_update_inventory_level(
        UpdateInventoryInput(inventory_item_id="100", location_id="200", available=5)
    )
    assert r["available"] == 5


@pytest.mark.asyncio
async def test_list_orders() -> None:
    r = await shopify_list_orders(ListOrdersInput(limit=10, financial_status="paid"))
    assert "orders" in r


@pytest.mark.asyncio
async def test_get_order() -> None:
    r = await shopify_get_order(OrderIdInput(order_id="1000001"))
    assert r["currency"] == "MXN"


@pytest.mark.asyncio
async def test_create_fulfillment() -> None:
    r = await shopify_create_fulfillment(
        CreateFulfillmentInput(
            order_id="1000001",
            tracking_number="EST123",
            tracking_company="Estafeta",
        )
    )
    assert r["tracking_company"] == "Estafeta"


@pytest.mark.asyncio
async def test_get_customer() -> None:
    r = await shopify_get_customer(CustomerIdInput(customer_id="200001"))
    assert r["email"] == "demo@example.mx"


@pytest.mark.asyncio
async def test_list_webhooks() -> None:
    r = await shopify_list_webhooks()
    assert "webhooks" in r


@pytest.mark.asyncio
async def test_calculate_tax_general() -> None:
    r = await shopify_calculate_tax_mx(CalculateTaxInput(subtotal_mxn=1000.0))
    assert r["iva_mxn"] == 160.0


@pytest.mark.asyncio
async def test_calculate_tax_frontera() -> None:
    r = await shopify_calculate_tax_mx(
        CalculateTaxInput(subtotal_mxn=1000.0, region="frontera_norte")
    )
    assert r["iva_mxn"] == 80.0


@pytest.mark.asyncio
async def test_calculate_tax_exento() -> None:
    r = await shopify_calculate_tax_mx(
        CalculateTaxInput(subtotal_mxn=500.0, producto_exento=True)
    )
    assert r["iva_mxn"] == 0.0


@pytest.mark.asyncio
async def test_listar_catalogos() -> None:
    r = await shopify_listar_catalogos()
    assert "order_financial_status" in r
    assert "carriers_mx" in r
    assert "estafeta" in r["carriers_mx"]
