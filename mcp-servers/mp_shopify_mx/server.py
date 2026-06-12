"""mp_shopify_mx — MCP para Shopify Admin API con utilidades específicas MX.

10 tools:
- shopify_list_products / shopify_get_product
- shopify_get_inventory_level / shopify_update_inventory_level
- shopify_list_orders / shopify_get_order
- shopify_create_fulfillment
- shopify_get_customer
- shopify_list_webhooks
- shopify_calculate_tax_mx (utility local)
- shopify_listar_catalogos

Mock-first sin SHOPIFY_SHOP + SHOPIFY_ACCESS_TOKEN.

⚠ Algunos endpoints son rate-limited. Cache de read ops mitiga.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_shopify_mx.catalogos import (  # noqa: E402
    CANCELLATION_REASONS,
    CARRIERS_MX,
    ORDER_FINANCIAL_STATUS,
    ORDER_FULFILLMENT_STATUS,
    PAYMENT_GATEWAYS_MX,
    TAX_CONFIG_MX,
    WEBHOOK_TOPICS,
)
from mp_shopify_mx.client import ShopifyMxClient  # noqa: E402
from shared.errors import McpError  # noqa: E402


mcp = FastMCP("shopify_mx_mcp")
_client = ShopifyMxClient()


# ---------- input models ----------


class ListProductsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limit: int = Field(50, ge=1, le=250)
    status: Optional[Literal["active", "archived", "draft"]] = None


class ProductIdInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_id: str = Field(..., min_length=1, max_length=80)


class InventoryLevelInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    inventory_item_id: str = Field(..., min_length=1, max_length=80)
    location_id: str = Field(..., min_length=1, max_length=80)


class UpdateInventoryInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    inventory_item_id: str = Field(..., min_length=1, max_length=80)
    location_id: str = Field(..., min_length=1, max_length=80)
    available: int = Field(..., ge=0, description="Stock disponible (entero).")


class ListOrdersInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limit: int = Field(50, ge=1, le=250)
    status: Literal["open", "closed", "cancelled", "any"] = "any"
    financial_status: Optional[
        Literal["pending", "authorized", "partially_paid", "paid", "partially_refunded", "refunded", "voided"]
    ] = None
    fulfillment_status: Optional[
        Literal["unfulfilled", "partial", "fulfilled", "restocked"]
    ] = None
    created_at_min: Optional[str] = Field(None, description="ISO date min (YYYY-MM-DD).")
    created_at_max: Optional[str] = None


class OrderIdInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: str = Field(..., min_length=1, max_length=80)


class CreateFulfillmentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: str = Field(..., min_length=1, max_length=80)
    tracking_number: Optional[str] = None
    tracking_company: Optional[str] = Field(
        None,
        description="Carrier name (Estafeta, DHL, FedEx, 99 Minutos, etc.)",
    )
    notify_customer: bool = True


class CustomerIdInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str = Field(..., min_length=1, max_length=80)


class CalculateTaxInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subtotal_mxn: float = Field(..., ge=0, description="Subtotal sin IVA.")
    region: Literal["general", "frontera_norte"] = "general"
    producto_exento: bool = Field(
        False,
        description="True si el producto es exento de IVA (medicamentos, libros, alimentos básicos).",
    )


# ---------- tools ----------


@mcp.tool(
    annotations={
        "title": "Listar productos Shopify",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def shopify_list_products(args: ListProductsInput) -> dict:
    """Lista productos con paginación."""
    try:
        return await _client.list_products(limit=args.limit, status=args.status)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Obtener producto Shopify por ID",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def shopify_get_product(args: ProductIdInput) -> dict:
    """Lee detalle de un producto."""
    try:
        return await _client.get_product(args.product_id)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Consultar nivel de inventario por SKU + sucursal",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def shopify_get_inventory_level(args: InventoryLevelInput) -> dict:
    """Stock disponible de un SKU en una sucursal."""
    try:
        return await _client.get_inventory_level(args.inventory_item_id, args.location_id)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Actualizar nivel de inventario (CRÍTICO: usar después de venta o ajuste)",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,  # set absolute es idempotent
        "openWorldHint": True,
    },
)
async def shopify_update_inventory_level(args: UpdateInventoryInput) -> dict:
    """Setea stock disponible (absoluto, no delta)."""
    try:
        return await _client.update_inventory_level(
            args.inventory_item_id, args.location_id, args.available
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Listar órdenes Shopify",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def shopify_list_orders(args: ListOrdersInput) -> dict:
    """Lista órdenes con filtros (status, financial_status, fulfillment_status, fechas)."""
    try:
        return await _client.list_orders(
            limit=args.limit,
            status=args.status,
            financial_status=args.financial_status,
            fulfillment_status=args.fulfillment_status,
            created_at_min=args.created_at_min,
            created_at_max=args.created_at_max,
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Obtener orden Shopify por ID",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def shopify_get_order(args: OrderIdInput) -> dict:
    """Detalle de orden con line items + customer + status."""
    try:
        return await _client.get_order(args.order_id)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Crear fulfillment (marcar orden como enviada)",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def shopify_create_fulfillment(args: CreateFulfillmentInput) -> dict:
    """Marca orden como enviada con tracking opcional. Notifica al cliente por default."""
    try:
        return await _client.create_fulfillment(
            args.order_id,
            tracking_number=args.tracking_number,
            tracking_company=args.tracking_company,
            notify_customer=args.notify_customer,
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Obtener customer Shopify por ID",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def shopify_get_customer(args: CustomerIdInput) -> dict:
    """Lee datos del cliente."""
    try:
        return await _client.get_customer(args.customer_id)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Listar webhooks configurados",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def shopify_list_webhooks() -> dict:
    """Lista webhooks configurados (orders/paid, orders/fulfilled, etc.)."""
    try:
        return await _client.list_webhooks()
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Calcular IVA según región MX (local, sin red)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def shopify_calculate_tax_mx(args: CalculateTaxInput) -> dict:
    """Calcula IVA MX (16% general, 8% frontera norte, 0% exentos).

    Local — no requiere API call. Útil antes de crear orden para mostrar
    total al cliente.
    """
    return _client.calculate_tax_mx(
        subtotal_mxn=args.subtotal_mxn,
        region=args.region,
        producto_exento=args.producto_exento,
    )


@mcp.tool(
    annotations={
        "title": "Catálogos: status órdenes, paqueterías MX, gateways pago, webhook topics",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def shopify_listar_catalogos() -> dict:
    """Discovery offline de catálogos Shopify + ajustes MX."""
    return {
        "order_financial_status": ORDER_FINANCIAL_STATUS,
        "order_fulfillment_status": ORDER_FULFILLMENT_STATUS,
        "cancellation_reasons": CANCELLATION_REASONS,
        "payment_gateways_mx": PAYMENT_GATEWAYS_MX,
        "carriers_mx": CARRIERS_MX,
        "webhook_topics": WEBHOOK_TOPICS,
        "tax_config_mx": TAX_CONFIG_MX,
        "nota": (
            "Para MX: gateway debe ser Conekta o MercadoPago. "
            "Configurar tax_inclusive=true (precios YA incluyen IVA). "
            "Aviso de privacidad LFPDPPP obligatorio en footer."
        ),
    }


# ---------- entry point ----------


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
