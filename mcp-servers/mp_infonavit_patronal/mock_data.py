"""Mock data INFONAVIT Patronal."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any


def mock_creditos_trabajadores(registro_patronal: str) -> dict[str, Any]:
    return {
        "registro_patronal": registro_patronal,
        "total_trabajadores_con_credito": 4,
        "creditos": [
            {
                "nss_hash": "abc123",
                "numero_credito": "1234567890",
                "tipo_descuento": "FACTOR_DESCUENTO",
                "valor_descuento": 0.2750,  # 27.5% SBC
                "status": "VIGENTE",
                "saldo_pendiente_uma": 4500.32,
                "producto": "tradicional",
                "fecha_inicio_descuento": "2023-08-01",
            },
            {
                "nss_hash": "def456",
                "numero_credito": "9876543210",
                "tipo_descuento": "PCP",
                "valor_descuento": 1850.00,  # $1,850 fijos
                "status": "VIGENTE",
                "saldo_pendiente_uma": 1200.50,
                "producto": "mejoravit",
                "fecha_inicio_descuento": "2024-02-01",
            },
            {
                "nss_hash": "ghi789",
                "numero_credito": "5555555555",
                "tipo_descuento": "VSM",
                "valor_descuento": 0.30,  # 30% SBC
                "status": "SUSPENDIDO",
                "saldo_pendiente_uma": 7200.00,
                "producto": "tradicional",
                "fecha_inicio_descuento": "2021-06-15",
                "razon_suspension": "INCAPACIDAD",
            },
            {
                "nss_hash": "jkl012",
                "numero_credito": "1111222233",
                "tipo_descuento": "FACTOR_DESCUENTO",
                "valor_descuento": 0.1850,
                "status": "PRORROGA",
                "saldo_pendiente_uma": 2300.00,
                "producto": "infonavit_total",
                "fecha_inicio_descuento": "2022-11-01",
            },
        ],
    }


def mock_emis(
    registro_patronal: str, mes: int, ejercicio: int
) -> dict[str, Any]:
    """EMIS — Emisión Mensual."""
    return {
        "registro_patronal": registro_patronal,
        "mes": mes,
        "ejercicio": ejercicio,
        "total_a_pagar": 18_500.00,
        "trabajadores_con_descuento": 3,
        "fecha_emision": date.today().isoformat(),
        "fecha_limite_pago": _decimo_septimo_proximo_mes(),
        "linea_captura": "0123 4567 8901 2345 6789",
        "url_descarga_pdf": None,
        "detalle_por_trabajador": [
            {"nss_hash": "abc123", "credito": "1234567890", "monto": 8200.00},
            {"nss_hash": "def456", "credito": "9876543210", "monto": 1850.00},
            {"nss_hash": "jkl012", "credito": "1111222233", "monto": 8450.00},
        ],
    }


def mock_descuentos_mensuales(
    registro_patronal: str, nss: str, mes: int, ejercicio: int
) -> dict[str, Any]:
    return {
        "registro_patronal": registro_patronal,
        "nss_mascarado": _mask(nss),
        "mes": mes,
        "ejercicio": ejercicio,
        "tiene_credito": True,
        "tipo_descuento": "FACTOR_DESCUENTO",
        "valor_descuento": 0.2750,
        "descuento_calculado_mxn": 8200.00,
        "status_credito": "VIGENTE",
    }


def mock_avisos_pendientes(registro_patronal: str) -> dict[str, Any]:
    return {
        "registro_patronal": registro_patronal,
        "total_avisos": 2,
        "avisos": [
            {
                "tipo": "ALTA_CREDITO",
                "fecha": (date.today() - timedelta(days=5)).isoformat(),
                "nss_hash": "mno345",
                "numero_credito": "7777888899",
                "valor_descuento": 0.30,
                "instruccion": "Iniciar descuento en próxima nómina",
            },
            {
                "tipo": "REQUERIMIENTO",
                "fecha": (date.today() - timedelta(days=12)).isoformat(),
                "folio": "REQ-2026-0042",
                "asunto": "Diferencias EMIS enero 2026",
                "fecha_limite": (date.today() + timedelta(days=15)).isoformat(),
            },
        ],
    }


def _mask(s: str) -> str:
    s = str(s).strip()
    return s[:2] + "*" * (len(s) - 4) + s[-2:] if len(s) > 4 else s


def _decimo_septimo_proximo_mes() -> str:
    hoy = date.today()
    if hoy.month == 12:
        return date(hoy.year + 1, 1, 17).isoformat()
    return date(hoy.year, hoy.month + 1, 17).isoformat()
