"""Catálogos Conekta: status de orden/charge, métodos de pago, currencies.

Origen: https://developers.conekta.com/api

⚠ Conekta cambia versiones de API con cierta frecuencia. La versión 2.1.0
es la usada por default aquí — verificar con `Accept: application/vnd.conekta-v2.1.0+json`.
"""

from __future__ import annotations


# ---------- Order / Charge Status ----------

ORDER_STATUS: dict[str, str] = {
    "pending_payment": "Orden creada, esperando pago",
    "paid": "Orden pagada totalmente",
    "partially_paid": "Orden pagada parcialmente",
    "declined": "Orden rechazada por el procesador",
    "refunded": "Orden completamente reembolsada",
    "expired": "Orden expirada sin pago",
    "canceled": "Orden cancelada manualmente",
    "unpaid": "Orden no pagada (alias usado en algunos endpoints)",
}

ORDER_STATUS_PAID = {"paid"}

ORDER_STATUS_TERMINAL = {
    "paid",
    "declined",
    "refunded",
    "expired",
    "canceled",
}

ORDER_STATUS_REFUNDABLE = {"paid", "partially_paid"}


CHARGE_STATUS: dict[str, str] = {
    "pending_payment": "Cargo pendiente de pago",
    "paid": "Cargo pagado",
    "declined": "Cargo declinado",
    "refunded": "Cargo devuelto",
    "expired": "Cargo expirado",
    "canceled": "Cargo cancelado",
    "chargeback": "Contracargo del banco",
    "pre_authorized": "Pre-autorizado (no capturado)",
}


# ---------- Payment Methods ----------

# Conekta soporta múltiples métodos en una sola orden (charges es lista)
PAYMENT_METHOD_TYPE: dict[str, str] = {
    "card": "Tarjeta de crédito o débito",
    "oxxo_cash": "OXXO Pay (efectivo en tienda)",
    "spei": "Transferencia bancaria SPEI",
    "default": "Método default del cliente guardado",
    "cashi": "Cashi Citibanamex",
    "bnpl_atrato": "Buy Now Pay Later — Atrato",
    "bnpl_kueski": "Buy Now Pay Later — KueskiPay",
}

# Métodos que generan referencia para pago offline (no inmediato)
PAYMENT_METHOD_OFFLINE = {"oxxo_cash", "spei", "cashi"}

# Métodos que requieren token de tarjeta (PCI scope)
PAYMENT_METHOD_REQUIRES_TOKEN = {"card", "default"}


# ---------- Currencies ----------

CURRENCY: dict[str, str] = {
    "MXN": "Peso Mexicano",
    "USD": "Dólar Estadounidense",
}

CURRENCY_DEFAULT = "MXN"


# ---------- Decline Codes (subset común) ----------

CHARGE_DECLINE_CODES: dict[str, str] = {
    "insufficient_funds": "Fondos insuficientes en la tarjeta",
    "invalid_cvc": "CVV/CVC inválido",
    "card_declined": "Tarjeta declinada por el banco emisor",
    "expired_card": "Tarjeta vencida",
    "lost_card": "Tarjeta reportada como perdida",
    "stolen_card": "Tarjeta reportada como robada",
    "processing_error": "Error de procesamiento",
    "incorrect_number": "Número de tarjeta incorrecto",
    "incorrect_zip": "CP incorrecto (AVS rechazado)",
    "currency_not_supported": "Moneda no soportada por la tarjeta",
    "fraudulent": "Rechazado por sistema antifraude",
    "issuer_not_available": "Banco emisor no disponible",
    "suspected_fraud": "Sospecha de fraude",
}


# ---------- Webhook Event Types (subset relevante) ----------

WEBHOOK_EVENTS: dict[str, str] = {
    "charge.created": "Cargo creado",
    "charge.paid": "Cargo pagado",
    "charge.pending_payment": "Cargo creado, esperando pago",
    "charge.declined": "Cargo declinado",
    "charge.refunded": "Cargo devuelto",
    "charge.expired": "Cargo expirado",
    "charge.canceled": "Cargo cancelado",
    "charge.chargeback.created": "Contracargo iniciado",
    "charge.chargeback.under_review": "Contracargo en revisión",
    "charge.chargeback.lost": "Contracargo perdido (dinero retirado)",
    "charge.chargeback.won": "Contracargo ganado (dinero retenido)",
    "order.paid": "Orden completamente pagada",
    "order.canceled": "Orden cancelada",
    "order.expired": "Orden expirada",
    "order.pending_payment": "Orden creada, esperando pago",
    "order.partially_refunded": "Orden devuelta parcialmente",
    "order.refunded": "Orden devuelta totalmente",
    "subscription.created": "Suscripción creada",
    "subscription.paid": "Suscripción cobrada exitosamente",
    "subscription.payment_failed": "Cobro de suscripción falló",
    "subscription.canceled": "Suscripción cancelada",
    "subscription.expired": "Suscripción expirada",
    "subscription.paused": "Suscripción pausada",
    "subscription.resumed": "Suscripción reanudada",
    "customer.created": "Cliente creado",
    "customer.updated": "Cliente actualizado",
    "customer.deleted": "Cliente eliminado",
    "payout.created": "Payout (dispersión) creado",
    "payout.paid": "Payout pagado",
}


# ---------- Subscription Status ----------

SUBSCRIPTION_STATUS: dict[str, str] = {
    "in_trial": "En periodo de prueba",
    "active": "Activa, cobrando periódicamente",
    "past_due": "Pago atrasado — siguiendo política de reintentos",
    "paused": "Pausada (no cobra hasta reanudar)",
    "canceled": "Cancelada definitivamente",
    "expired": "Expirada (max_billing_attempts agotados)",
}


# ---------- helpers ----------


def describe_order_status(status: str) -> str | None:
    return ORDER_STATUS.get(status)


def is_order_paid(status: str) -> bool:
    return status in ORDER_STATUS_PAID


def is_order_terminal(status: str) -> bool:
    return status in ORDER_STATUS_TERMINAL


def is_order_refundable(status: str) -> bool:
    return status in ORDER_STATUS_REFUNDABLE


def describe_decline_code(code: str) -> str:
    return CHARGE_DECLINE_CODES.get(code, f"Razón desconocida: {code}")
