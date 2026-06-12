"""mp_trustly_mx — MCP para Trustly MX (open banking)."""

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

from mp_trustly_mx.catalogos import (  # noqa: E402
    BANCOS_SOPORTADOS,
    PAYMENT_STATUS,
    WEBHOOK_EVENTS,
)
from mp_trustly_mx.client import TrustlyMxClient  # noqa: E402
from shared.errors import McpError  # noqa: E402


mcp = FastMCP("trustly_mx_mcp")
_client = TrustlyMxClient()


class CreatePaymentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount_mxn: float = Field(..., gt=0, description="Monto en MXN (decimal).")
    external_reference: str = Field(..., min_length=1, max_length=80,
                                     description="Referencia única tuya para reconciliar.")
    customer_email: str = Field(..., min_length=3, max_length=254)
    description: str = Field("", max_length=300)


class PaymentIdInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    payment_id: str = Field(..., min_length=1, max_length=80)


class ListPaymentsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Optional[Literal[
        "pending", "authorized", "completed", "failed", "expired", "cancelled", "refunded"
    ]] = None
    limit: int = Field(25, ge=1, le=100)


class RefundInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    payment_id: str = Field(..., min_length=1, max_length=80)
    amount_mxn: Optional[float] = Field(None, ge=0, description="None = refund total.")


@mcp.tool(annotations={"title": "Crear solicitud de pago open banking", "readOnlyHint": False, "openWorldHint": True})
async def trustly_create_payment(args: CreatePaymentInput) -> dict:
    """Crea solicitud de pago. Cliente recibe checkout_url para autorizar en su banco."""
    try:
        return await _client.create_payment_request(
            args.amount_mxn, args.external_reference,
            args.customer_email, args.description,
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Consultar status de pago", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def trustly_get_payment(args: PaymentIdInput) -> dict:
    """Status actual del pago (pending, completed, etc.). Cache 2 min."""
    try:
        return await _client.get_payment_status(args.payment_id)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Listar pagos con filtros", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def trustly_list_payments(args: ListPaymentsInput) -> dict:
    try:
        return await _client.list_payments(status=args.status, limit=args.limit)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Refund pago total o parcial", "readOnlyHint": False, "destructiveHint": True, "openWorldHint": True})
async def trustly_refund_payment(args: RefundInput) -> dict:
    """Devuelve fondos al pagador. amount=None = refund total."""
    try:
        return await _client.refund_payment(args.payment_id, args.amount_mxn)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Catálogos Trustly: status, bancos soportados, webhooks", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def trustly_listar_catalogos() -> dict:
    return {
        "payment_status": PAYMENT_STATUS,
        "bancos_soportados": BANCOS_SOPORTADOS,
        "webhook_events": WEBHOOK_EVENTS,
        "nota": "Trustly opera open banking en MX desde 2023. Cobertura ~8 bancos principales.",
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
