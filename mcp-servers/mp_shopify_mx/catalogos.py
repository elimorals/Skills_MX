"""Catálogos de Shopify específicos para mercado MX.

Notas:
- Shopify Admin API REST v2024-04+ es el target (versión 2025-01 en producción).
- Algunos features (Shopify Functions, B2B) requieren Shopify Plus.
- Para MX: gateway debe ser Conekta o MercadoPago (no Shopify Payments).
"""

from __future__ import annotations


# ---------- Order Financial Status ----------

ORDER_FINANCIAL_STATUS: dict[str, str] = {
    "pending": "Pago pendiente de procesamiento",
    "authorized": "Autorizado (TDC) pero no capturado",
    "partially_paid": "Pagado parcialmente",
    "paid": "Pagado completamente",
    "partially_refunded": "Reembolsado parcialmente",
    "refunded": "Reembolsado totalmente",
    "voided": "Anulado antes de captura",
}

ORDER_FINANCIAL_STATUS_PAID = {"paid"}
ORDER_FINANCIAL_STATUS_REFUNDABLE = {"paid", "partially_paid"}


# ---------- Order Fulfillment Status ----------

ORDER_FULFILLMENT_STATUS: dict[str, str] = {
    "unfulfilled": "No enviado todavía",
    "partial": "Enviado parcialmente",
    "fulfilled": "Enviado completamente",
    "restocked": "Devuelto y reingresado a stock",
}


# ---------- Order Status (cancellation) ----------

ORDER_STATUS: dict[str, str] = {
    "open": "Orden activa",
    "closed": "Orden cerrada (fulfilled o cancelada)",
    "cancelled": "Orden cancelada",
}


# ---------- Cancellation Reasons ----------

CANCELLATION_REASONS: dict[str, str] = {
    "customer": "Cancelada por el cliente",
    "fraud": "Cancelada por sospecha de fraude",
    "inventory": "Cancelada por falta de inventario",
    "declined": "Cancelada por pago declinado",
    "other": "Otra razón",
}


# ---------- Métodos de pago aceptados en MX ----------

PAYMENT_GATEWAYS_MX: dict[str, str] = {
    "conekta": "Conekta — TDC + OXXO + SPEI (recomendado MX)",
    "mercadopago": "MercadoPago — TDC + OXXO + cuenta MP",
    "openpay": "Openpay — TDC empresarial",
    "stripe_mx": "Stripe MX — cross-border MX↔US",
    "paypal_mx": "PayPal MX — alternativa",
    "manual_bank_transfer": "Transferencia manual SPEI",
}


# ---------- Paqueterías MX ----------

CARRIERS_MX: dict[str, dict] = {
    "estafeta": {
        "nombre": "Estafeta",
        "cobertura": "nacional",
        "tipos_servicio": ["dia_siguiente", "terrestre", "express"],
        "peso_max_kg": 70,
        "shopify_app": "Estafeta Shopify",
    },
    "dhl_mx": {
        "nombre": "DHL México",
        "cobertura": "nacional+internacional",
        "tipos_servicio": ["express", "same_day", "next_day"],
        "peso_max_kg": 70,
        "shopify_app": "MyDHL Plus",
    },
    "fedex_mx": {
        "nombre": "FedEx México",
        "cobertura": "nacional+internacional",
        "tipos_servicio": ["overnight", "ground", "express"],
        "peso_max_kg": 68,
        "shopify_app": "FedEx Shipping",
    },
    "99_minutos": {
        "nombre": "99 Minutos",
        "cobertura": "metropolitana (CDMX, GDL, MTY)",
        "tipos_servicio": ["same_day", "next_day"],
        "peso_max_kg": 25,
        "shopify_app": "99 Minutos",
    },
    "skydropx": {
        "nombre": "Skydropx (multi-carrier)",
        "cobertura": "nacional+internacional",
        "tipos_servicio": ["comparativa"],
        "peso_max_kg": 70,
        "shopify_app": "Skydropx",
    },
}


# ---------- Webhook topics relevantes ----------

WEBHOOK_TOPICS: dict[str, str] = {
    "orders/create": "Nueva orden creada",
    "orders/paid": "Orden pagada",
    "orders/cancelled": "Orden cancelada",
    "orders/fulfilled": "Orden marcada como enviada",
    "orders/partially_fulfilled": "Orden parcialmente enviada",
    "orders/refunds/create": "Refund procesado",
    "products/create": "Producto nuevo",
    "products/update": "Producto actualizado",
    "inventory_levels/update": "Cambio en niveles de inventario",
    "customers/create": "Cliente nuevo",
    "customers/update": "Cliente actualizado",
    "checkouts/create": "Checkout iniciado",
    "checkouts/update": "Checkout actualizado (abandono)",
    "app/uninstalled": "App desinstalada",
}


# ---------- Tax overrides MX ----------

TAX_CONFIG_MX: dict[str, dict] = {
    "general": {
        "tasa": 0.16,
        "descripcion": "IVA general 16%",
    },
    "frontera_norte": {
        "tasa": 0.08,
        "descripcion": "IVA 8% región fronteriza norte (decreto)",
        "municipios_aplicables": "Lista pública SAT — validar antes de aplicar",
    },
    "exento": {
        "tasa": 0.0,
        "descripcion": "Exento — medicamentos, libros, alimentos básicos",
        "aplicacion": "Configurar por colección con tax: false",
    },
}


# ---------- helpers ----------


def is_paid(financial_status: str) -> bool:
    return financial_status in ORDER_FINANCIAL_STATUS_PAID


def is_refundable(financial_status: str) -> bool:
    return financial_status in ORDER_FINANCIAL_STATUS_REFUNDABLE


def carrier_info(code: str) -> dict | None:
    return CARRIERS_MX.get(code)
