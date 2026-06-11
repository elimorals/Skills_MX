"""Catálogos de Mercado Pago: estados, métodos, tipos de notificación.

Origen: https://www.mercadopago.com.mx/developers/es/reference

⚠ Datos a verificar vigentes antes de producción: Mercado Pago raramente
cambia estos enums (estables desde 2018+), pero validar con docs vigentes
si surge un valor desconocido.
"""

from __future__ import annotations

# ---------- Payment Status ----------

PAYMENT_STATUS: dict[str, str] = {
    "pending": "Pago iniciado pero no procesado",
    "approved": "Pago aprobado y acreditado",
    "authorized": "Pago autorizado pero no capturado (solo TDC)",
    "in_process": "Pago en revisión (manual o antifraude)",
    "in_mediation": "Pago en disputa entre comprador/vendedor",
    "rejected": "Pago rechazado (insuficientes fondos, antifraude, etc.)",
    "cancelled": "Pago cancelado por el comprador o expirado",
    "refunded": "Pago devuelto total",
    "charged_back": "Contracargo del banco emisor",
}

# Statuses que indican que el dinero está disponible para el vendedor
PAYMENT_STATUS_PAID = {"approved"}

# Statuses terminales — no van a cambiar más
PAYMENT_STATUS_TERMINAL = {
    "approved",
    "rejected",
    "cancelled",
    "refunded",
    "charged_back",
}

# Statuses donde un refund todavía tiene sentido
PAYMENT_STATUS_REFUNDABLE = {"approved", "authorized"}


# ---------- Payment Status Detail (más fino que status) ----------

PAYMENT_STATUS_DETAIL: dict[str, str] = {
    "accredited": "Aprobado y acreditado",
    "pending_contingency": "Procesando — espera",
    "pending_review_manual": "En revisión manual antifraude",
    "cc_rejected_bad_filled_card_number": "TDC: número incorrecto",
    "cc_rejected_bad_filled_date": "TDC: fecha vencimiento incorrecta",
    "cc_rejected_bad_filled_other": "TDC: datos incorrectos",
    "cc_rejected_bad_filled_security_code": "TDC: CVV incorrecto",
    "cc_rejected_blacklist": "TDC: en lista negra MP",
    "cc_rejected_call_for_authorize": "TDC: cliente debe autorizar con banco",
    "cc_rejected_card_disabled": "TDC: tarjeta deshabilitada",
    "cc_rejected_card_error": "TDC: error genérico",
    "cc_rejected_duplicated_payment": "Pago duplicado",
    "cc_rejected_high_risk": "Rechazado por riesgo",
    "cc_rejected_insufficient_amount": "TDC: fondos insuficientes",
    "cc_rejected_invalid_installments": "Mensualidades no permitidas para este monto",
    "cc_rejected_max_attempts": "Demasiados intentos",
    "cc_rejected_other_reason": "Rechazado, razón no especificada",
    "expired": "Expiró sin completarse (OXXO, transferencia)",
    "refunded": "Reembolsado",
}


# ---------- Métodos de pago disponibles en MX ----------

PAYMENT_METHODS: dict[str, str] = {
    # Tarjetas
    "visa": "Visa crédito",
    "master": "Mastercard crédito",
    "amex": "American Express",
    "debvisa": "Visa débito",
    "debmaster": "Mastercard débito",
    "debcabal": "Cabal débito",
    # Efectivo / convenio
    "oxxo": "OXXO (pago efectivo en tienda)",
    "paycash": "PayCash (red de tiendas de conveniencia)",
    # Transferencia
    "bancomerpagoencuotas": "BBVA — pago en cuotas",
    "ticket": "Transferencia bancaria SPEI",
    # MP wallet
    "account_money": "Saldo Mercado Pago",
}


# ---------- Payment Type (alto nivel) ----------

PAYMENT_TYPE: dict[str, str] = {
    "credit_card": "Tarjeta de crédito",
    "debit_card": "Tarjeta de débito",
    "ticket": "OXXO / Pagos en efectivo",
    "bank_transfer": "SPEI",
    "account_money": "Saldo MP",
    "digital_currency": "Crypto",
}


# ---------- Currency ----------

CURRENCY: dict[str, str] = {
    "MXN": "Peso Mexicano",
    "USD": "Dólar Estadounidense",
    "BRL": "Real Brasileño",
    "ARS": "Peso Argentino",
    "CLP": "Peso Chileno",
    "COP": "Peso Colombiano",
    "PEN": "Sol Peruano",
    "UYU": "Peso Uruguayo",
}

# Currencies que normalmente se aceptan en MX
CURRENCY_MX = {"MXN", "USD"}


# ---------- Refund Status ----------

REFUND_STATUS: dict[str, str] = {
    "approved": "Reembolso aprobado y procesado",
    "in_process": "Reembolso en proceso",
    "rejected": "Reembolso rechazado",
}


# ---------- Webhook Notification Types ----------

WEBHOOK_TOPICS: dict[str, str] = {
    "payment": "Cambio en un pago (creado, aprobado, rechazado, refundido)",
    "merchant_order": "Cambio en una orden mercante",
    "plan": "Cambio en un plan de suscripción",
    "subscription": "Cambio en una suscripción activa",
    "invoice": "Cambio en una factura de suscripción",
    "point_integration_wh": "Cambio en una venta con Point (terminal física)",
}


# ---------- Subscription Status ----------

SUBSCRIPTION_STATUS: dict[str, str] = {
    "pending": "Suscripción creada pero no confirmada por el usuario",
    "authorized": "Suscripción activa cobrando periódicamente",
    "paused": "Suscripción pausada (no cobra hasta reanudar)",
    "cancelled": "Suscripción cancelada definitivamente",
    "expired": "Suscripción terminó su periodo (max_billing_attempts agotados)",
}


# ---------- helpers ----------


def describe_payment_status(status: str) -> str | None:
    return PAYMENT_STATUS.get(status)


def is_payment_paid(status: str) -> bool:
    return status in PAYMENT_STATUS_PAID


def is_payment_terminal(status: str) -> bool:
    return status in PAYMENT_STATUS_TERMINAL


def is_payment_refundable(status: str) -> bool:
    return status in PAYMENT_STATUS_REFUNDABLE
