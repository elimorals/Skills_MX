"""Mock data plausible para mp_bancos_mx."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any


def mock_estado_cuenta(
    banco: str, cuenta: str, ejercicio: int, mes: int
) -> dict[str, Any]:
    fecha_inicio = date(ejercicio, mes, 1)
    # Último día del mes (simplificado)
    if mes == 12:
        fecha_fin = date(ejercicio, 12, 31)
    else:
        fecha_fin = date(ejercicio, mes + 1, 1) - timedelta(days=1)

    return {
        "banco": banco,
        "cuenta_mascarada": _mascarar(cuenta),
        "periodo": {
            "inicio": fecha_inicio.isoformat(),
            "fin": fecha_fin.isoformat(),
        },
        "saldo_inicial": 125_000.00,
        "saldo_final": 168_500.00,
        "depositos_total": 195_000.00,
        "retiros_total": 151_500.00,
        "num_movimientos": 47,
        "formato_disponible": "pdf",
        "url_descarga": None,
    }


def mock_movimientos(
    banco: str, cuenta: str, dias: int = 30
) -> dict[str, Any]:
    hoy = date.today()
    movs = [
        {
            "fecha": (hoy - timedelta(days=2)).isoformat(),
            "tipo": "transferencia_recibida",
            "concepto": "PAGO FACTURA F-2026-0042 / SPEI BBVA / Cliente Demo SA",
            "referencia_numerica": "0021480042",
            "clave_rastreo": "MBAN01202603152120000001",
            "monto": 58_000.00,
            "saldo_resultante": 168_500.00,
            "rfc_ordenante": "EFD850101001",
        },
        {
            "fecha": (hoy - timedelta(days=5)).isoformat(),
            "tipo": "comision",
            "concepto": "COMISION MANEJO DE CUENTA",
            "monto": -350.00,
            "saldo_resultante": 110_500.00,
        },
        {
            "fecha": (hoy - timedelta(days=7)).isoformat(),
            "tipo": "transferencia_enviada",
            "concepto": "PAGO NOMINA QUINCENA",
            "referencia_numerica": "0034567890",
            "monto": -69_500.00,
            "saldo_resultante": 110_850.00,
        },
        {
            "fecha": (hoy - timedelta(days=10)).isoformat(),
            "tipo": "deposito",
            "concepto": "DEPOSITO EN VENTANILLA",
            "monto": 5_000.00,
            "saldo_resultante": 180_350.00,
        },
        {
            "fecha": (hoy - timedelta(days=15)).isoformat(),
            "tipo": "transferencia_recibida",
            "concepto": "PAGO FACTURA F-2026-0041 / SPEI",
            "referencia_numerica": "0021479991",
            "clave_rastreo": "MBAN01202603012103000001",
            "monto": 116_000.00,
            "saldo_resultante": 175_350.00,
            "rfc_ordenante": "IBM970131DRA",
        },
    ]

    return {
        "banco": banco,
        "cuenta_mascarada": _mascarar(cuenta),
        "dias_consultados": dias,
        "total_movimientos": len(movs),
        "movimientos": movs,
    }


def mock_verificar_pago(
    banco: str, referencia: str, monto: float
) -> dict[str, Any]:
    encontrado = referencia.startswith("0021")  # demo: rangos de referencia válidos
    return {
        "banco": banco,
        "referencia_consultada": referencia,
        "monto_consultado": monto,
        "encontrado": encontrado,
        "fecha_pago": (date.today() - timedelta(days=2)).isoformat() if encontrado else None,
        "ordenante": "Cliente Demo SA" if encontrado else None,
        "rfc_ordenante": "EFD850101001" if encontrado else None,
    }


def _mascarar(cuenta: str) -> str:
    """Muestra solo los últimos 4 dígitos."""
    s = str(cuenta).strip()
    if len(s) <= 4:
        return s
    return "*" * (len(s) - 4) + s[-4:]
