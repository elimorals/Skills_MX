"""mp_mercado_pago — pasarela de pagos LATAM con webhook validation.

Cubre el flujo crítico: crear payment link, recibir pago, validar
webhook firmado, consultar estatus, hacer refunds, cancelar pendientes.

La validación de firma de webhook (mercadopago_validate_webhook_signature)
es CRÍTICA — sin ella, cualquiera puede mandar POSTs falsos al endpoint
y disparar emisión de CFDIs por pagos que nunca ocurrieron.

Sin MERCADOPAGO_ACCESS_TOKEN corre en modo mock con preference_ids
determinísticos (sha256 del payload) — mismo input siempre regresa mismo id.
"""

from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Make sibling packages importable
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_mercado_pago.catalogos import (  # noqa: E402
    CURRENCY,
    PAYMENT_STATUS,
    PAYMENT_STATUS_DETAIL,
    REFUND_STATUS,
    SUBSCRIPTION_STATUS,
    WEBHOOK_TOPICS,
    is_payment_paid,
    is_payment_refundable,
    is_payment_terminal,
)
from mp_mercado_pago.client import MercadoPagoClient  # noqa: E402
from mp_mercado_pago.webhooks import (  # noqa: E402
    parse_signature_header,
    validate_webhook_signature,
)
from shared.errors import McpError  # noqa: E402


mcp = FastMCP("mercadopago_mcp")
_client = MercadoPagoClient()


# ---------- enums ----------


class CurrencyMP(str, Enum):
    """Monedas soportadas en MX."""

    MXN = "MXN"
    USD = "USD"


class PaymentStatusEnum(str, Enum):
    """Estados de pago para filtrado."""

    pending = "pending"
    approved = "approved"
    authorized = "authorized"
    in_process = "in_process"
    rejected = "rejected"
    cancelled = "cancelled"
    refunded = "refunded"


# ---------- input models ----------


class Item(BaseModel):
    """Un ítem dentro de una preferencia Mercado Pago."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="allow")

    title: str = Field(
        ..., description="Nombre visible del item (ej. 'Consultoría 1 hora').", min_length=1, max_length=256
    )
    quantity: int = Field(..., description="Cantidad de unidades.", ge=1)
    unit_price: float = Field(..., description="Precio unitario en la moneda especificada.", gt=0)
    currency_id: CurrencyMP = Field(default=CurrencyMP.MXN, description="Código ISO de moneda.")
    id: Optional[str] = Field(default=None, description="ID interno del item (SKU, etc.). Opcional.")
    description: Optional[str] = Field(default=None, description="Descripción extendida del item.")


class CreatePreferenceInput(BaseModel):
    """Input para crear un payment link (preference)."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    items: list[Item] = Field(
        ..., description="Lista de items a cobrar. Mínimo uno.", min_length=1
    )
    payer_email: Optional[str] = Field(
        default=None,
        description="Email del pagador. Si se provee, MP pre-llena el checkout.",
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
    )
    external_reference: Optional[str] = Field(
        default=None,
        description="Tu identificador interno (ej. ID de la cotización o factura). "
        "Aparece en webhooks → úsalo para mapear pagos a operaciones internas.",
        max_length=256,
    )
    notification_url: Optional[str] = Field(
        default=None,
        description="URL HTTPS pública donde MP enviará webhooks de cambios. "
        "Debe responder 200 OK rápido o MP reintenta.",
    )
    back_url_success: Optional[str] = Field(
        default=None, description="URL a redirigir al pagador tras éxito."
    )
    back_url_failure: Optional[str] = Field(
        default=None, description="URL a redirigir al pagador tras rechazo."
    )
    back_url_pending: Optional[str] = Field(
        default=None, description="URL a redirigir cuando el pago queda pendiente."
    )
    expires: bool = Field(
        default=False, description="Si True, la preferencia expira en expiration_date_to."
    )
    expiration_date_to: Optional[str] = Field(
        default=None,
        description="ISO 8601 con timezone. Solo aplica si expires=True. Ej. '2026-04-15T23:59:59.000-06:00'.",
    )


class PaymentIdInput(BaseModel):
    """Input genérico que requiere un payment_id."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    payment_id: str = Field(
        ..., description="ID del pago en Mercado Pago (numérico o string).", min_length=1
    )


class PreferenceIdInput(BaseModel):
    """Input genérico que requiere un preference_id."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    preference_id: str = Field(
        ..., description="ID de la preferencia (devuelto por create_preference).", min_length=1
    )


class ListPaymentsInput(BaseModel):
    """Filtros para buscar pagos."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    external_reference: Optional[str] = Field(
        default=None,
        description="Filtrar por tu identificador interno (asociado con create_preference).",
    )
    status: Optional[PaymentStatusEnum] = Field(
        default=None, description="Filtrar por estatus del pago."
    )
    fecha_desde: Optional[str] = Field(
        default=None,
        description="Fecha mínima de creación ISO 8601 (ej. '2026-03-01T00:00:00.000-06:00').",
    )
    fecha_hasta: Optional[str] = Field(
        default=None, description="Fecha máxima de creación ISO 8601."
    )
    limit: int = Field(default=50, ge=1, le=100, description="Máximo de resultados.")
    offset: int = Field(default=0, ge=0, description="Offset para paginación.")


class RefundPaymentInput(BaseModel):
    """Input para refund total o parcial."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    payment_id: str = Field(..., description="ID del pago a reembolsar.", min_length=1)
    amount: Optional[float] = Field(
        default=None,
        description="Monto a reembolsar. Si se omite, es refund TOTAL. Para parcial: especifica monto menor al original.",
        gt=0,
    )


class ValidateWebhookInput(BaseModel):
    """Input para validar firma de webhook entrante."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    x_signature: str = Field(
        ...,
        description="Valor crudo del header 'x-signature' (formato: 'ts=...,v1=...').",
    )
    x_request_id: str = Field(..., description="Valor del header 'x-request-id'.")
    data_id: str = Field(
        ...,
        description="ID del recurso notificado (típicamente del query string '?data.id=...' "
        "o del body 'data.id').",
    )
    secret: str = Field(
        ...,
        description="Webhook secret del panel MP (no es el access_token). "
        "Configúralo en el panel de la app de MP.",
    )
    max_age_seconds: Optional[int] = Field(
        default=300,
        description="Si se pasa, rechaza webhooks con timestamp más viejo. Defaults a 5 min (anti-replay).",
        ge=0,
    )


# ---------- tools ----------


@mcp.tool(
    name="mercadopago_create_preference",
    annotations={
        "title": "Crear payment link (preference) — Checkout Pro",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def mercadopago_create_preference(params: CreatePreferenceInput) -> dict:
    """Crea una preferencia de pago y devuelve URL pública (init_point) para enviar al cliente.

    El flujo típico:
    1. Llamas a este tool con los items y external_reference (tu ID interno)
    2. Mandas init_point al cliente vía WhatsApp/email
    3. Cliente paga
    4. MP dispara webhook a tu notification_url
    5. Validas webhook con mercadopago_validate_webhook_signature
    6. Consultas el pago con mercadopago_get_payment para obtener el monto y status
    7. Si status=approved, disparas timbrado CFDI con mp_facturama_extendido

    Args:
        params (CreatePreferenceInput):
            - items: lista de {title, quantity, unit_price, currency_id}
            - payer_email: para pre-llenar checkout (opcional)
            - external_reference: TU id interno para mapeo (recomendado)
            - notification_url: URL HTTPS para webhooks
            - back_url_success/failure/pending: redirects post-pago
            - expires + expiration_date_to: para preferencias con caducidad

    Returns:
        {
            "preference_id": "1234567-...",
            "init_point": "https://www.mercadopago.com.mx/checkout/...",  # producción
            "sandbox_init_point": "https://sandbox.mercadopago.com.mx/...",
            "external_reference": "...",
            "date_created": "...",
            "simulated": bool
        }
    """
    try:
        # Build the preference body in MP's format
        preference = {
            "items": [item.model_dump(exclude_none=True) for item in params.items],
        }
        if params.payer_email:
            preference["payer"] = {"email": params.payer_email}
        if params.external_reference:
            preference["external_reference"] = params.external_reference
        if params.notification_url:
            preference["notification_url"] = params.notification_url

        back_urls = {}
        if params.back_url_success:
            back_urls["success"] = params.back_url_success
        if params.back_url_failure:
            back_urls["failure"] = params.back_url_failure
        if params.back_url_pending:
            back_urls["pending"] = params.back_url_pending
        if back_urls:
            preference["back_urls"] = back_urls
            # auto_return triggers automatic redirect after approval
            preference["auto_return"] = "approved"

        if params.expires:
            preference["expires"] = True
            if params.expiration_date_to:
                preference["expiration_date_to"] = params.expiration_date_to

        result = await _client.create_preference(preference)
        return result
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="mercadopago_get_preference",
    annotations={
        "title": "Leer una preferencia ya creada",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def mercadopago_get_preference(params: PreferenceIdInput) -> dict:
    """Lee el detalle de una preferencia por su ID. Cache 15 min."""
    try:
        return await _client.get_preference(params.preference_id)
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="mercadopago_get_payment",
    annotations={
        "title": "Consultar un pago por ID",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def mercadopago_get_payment(params: PaymentIdInput) -> dict:
    """Obtiene el detalle de un pago: status, monto, método, payer.

    Incluye campos derivados útiles:
        is_paid: bool          — true si status=approved
        is_terminal: bool      — true si status ya no va a cambiar
        is_refundable: bool    — true si todavía se puede refund
        status_description: str  — descripción en español del status
    """
    try:
        payment = await _client.get_payment(params.payment_id)
        # Enrich with derived flags
        status = payment.get("status", "")
        payment["is_paid"] = is_payment_paid(status)
        payment["is_terminal"] = is_payment_terminal(status)
        payment["is_refundable"] = is_payment_refundable(status)
        payment["status_description"] = PAYMENT_STATUS.get(status, "Estatus desconocido")
        return payment
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="mercadopago_list_payments",
    annotations={
        "title": "Buscar pagos con filtros",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def mercadopago_list_payments(params: ListPaymentsInput) -> dict:
    """Busca pagos por filtros: external_reference, status, rango fechas.

    Útil para reconciliar — "¿qué pagos llegaron por el external_reference X?".
    """
    try:
        return await _client.list_payments(
            external_reference=params.external_reference,
            status=params.status.value if params.status else None,
            fecha_desde=params.fecha_desde,
            fecha_hasta=params.fecha_hasta,
            limit=params.limit,
            offset=params.offset,
        )
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="mercadopago_refund_payment",
    annotations={
        "title": "Reembolsar un pago (total o parcial)",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def mercadopago_refund_payment(params: RefundPaymentInput) -> dict:
    """Reembolsa un pago aprobado.

    Sin `amount` → refund TOTAL. Con `amount` → refund PARCIAL del monto
    especificado (debe ser menor al monto total del pago).

    El status del pago original cambia a `refunded` (total) o se mantiene
    en `approved` con una entrada en refunds[] (parcial).

    Recordatorio fiscal: tras un refund debes emitir CFDI tipo E (Egreso)
    con TipoRelacion 01 vinculado al CFDI original. El workflow típico:
    payment.refunded webhook → emitir CFDI E con cfdi-emision skill.
    """
    try:
        result = await _client.refund_payment(params.payment_id, amount=params.amount)
        return result
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="mercadopago_cancel_payment",
    annotations={
        "title": "Cancelar un pago pendiente",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def mercadopago_cancel_payment(params: PaymentIdInput) -> dict:
    """Cancela un pago en status=pending. No funciona en pagos ya aprobados.

    Para revertir un pago aprobado, usa mercadopago_refund_payment.
    """
    try:
        return await _client.cancel_payment(params.payment_id)
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="mercadopago_validate_webhook_signature",
    annotations={
        "title": "Validar firma HMAC de webhook entrante (CRÍTICO PARA SEGURIDAD)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def mercadopago_validate_webhook_signature(params: ValidateWebhookInput) -> dict:
    """Valida la firma HMAC-SHA256 de un webhook entrante de Mercado Pago.

    CRÍTICO: SIN esta validación, cualquiera puede mandar POSTs falsos al
    endpoint y disparar emisión de CFDIs por pagos que nunca ocurrieron.

    Algoritmo oficial MP:
    1. Headers entrantes: x-signature (ts=...,v1=...) y x-request-id
    2. Manifest: 'id:<data_id>;request-id:<x_request_id>;ts:<ts>;'
    3. HMAC-SHA256(manifest, secret).hexdigest() debe igualar v1=...
    4. Opcional: rechazar si ts es más viejo que max_age_seconds (anti-replay)

    Args:
        params (ValidateWebhookInput):
            - x_signature: header crudo 'x-signature'
            - x_request_id: header 'x-request-id'
            - data_id: ID del recurso del query string '?data.id=...' o body
            - secret: webhook secret del panel MP
            - max_age_seconds: anti-replay window (default 300s, None desactiva)

    Returns:
        {
            "valid": bool,
            "reason": "..." | null,   # null si valid; código si no
            "timestamp": int | null,
            "data_id": "..."
        }

    Reasons posibles cuando NO es válido:
        - "missing_signature_header"
        - "malformed_signature_header"
        - "missing_secret" / "missing_request_id" / "missing_data_id"
        - "hmac_mismatch" (firma no coincide → posible spoof)
        - "expired_timestamp" (anti-replay)
    """
    try:
        result = validate_webhook_signature(
            x_signature=params.x_signature,
            x_request_id=params.x_request_id,
            data_id=params.data_id,
            secret=params.secret,
            max_age_seconds=params.max_age_seconds,
        )
        return result.to_dict()
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="mercadopago_listar_catalogos",
    annotations={
        "title": "Catálogos MP: estados, métodos, monedas, topics webhooks",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def mercadopago_listar_catalogos() -> dict:
    """Catálogos MP que este MCP conoce. Útil para discovery del agente."""
    return {
        "payment_status": PAYMENT_STATUS,
        "payment_status_detail": PAYMENT_STATUS_DETAIL,
        "refund_status": REFUND_STATUS,
        "subscription_status": SUBSCRIPTION_STATUS,
        "webhook_topics": WEBHOOK_TOPICS,
        "currency": CURRENCY,
        "advertencia_vigencia": (
            "Catálogos extraídos al momento del training. Mercado Pago raramente "
            "cambia estos enums pero validar contra docs vigentes si surge un valor desconocido."
        ),
    }


# ---------- entry point ----------


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
