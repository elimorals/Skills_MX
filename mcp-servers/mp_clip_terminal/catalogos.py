"""Catálogos Clip Terminal (POS MX)."""

from __future__ import annotations


TIPOS_TERMINAL: dict[str, dict] = {
    "clip_air": {"nombre": "Clip Air", "precio_mxn": 999, "msi": True},
    "clip_lite": {"nombre": "Clip Lite", "precio_mxn": 599, "msi": False},
    "clip_pro": {"nombre": "Clip Pro", "precio_mxn": 1799, "msi": True, "wifi": True, "lector_qr": True},
    "clip_total": {"nombre": "Clip Total", "precio_mxn": 0, "renta": True, "wifi": True, "imprime_ticket": True},
}


COMISIONES_TIPICAS: dict[str, dict] = {
    "tdc_visa_master_amex": {
        "1_pago": 3.6,
        "3_msi": 6.55,
        "6_msi": 9.55,
        "9_msi": 12.85,
        "12_msi": 15.85,
        "18_msi": 18.85,
    },
    "incluye_iva": False,
}


CHARGE_STATUS: dict[str, str] = {
    "pending": "Esperando autorización banco",
    "approved": "Aprobado y procesado",
    "declined": "Declinado por banco",
    "refunded": "Devuelto",
    "voided": "Anulado antes de captura",
    "chargeback": "Contracargo del banco emisor",
}


SETTLEMENT_FRECUENCIA: dict[str, str] = {
    "T+1": "Liquidación día siguiente (default tarifa estándar)",
    "T+0": "Liquidación mismo día (premium, +0.5% comisión)",
    "T+7": "Liquidación semanal (descuento, raro)",
}
