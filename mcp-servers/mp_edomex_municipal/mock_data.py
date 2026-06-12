"""Mock data EdoMex."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any


def mock_predial_edomex(municipio: str, cuenta_predial: str) -> dict[str, Any]:
    return {
        "municipio": municipio,
        "cuenta_predial": cuenta_predial,
        "direccion": "AV. DEMO 123, COL. CENTRO",
        "status": "AL_CORRIENTE",
        "valor_catastral_mxn": 1_850_000.00,
        "bimestre_actual_mxn": 1_240.00,
        "adeudo_total_mxn": 0.00,
    }


def mock_tenencia_edomex(placa: str, ejercicio: int) -> dict[str, Any]:
    return {
        "placa": placa.upper(),
        "ejercicio": ejercicio,
        "status": "PENDIENTE_PAGO",
        "monto_calculado_mxn": 3_850.00,
        "subsidio_aplicable": False,
        "fecha_limite": f"{ejercicio}-03-31",
    }


def mock_multas_edomex(placa: str) -> dict[str, Any]:
    return {
        "placa": placa.upper(),
        "total_multas": 1,
        "monto_adeudo_mxn": 1_240.00,
        "multas": [
            {
                "folio": "EDOMEX-2026-005678",
                "tipo": "transito_manual",
                "infraccion": "Vuelta prohibida",
                "fecha": (date.today() - timedelta(days=22)).isoformat(),
                "monto_mxn": 1_240.00,
                "ubicacion": "Carretera Lechería-Texcoco km 23",
            }
        ],
    }
