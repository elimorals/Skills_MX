"""Mock data Monterrey/NL."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any


def mock_predial_nl(municipio: str, cuenta: str) -> dict[str, Any]:
    return {
        "municipio": municipio,
        "cuenta_predial": cuenta,
        "direccion": "AV. DEMO 456, COL. CENTRO",
        "status": "AL_CORRIENTE",
        "valor_catastral_mxn": 2_350_000.00,
        "bimestre_actual_mxn": 1_540.00,
        "adeudo_total_mxn": 0.00,
    }


def mock_multas_nl(placa: str) -> dict[str, Any]:
    return {
        "placa": placa.upper(),
        "estado": "NL",
        "total_multas": 1,
        "monto_adeudo_mxn": 875.00,
        "multas": [
            {
                "folio": "NL-2026-002468",
                "tipo": "transito_manual",
                "infraccion": "No respetar señal de alto",
                "fecha": (date.today() - timedelta(days=14)).isoformat(),
                "monto_mxn": 875.00,
                "ubicacion": "Av. Constitución y Pino Suárez, Monterrey",
            }
        ],
    }


def mock_status_aire_nl(fecha: str) -> dict[str, Any]:
    return {
        "fecha": fecha,
        "estado": "Nuevo León",
        "contingencia_activa": False,
        "fase": None,
        "calidad_aire_imeca": 65,
        "categoria_imeca": "Buena",
        "restricciones_aplicables": [],
    }
