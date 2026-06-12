"""Catálogos Amazon MX Seller (Selling Partner API)."""

from __future__ import annotations


MARKETPLACE_ID_MX = "A1AM78C64UM0Y8"  # Amazon México


LISTING_STATUS: dict[str, str] = {
    "ACTIVE": "Listing activo y comprable",
    "INACTIVE": "Pausado por el seller",
    "INCOMPLETE": "Faltan atributos obligatorios",
    "PROHIBITED": "Bloqueado por Amazon (política violada)",
    "SUPPRESSED": "Suprimido (foto pobre, info faltante)",
}


ORDER_STATUS: dict[str, str] = {
    "Pending": "Pago pendiente o pre-autorización",
    "Unshipped": "Pagado, listo para enviar",
    "PartiallyShipped": "Algunos items enviados",
    "Shipped": "Completamente enviado",
    "Canceled": "Cancelado",
    "Unfulfillable": "No se puede fulfillment",
    "InvoiceUnconfirmed": "Factura pendiente confirmación",
    "PendingAvailability": "Esperando stock disponible",
}


FULFILLMENT_CHANNEL: dict[str, str] = {
    "MFN": "Merchant Fulfilled Network — seller envía",
    "AFN": "Amazon Fulfilled Network — Amazon envía (FBA)",
}


# Categorías con comisiones específicas Amazon MX (referencia 2025, validar 2026)
COMISIONES_CATEGORIA: dict[str, float] = {
    "electronics": 0.08,
    "computers": 0.06,
    "clothing": 0.17,
    "shoes_handbags": 0.15,
    "home_kitchen": 0.15,
    "beauty": 0.15,
    "books": 0.15,
    "toys_games": 0.15,
    "sports_outdoors": 0.15,
    "tools_home_improvement": 0.13,
    "office_products": 0.15,
    "default": 0.15,
}


# Comisiones FBA típicas (referencia)
COMISIONES_FBA_MX: dict[str, dict] = {
    "small_envelope": {"peso_max_g": 200, "tarifa_mxn": 25.00},
    "standard_small": {"peso_max_g": 500, "tarifa_mxn": 55.00},
    "standard_medium": {"peso_max_g": 1500, "tarifa_mxn": 95.00},
    "standard_large": {"peso_max_g": 9000, "tarifa_mxn": 145.00},
    "oversize_standard": {"peso_max_g": 25000, "tarifa_mxn": 245.00},
    "oversize_large": {"peso_max_g": "50kg+", "tarifa_mxn": "varies"},
}
