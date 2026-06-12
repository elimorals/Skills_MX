"""Catálogos Trustly MX (open banking)."""

from __future__ import annotations


PAYMENT_STATUS: dict[str, str] = {
    "pending": "Esperando autorización del banco",
    "authorized": "Autorizado por banco emisor",
    "completed": "Completado y acreditado",
    "failed": "Falló — fondos insuficientes / banco rechazó",
    "expired": "Expiró (cliente no autorizó en tiempo)",
    "cancelled": "Cancelado por usuario",
    "refunded": "Devuelto al pagador",
}

PAYMENT_STATUS_TERMINAL = {"completed", "failed", "expired", "cancelled", "refunded"}
PAYMENT_STATUS_PAID = {"completed"}


# Bancos MX soportados por Trustly (referencia)
BANCOS_SOPORTADOS: dict[str, str] = {
    "bbva": "BBVA México",
    "banamex": "Banamex (Citibanamex)",
    "santander": "Santander México",
    "banorte": "Banorte",
    "hsbc": "HSBC México",
    "scotiabank": "Scotiabank México",
    "inbursa": "Inbursa",
    "banregio": "Banregio",
}


CURRENCY: dict[str, str] = {
    "MXN": "Peso Mexicano",
    "USD": "Dólar (limitado por banco)",
}


WEBHOOK_EVENTS: dict[str, str] = {
    "payment.created": "Solicitud de pago creada",
    "payment.authorized": "Cliente autorizó pago en su banco",
    "payment.completed": "Pago completado y fondos disponibles",
    "payment.failed": "Pago falló",
    "payment.refunded": "Pago devuelto",
    "payment.expired": "Pago expiró sin autorización",
}
