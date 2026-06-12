"""mp_amazon_mx_seller — MCP para Amazon MX Selling Partner.

⚠ Mock-first. Path real (LWA + AWS Sig V4) NO implementado completamente.
Comisiones y FBA fees son referenciales 2025.
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

from mp_amazon_mx_seller.catalogos import (  # noqa: E402
    COMISIONES_CATEGORIA,
    COMISIONES_FBA_MX,
    FULFILLMENT_CHANNEL,
    LISTING_STATUS,
    MARKETPLACE_ID_MX,
    ORDER_STATUS,
)
from mp_amazon_mx_seller.client import AmazonMxSellerClient  # noqa: E402
from shared.errors import McpError  # noqa: E402


mcp = FastMCP("amazon_mx_seller_mcp")
_client = AmazonMxSellerClient()


class ListListingsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    limit: int = Field(25, ge=1, le=100)
    status: Optional[Literal[
        "ACTIVE", "INACTIVE", "INCOMPLETE", "PROHIBITED", "SUPPRESSED"
    ]] = None


class SkuInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sku: str = Field(..., min_length=1, max_length=80)


class UpdateInventoryInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sku: str = Field(..., min_length=1, max_length=80)
    quantity: int = Field(..., ge=0)


class ListOrdersInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    limit: int = Field(25, ge=1, le=100)
    status: Optional[Literal[
        "Pending", "Unshipped", "PartiallyShipped", "Shipped", "Canceled",
        "Unfulfillable", "InvoiceUnconfirmed", "PendingAvailability"
    ]] = None


class OrderIdInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amazon_order_id: str = Field(..., min_length=10, max_length=30)


class FeesEstimateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sku: str = Field(..., min_length=1, max_length=80)
    price_mxn: float = Field(..., gt=0)


@mcp.tool(annotations={"title": "Listar listings Amazon MX", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def amazon_mx_list_listings(args: ListListingsInput) -> dict:
    try:
        return await _client.list_listings(args.limit, args.status)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Detalle listing por SKU", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def amazon_mx_get_listing(args: SkuInput) -> dict:
    try:
        return await _client.get_listing(args.sku)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Actualizar inventario (stock) por SKU", "readOnlyHint": False, "idempotentHint": True, "openWorldHint": True})
async def amazon_mx_update_inventory(args: UpdateInventoryInput) -> dict:
    """Setea stock absoluto del SKU."""
    try:
        return await _client.update_inventory(args.sku, args.quantity)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Listar órdenes Amazon MX", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def amazon_mx_list_orders(args: ListOrdersInput) -> dict:
    try:
        return await _client.list_orders(args.limit, args.status)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Detalle orden Amazon MX por ID", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def amazon_mx_get_order(args: OrderIdInput) -> dict:
    try:
        return await _client.get_order(args.amazon_order_id)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Estimar comisión Amazon + FBA por precio", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def amazon_mx_get_fees_estimate(args: FeesEstimateInput) -> dict:
    """Estima comisión referral + fulfillment FBA + storage. Útil para pricing."""
    try:
        return await _client.get_fees_estimate(args.sku, args.price_mxn)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Catálogos Amazon MX: marketplace ID, status, comisiones", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def amazon_mx_listar_catalogos() -> dict:
    return {
        "marketplace_id_mx": MARKETPLACE_ID_MX,
        "listing_status": LISTING_STATUS,
        "order_status": ORDER_STATUS,
        "fulfillment_channel": FULFILLMENT_CHANNEL,
        "comisiones_categoria": COMISIONES_CATEGORIA,
        "comisiones_fba_mx": COMISIONES_FBA_MX,
        "nota": "Comisiones referenciales 2025. Validar 2026 en Amazon Seller Central.",
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
