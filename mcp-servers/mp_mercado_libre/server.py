"""mp_mercado_libre — marketplace dominante en LATAM (~50% e-commerce MX).

Cubre el flujo crítico de un seller activo: leer listings, actualizar precio
y stock (para sincronizar con otros canales), responder preguntas pre-venta,
gestionar mensajes post-venta, consultar órdenes y reputación.

OAuth 2.0 con refresh automático. Sin credenciales corre en modo mock con
IDs determinísticos y datos plausibles (3 listings, status según paridad
del último dígito del ID, etc.).

⚠ Sin MCP oficial — esta es la implementación propia que llena el gap.
"""

from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

# Make sibling packages importable
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_mercado_libre.catalogos import (  # noqa: E402
    CURRENCY,
    ITEM_CONDITION,
    ITEM_STATUS,
    LISTING_TYPE,
    MESSAGE_FROM,
    ORDER_STATUS,
    QUESTION_STATUS,
    SHIPMENT_STATUS,
    SITE_ID,
    is_item_reactivable,
    is_item_terminal,
    is_order_paid,
    is_order_terminal,
    is_shipment_awaiting_seller,
    is_shipment_delivered,
    is_shipment_in_transit,
)
from mp_mercado_libre.client import MercadoLibreClient  # noqa: E402
from shared.errors import McpError  # noqa: E402


mcp = FastMCP("mercadolibre_mcp")
_client = MercadoLibreClient()


# ---------- enums ----------


class ItemStatus(str, Enum):
    active = "active"
    paused = "paused"
    closed = "closed"
    under_review = "under_review"
    inactive = "inactive"


class OrderStatus(str, Enum):
    confirmed = "confirmed"
    payment_required = "payment_required"
    payment_in_process = "payment_in_process"
    partially_paid = "partially_paid"
    paid = "paid"
    cancelled = "cancelled"


class QuestionStatus(str, Enum):
    UNANSWERED = "UNANSWERED"
    ANSWERED = "ANSWERED"
    CLOSED_UNANSWERED = "CLOSED_UNANSWERED"


# ---------- input models ----------


class ListItemsInput(BaseModel):
    """Filtros para listar items del seller."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    seller_id: Optional[int] = Field(
        default=None,
        description="ID del seller. Si se omite, usa el seller dueño del refresh_token (vía /users/me).",
    )
    status: Optional[ItemStatus] = Field(
        default=None, description="Filtrar por estado del listing."
    )
    limit: int = Field(default=50, ge=1, le=100, description="Máximo de resultados por página.")
    offset: int = Field(default=0, ge=0, description="Offset para paginación.")


class GetItemInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    item_id: str = Field(
        ...,
        description="ID del listing en formato 'MLM<digits>' (México) o equivalente para otros sites.",
        pattern=r"^M[A-Z]{2}\d{6,}$",
    )


class UpdateStockInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    item_id: str = Field(
        ...,
        description="ID del listing.",
        pattern=r"^M[A-Z]{2}\d{6,}$",
    )
    available_quantity: int = Field(
        ..., description="Nueva cantidad disponible.", ge=0
    )


class UpdatePriceInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    item_id: str = Field(
        ...,
        description="ID del listing.",
        pattern=r"^M[A-Z]{2}\d{6,}$",
    )
    price: float = Field(..., description="Nuevo precio en la moneda del listing.", gt=0)


class ToggleStatusInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    item_id: str = Field(
        ...,
        description="ID del listing.",
        pattern=r"^M[A-Z]{2}\d{6,}$",
    )


class ListOrdersInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    seller_id: Optional[int] = Field(default=None, description="ID del seller (default: el del token).")
    status: Optional[OrderStatus] = Field(default=None, description="Filtrar por status de orden.")
    fecha_desde: Optional[str] = Field(
        default=None,
        description="Fecha desde ISO 8601 (ej. '2026-03-01T00:00:00.000-06:00').",
    )
    fecha_hasta: Optional[str] = Field(
        default=None, description="Fecha hasta ISO 8601."
    )
    limit: int = Field(default=50, ge=1, le=100, description="Máximo de resultados.")
    offset: int = Field(default=0, ge=0, description="Offset para paginación.")


class OrderIdInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    order_id: str = Field(..., description="ID de la orden.", min_length=1)


class ListMessagesInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    pack_id: str = Field(
        ...,
        description="ID del 'pack' (conversación post-venta). Lo obtienes de la orden.",
        min_length=1,
    )
    seller_id: Optional[int] = Field(default=None, description="ID del seller.")
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class SendMessageInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    pack_id: str = Field(..., description="ID del pack donde enviar el mensaje.", min_length=1)
    buyer_id: int = Field(..., description="ID del comprador.", ge=1)
    text: str = Field(
        ...,
        description="Texto del mensaje. ML tiene reglas de moderación — evita compartir contactos externos.",
        min_length=1,
        max_length=2000,
    )
    seller_id: Optional[int] = Field(default=None, description="ID del seller.")


class ListQuestionsInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    item_id: Optional[str] = Field(
        default=None,
        description="Filtrar por listing específico. Si se omite, todas las preguntas del seller.",
        pattern=r"^M[A-Z]{2}\d{6,}$",
    )
    status: QuestionStatus = Field(
        default=QuestionStatus.UNANSWERED,
        description="Default 'UNANSWERED' — preguntas pendientes de responder.",
    )
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class AnswerQuestionInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    question_id: int = Field(..., description="ID de la pregunta.", ge=1)
    text: str = Field(
        ...,
        description="Texto de la respuesta. Aplica moderación ML (no contactos externos).",
        min_length=1,
        max_length=2000,
    )


class SellerIdInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    seller_id: Optional[int] = Field(default=None, description="ID del seller (default: el del token).")


# ---------- tools ----------


@mcp.tool(
    name="mercadolibre_get_me",
    annotations={
        "title": "Identificar al seller (whose token we hold)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def mercadolibre_get_me() -> dict:
    """Identifica al seller dueño del refresh_token actual.

    Útil para descubrir el seller_id que después pasas a otros tools.
    Cache 24h.
    """
    try:
        return await _client.get_me()
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="mercadolibre_list_items",
    annotations={
        "title": "Listar items del seller",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def mercadolibre_list_items(params: ListItemsInput) -> dict:
    """Lista los items del seller con paginación.

    Args:
        params:
            - seller_id (opcional): si se omite, usa el dueño del token
            - status (opcional): filtra por active/paused/closed/etc.
            - limit (1-100), offset

    Returns:
        {results: [item_ids], paging: {total, limit, offset}, items_preview: [...]}
    """
    try:
        return await _client.list_items(
            seller_id=params.seller_id,
            status=params.status.value if params.status else None,
            limit=params.limit,
            offset=params.offset,
        )
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="mercadolibre_get_item",
    annotations={
        "title": "Detalle completo de un listing",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def mercadolibre_get_item(params: GetItemInput) -> dict:
    """Obtiene el detalle completo de un listing por ID (MLM...).

    Enriquece con campos derivados:
        is_reactivable: bool   — true si está pausado y puede reactivarse
        is_terminal: bool      — true si closed/inactive (no se puede recuperar)
        status_description: str  — descripción del status en español
    """
    try:
        item = await _client.get_item(params.item_id)
        if "error" not in item:
            status = item.get("status", "")
            item["is_reactivable"] = is_item_reactivable(status)
            item["is_terminal"] = is_item_terminal(status)
            item["status_description"] = ITEM_STATUS.get(status, "Estatus desconocido")
        return item
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="mercadolibre_update_stock",
    annotations={
        "title": "Actualizar inventario disponible de un listing",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def mercadolibre_update_stock(params: UpdateStockInput) -> dict:
    """Cambia la cantidad disponible de un listing.

    Caso de uso típico: sincronizar inventario entre canales (Shopify, físico, MELI).
    """
    try:
        return await _client.update_item(
            params.item_id, {"available_quantity": params.available_quantity}
        )
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="mercadolibre_update_price",
    annotations={
        "title": "Actualizar precio de un listing",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def mercadolibre_update_price(params: UpdatePriceInput) -> dict:
    """Cambia el precio de un listing.

    Si el item tiene variaciones, este tool actualiza el precio "base"; para
    variaciones específicas hace falta endpoint distinto (no implementado).
    """
    try:
        return await _client.update_item(params.item_id, {"price": params.price})
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="mercadolibre_pause_item",
    annotations={
        "title": "Pausar un listing (queda fuera de búsqueda)",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def mercadolibre_pause_item(params: ToggleStatusInput) -> dict:
    """Pausa un listing — desaparece de búsquedas pero puede reactivarse.

    Útil para retirar temporalmente un producto sin perder el historial.
    """
    try:
        return await _client.update_item(params.item_id, {"status": "paused"})
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="mercadolibre_activate_item",
    annotations={
        "title": "Reactivar un listing pausado",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def mercadolibre_activate_item(params: ToggleStatusInput) -> dict:
    """Reactiva un listing pausado.

    No funciona en listings 'closed' (esos están terminados, hay que crear uno nuevo).
    """
    try:
        return await _client.update_item(params.item_id, {"status": "active"})
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="mercadolibre_list_orders",
    annotations={
        "title": "Listar órdenes del seller con filtros",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def mercadolibre_list_orders(params: ListOrdersInput) -> dict:
    """Lista órdenes con filtros: status, rango fechas, paginación."""
    try:
        return await _client.list_orders(
            seller_id=params.seller_id,
            status=params.status.value if params.status else None,
            fecha_desde=params.fecha_desde,
            fecha_hasta=params.fecha_hasta,
            limit=params.limit,
            offset=params.offset,
        )
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="mercadolibre_get_order",
    annotations={
        "title": "Detalle de una orden",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def mercadolibre_get_order(params: OrderIdInput) -> dict:
    """Detalle completo de orden + campos derivados (is_paid, is_terminal, ...)."""
    try:
        order = await _client.get_order(params.order_id)
        if "error" not in order:
            status = order.get("status", "")
            order["is_paid"] = is_order_paid(status)
            order["is_terminal"] = is_order_terminal(status)
            order["status_description"] = ORDER_STATUS.get(status, "Estatus desconocido")
        return order
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="mercadolibre_list_messages",
    annotations={
        "title": "Listar mensajes de una conversación (post-venta)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def mercadolibre_list_messages(params: ListMessagesInput) -> dict:
    """Lista mensajes en un pack (conversación post-venta).

    El pack_id lo obtienes del campo order.pack_id en la orden.
    """
    try:
        return await _client.list_messages(
            pack_id=params.pack_id,
            seller_id=params.seller_id,
            limit=params.limit,
            offset=params.offset,
        )
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="mercadolibre_send_message",
    annotations={
        "title": "Enviar mensaje al comprador en una conversación",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def mercadolibre_send_message(params: SendMessageInput) -> dict:
    """Envía un mensaje al comprador en un pack post-venta.

    ⚠ Moderación de ML: NO compartir números de teléfono, emails, links a
    sitios externos en el mensaje. ML banea cuentas que evaden plataforma.
    """
    try:
        return await _client.send_message(
            pack_id=params.pack_id,
            buyer_id=params.buyer_id,
            text=params.text,
            seller_id=params.seller_id,
        )
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="mercadolibre_list_questions",
    annotations={
        "title": "Listar preguntas pre-venta",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def mercadolibre_list_questions(params: ListQuestionsInput) -> dict:
    """Lista preguntas pre-venta sobre los listings.

    Default: status=UNANSWERED (las que requieren tu atención).
    """
    try:
        return await _client.list_questions(
            item_id=params.item_id,
            status=params.status.value,
            limit=params.limit,
            offset=params.offset,
        )
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="mercadolibre_answer_question",
    annotations={
        "title": "Responder una pregunta pre-venta",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def mercadolibre_answer_question(params: AnswerQuestionInput) -> dict:
    """Responde una pregunta. Misma moderación ML que en mensajes."""
    try:
        return await _client.answer_question(params.question_id, params.text)
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="mercadolibre_get_seller_reputation",
    annotations={
        "title": "Reputación + métricas del seller",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def mercadolibre_get_seller_reputation(params: SellerIdInput) -> dict:
    """Métricas del seller: level (1-5), power_seller status, transacciones,
    tasa de reclamos, demoras, cancelaciones.

    Útil para monitorear health de la cuenta y detectar problemas temprano.
    Cache 30 min.
    """
    try:
        return await _client.get_seller_reputation(params.seller_id)
    except McpError as err:
        return err.to_dict()


@mcp.tool(
    name="mercadolibre_listar_catalogos",
    annotations={
        "title": "Catálogos: estados de item/orden/envío/pregunta, sites, monedas",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def mercadolibre_listar_catalogos() -> dict:
    """Discovery sin red de los catálogos que este MCP conoce."""
    return {
        "item_status": ITEM_STATUS,
        "item_condition": ITEM_CONDITION,
        "listing_type": LISTING_TYPE,
        "order_status": ORDER_STATUS,
        "shipment_status": SHIPMENT_STATUS,
        "question_status": QUESTION_STATUS,
        "message_from": MESSAGE_FROM,
        "site_id": SITE_ID,
        "currency": CURRENCY,
        "advertencia_vigencia": (
            "Catálogos extraídos al momento del training. ML ocasionalmente añade "
            "subestados y ajusta enums. Validar contra docs vigentes si surge un valor desconocido."
        ),
    }


# ---------- entry point ----------


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
