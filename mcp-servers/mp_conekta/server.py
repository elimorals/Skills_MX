"""mp_conekta — MCP para Conekta (pasarela MX con OXXO + SPEI + TDC).

11 tools:
- conekta_create_order
- conekta_get_order
- conekta_list_orders
- conekta_create_charge_on_order
- conekta_refund_order
- conekta_create_customer
- conekta_get_customer
- conekta_create_payment_link
- conekta_subscription_create
- conekta_subscription_update
- conekta_subscription_cancel
- conekta_validate_webhook
- conekta_listar_catalogos

Mock-first sin CONEKTA_API_KEY. Path real con sandbox keys (`key_test_...`)
o producción (`key_live_...`).

⚠ Precios en Conekta son CENTAVOS enteros. $100.00 MXN = 10000.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Literal, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_conekta.catalogos import (  # noqa: E402
    CHARGE_DECLINE_CODES,
    CHARGE_STATUS,
    CURRENCY,
    ORDER_STATUS,
    PAYMENT_METHOD_TYPE,
    SUBSCRIPTION_STATUS,
    WEBHOOK_EVENTS,
)
from mp_conekta.client import ConektaClient  # noqa: E402
from mp_conekta.webhooks import (  # noqa: E402
    validate_webhook_auto,
)
from shared.errors import McpError  # noqa: E402


mcp = FastMCP("conekta_mcp")
_client = ConektaClient()


# ---------- input models ----------


class LineItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Nombre del producto.", min_length=1, max_length=250)
    unit_price: int = Field(..., description="Precio unitario en CENTAVOS.", ge=0)
    quantity: int = Field(..., description="Cantidad.", ge=1)


class CustomerInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=250)
    email: str = Field(..., min_length=3, max_length=254)
    phone: Optional[str] = Field(None, description="Teléfono E.164 (+52...).")


class PaymentMethodInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal[
        "card", "oxxo_cash", "spei", "default", "cashi"
    ] = Field(..., description="Tipo de método de pago.")
    token_id: Optional[str] = Field(
        None, description="Token de tarjeta (requerido para type=card)."
    )
    expires_at: Optional[int] = Field(
        None, description="Unix timestamp de expiración (para offline)."
    )


class CreateOrderInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    line_items: list[LineItem] = Field(..., min_length=1)
    currency: Literal["MXN", "USD"] = Field("MXN")
    customer_info: CustomerInfo = Field(...)
    charges: Optional[list[PaymentMethodInput]] = Field(
        None,
        description="Opcional — si se pasa, intenta crear charges al mismo tiempo que la orden.",
    )


class OrderIdInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    order_id: str = Field(..., min_length=1, max_length=80)


class ListOrdersInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limit: int = Field(25, ge=1, le=250)
    next_id: Optional[str] = Field(None, description="Cursor para siguiente página.")
    payment_status: Optional[
        Literal["paid", "pending_payment", "declined", "refunded", "expired", "canceled"]
    ] = None


class ChargeOnOrderInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: str = Field(..., min_length=1, max_length=80)
    payment_method: PaymentMethodInput = Field(...)


class RefundOrderInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: str = Field(..., min_length=1, max_length=80)
    amount: Optional[int] = Field(
        None,
        description="Monto a refundar en CENTAVOS. None = refund total.",
        ge=0,
    )
    reason: Literal[
        "requested_by_client",
        "cannot_be_fulfilled",
        "duplicate",
        "fraudulent",
        "other",
    ] = "requested_by_client"


class CreateCustomerInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=250)
    email: str = Field(..., min_length=3, max_length=254)
    phone: Optional[str] = None


class CustomerIdInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    customer_id: str = Field(..., min_length=1, max_length=80)


class PaymentLinkInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=250)
    amount: int = Field(..., ge=1, description="Monto en CENTAVOS.")
    currency: Literal["MXN", "USD"] = "MXN"
    expires_at: Optional[int] = Field(None, description="Unix timestamp.")
    allowed_payment_methods: Optional[list[Literal["card", "cash", "bank_transfer"]]] = None
    success_url: Optional[str] = None
    failure_url: Optional[str] = None


class SubscriptionCreateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str = Field(..., min_length=1, max_length=80)
    plan_id: str = Field(..., min_length=1, max_length=80)
    card_id: Optional[str] = None


class SubscriptionUpdateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str = Field(..., min_length=1, max_length=80)
    plan_id: Optional[str] = None
    card_id: Optional[str] = None


class WebhookValidateInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    headers: dict[str, str] = Field(
        ...,
        description="Headers HTTP recibidos. Se buscan 'Digest' o 'conekta-signature'.",
    )
    payload: str = Field(
        ...,
        description="Body crudo del webhook (string utf-8). Se convierte a bytes internamente.",
        max_length=200_000,
    )
    secret: str = Field(
        ...,
        description="Webhook secret del panel Conekta.",
        min_length=1,
        max_length=500,
    )
    max_age_seconds: Optional[int] = Field(
        300,
        description="Rechazar webhooks más viejos que esto. None desactiva.",
        ge=0,
    )


# ---------- tools ----------


@mcp.tool(
    annotations={
        "title": "Crear orden Conekta (con line items y customer)",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def conekta_create_order(args: CreateOrderInput) -> dict:
    """Crea una orden Conekta con line items, customer y opcionalmente charges.

    Precios en CENTAVOS enteros (Conekta no acepta decimales).

    Retorna la orden con `id`, `payment_status` y referencias de pago si
    se generaron charges offline (OXXO/SPEI).
    """
    try:
        payload: dict[str, Any] = {
            "line_items": [item.model_dump() for item in args.line_items],
            "currency": args.currency,
            "customer_info": args.customer_info.model_dump(),
        }
        if args.charges:
            payload["charges"] = [
                {"payment_method": c.model_dump(exclude_none=True)} for c in args.charges
            ]
        return await _client.create_order(payload)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Consultar orden Conekta por ID",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def conekta_get_order(args: OrderIdInput) -> dict:
    """Lee una orden por ID. Cache 2 min porque status puede cambiar."""
    try:
        return await _client.get_order(args.order_id)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Listar órdenes Conekta",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def conekta_list_orders(args: ListOrdersInput) -> dict:
    """Lista órdenes con paginación cursor (next_id). Filtra por payment_status."""
    try:
        return await _client.list_orders(
            limit=args.limit,
            next_id=args.next_id,
            payment_status=args.payment_status,
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Crear charge sobre orden existente",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def conekta_create_charge_on_order(args: ChargeOnOrderInput) -> dict:
    """Crea un charge (card / oxxo / spei) sobre una orden ya creada.

    Para OXXO/SPEI retorna la referencia para que el cliente pague offline.
    """
    try:
        return await _client.create_charge_on_order(
            args.order_id,
            {"payment_method": args.payment_method.model_dump(exclude_none=True)},
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Refund de orden Conekta (total o parcial)",
        "readOnlyHint": False,
        "destructiveHint": True,  # mueve dinero
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def conekta_refund_order(args: RefundOrderInput) -> dict:
    """Refunda una orden. amount=None = refund total. amount en centavos."""
    try:
        return await _client.refund_charge(
            order_id=args.order_id,
            amount=args.amount,
            reason=args.reason,
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Crear customer Conekta",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def conekta_create_customer(args: CreateCustomerInput) -> dict:
    """Crea cliente reutilizable para órdenes/suscripciones futuras."""
    try:
        return await _client.create_customer(args.model_dump(exclude_none=True))
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Consultar customer Conekta por ID",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def conekta_get_customer(args: CustomerIdInput) -> dict:
    try:
        return await _client.get_customer(args.customer_id)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Crear payment link (Conekta Checkout hospedado)",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def conekta_create_payment_link(args: PaymentLinkInput) -> dict:
    """Crea un Checkout Link hospedado por Conekta.

    Retorna URL pagable + ID. Cliente paga vía card/cash/bank_transfer.
    Monto en centavos.
    """
    try:
        return await _client.create_payment_link(
            name=args.name,
            amount=args.amount,
            currency=args.currency,
            expires_at=args.expires_at,
            allowed_payment_methods=args.allowed_payment_methods,
            success_url=args.success_url,
            failure_url=args.failure_url,
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Crear suscripción Conekta",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def conekta_subscription_create(args: SubscriptionCreateInput) -> dict:
    """Crea suscripción del customer a un plan."""
    try:
        return await _client.subscription_create(
            customer_id=args.customer_id, plan_id=args.plan_id, card_id=args.card_id
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Actualizar suscripción Conekta (cambio plan o tarjeta)",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def conekta_subscription_update(args: SubscriptionUpdateInput) -> dict:
    try:
        return await _client.subscription_update(
            customer_id=args.customer_id, plan_id=args.plan_id, card_id=args.card_id
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Cancelar suscripción Conekta",
        "readOnlyHint": False,
        "destructiveHint": True,  # corta el cobro recurrente
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def conekta_subscription_cancel(args: CustomerIdInput) -> dict:
    try:
        return await _client.subscription_cancel(args.customer_id)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Validar firma de webhook Conekta",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def conekta_validate_webhook(args: WebhookValidateInput) -> dict:
    """Valida la firma de un webhook Conekta (Digest o conekta-signature).

    CRÍTICO: sin esta validación, cualquiera puede mandar POSTs falsos y
    disparar acciones (timbrado CFDI, registrar pago) por eventos que no
    ocurrieron.

    Retorna `valid: true/false` + `reason` si no es válida.
    """
    result = validate_webhook_auto(
        headers=args.headers,
        payload=args.payload.encode("utf-8"),
        secret=args.secret,
        max_age_seconds=args.max_age_seconds,
    )
    return result.to_dict()


# ---------- catálogos ----------


@mcp.tool(
    annotations={
        "title": "Catálogos Conekta: status orden, métodos, eventos webhook",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def conekta_listar_catalogos() -> dict:
    """Discovery offline de catálogos Conekta."""
    return {
        "order_status": ORDER_STATUS,
        "charge_status": CHARGE_STATUS,
        "payment_method_type": PAYMENT_METHOD_TYPE,
        "charge_decline_codes": CHARGE_DECLINE_CODES,
        "currency": CURRENCY,
        "webhook_events": WEBHOOK_EVENTS,
        "subscription_status": SUBSCRIPTION_STATUS,
        "nota": (
            "Precios Conekta son ENTEROS en centavos. $100.00 MXN = 10000. "
            "Mock activo cuando CONEKTA_API_KEY ausente."
        ),
    }


# ---------- entry point ----------


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
