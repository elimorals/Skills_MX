"""Catálogos de Mercado Libre: estados de listing, orden, envío, condición.

Origen: https://developers.mercadolibre.com.mx

⚠ Datos a verificar vigentes antes de producción: ML añade subestados y
ajusta enums ocasionalmente. Validar contra docs vigentes si surge un
valor desconocido.
"""

from __future__ import annotations

# ---------- Estados de un Item (listing) ----------

ITEM_STATUS: dict[str, str] = {
    "active": "Publicación activa y visible",
    "paused": "Pausada por el vendedor (no aparece en búsquedas)",
    "closed": "Cerrada permanentemente (no se puede reactivar)",
    "under_review": "Bajo revisión de ML antes de publicar",
    "inactive": "Inactiva por motivos de calidad o policy",
    "payment_required": "Requiere pago de fee para activarse",
    "not_yet_active": "Aún no activa (en proceso de publicación)",
}

# Estados desde donde un item puede ser reactivado
ITEM_STATUS_REACTIVABLE = {"paused"}

# Estados terminales — no van a cambiar más
ITEM_STATUS_TERMINAL = {"closed", "inactive"}


# ---------- Condition de un Item ----------

ITEM_CONDITION: dict[str, str] = {
    "new": "Nuevo",
    "used": "Usado",
    "not_specified": "Sin especificar",
    "refurbished": "Reacondicionado",
}


# ---------- Listing types (categorías de exposición) ----------

LISTING_TYPE: dict[str, str] = {
    "free": "Gratuita — exposición limitada, sin cargo por venta",
    "bronze": "Bronce — exposición media, comisión normal",
    "silver": "Plata — exposición alta",
    "gold": "Oro — exposición alta + mensualidades sin interés",
    "gold_special": "Oro especial — máxima exposición + MSI",
    "gold_premium": "Oro premium — exposición especial promocionada",
    "gold_pro": "Oro pro — máxima exposición + promociones",
}


# ---------- Estados de Order ----------

ORDER_STATUS: dict[str, str] = {
    "confirmed": "Confirmada (comprador completó la compra)",
    "payment_required": "Esperando que el comprador pague",
    "payment_in_process": "Pago iniciado pero no acreditado",
    "partially_paid": "Pago parcial recibido",
    "paid": "Pago acreditado completamente",
    "cancelled": "Cancelada (por comprador, vendedor o sistema)",
    "invalid": "Orden inválida",
}

ORDER_STATUS_PAID = {"paid", "partially_paid"}
ORDER_STATUS_TERMINAL = {"paid", "cancelled", "invalid"}


# ---------- Estados de Shipment ----------

SHIPMENT_STATUS: dict[str, str] = {
    "to_be_agreed": "Por acordar entre vendedor y comprador",
    "pending": "Pendiente — vendedor debe imprimir etiqueta",
    "handling": "Vendedor preparando envío",
    "ready_to_ship": "Listo para ser entregado a la paquetería",
    "shipped": "En tránsito",
    "delivered": "Entregado al destinatario",
    "not_delivered": "No entregado (intentos fallidos)",
    "cancelled": "Cancelado",
    "returned": "Devuelto al vendedor",
}

SHIPMENT_STATUS_DELIVERED = {"delivered"}
SHIPMENT_STATUS_IN_TRANSIT = {"shipped"}
SHIPMENT_STATUS_AWAITING_SELLER = {"pending", "handling", "ready_to_ship"}


# ---------- Tipos de mensaje (en post-venta) ----------

MESSAGE_FROM: dict[str, str] = {
    "buyer": "Mensaje del comprador",
    "seller": "Mensaje del vendedor (tú)",
    "system": "Mensaje automático de Mercado Libre",
}


# ---------- Estados de Question (pre-venta) ----------

QUESTION_STATUS: dict[str, str] = {
    "UNANSWERED": "Sin responder — requiere atención del vendedor",
    "ANSWERED": "Ya respondida",
    "CLOSED_UNANSWERED": "Cerrada sin respuesta (item ya no disponible)",
    "UNDER_REVIEW": "En revisión por ML",
    "BANNED": "Pregunta bloqueada por contenido inadecuado",
    "DELETED": "Eliminada",
}


# ---------- Sites soportados (MX foco) ----------

SITE_ID: dict[str, str] = {
    "MLM": "Mercado Libre México",
    "MLB": "Mercado Libre Brasil",
    "MLA": "Mercado Libre Argentina",
    "MLC": "Mercado Libre Chile",
    "MCO": "Mercado Libre Colombia",
    "MPE": "Mercado Libre Perú",
    "MLU": "Mercado Libre Uruguay",
    "MLV": "Mercado Libre Venezuela",
}


# ---------- Currency ----------

CURRENCY: dict[str, str] = {
    "MXN": "Peso Mexicano",
    "USD": "Dólar Estadounidense",
    "BRL": "Real Brasileño",
    "ARS": "Peso Argentino",
}


# ---------- helpers ----------


def describe_item_status(status: str) -> str | None:
    return ITEM_STATUS.get(status)


def is_item_reactivable(status: str) -> bool:
    return status in ITEM_STATUS_REACTIVABLE


def is_item_terminal(status: str) -> bool:
    return status in ITEM_STATUS_TERMINAL


def is_order_paid(status: str) -> bool:
    return status in ORDER_STATUS_PAID


def is_order_terminal(status: str) -> bool:
    return status in ORDER_STATUS_TERMINAL


def is_shipment_delivered(status: str) -> bool:
    return status in SHIPMENT_STATUS_DELIVERED


def is_shipment_in_transit(status: str) -> bool:
    return status in SHIPMENT_STATUS_IN_TRANSIT


def is_shipment_awaiting_seller(status: str) -> bool:
    return status in SHIPMENT_STATUS_AWAITING_SELLER
