"""Mock data CDMX Municipal."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any


def mock_predial(cuenta_predial: str) -> dict[str, Any]:
    return {
        "cuenta_predial": cuenta_predial,
        "direccion": "AV. INSURGENTES SUR 1234, COL. DEL VALLE, CDMX",
        "status": "AL_CORRIENTE",
        "valor_catastral_mxn": 4_500_000.00,
        "bimestre_actual_mxn": 2_850.00,
        "adeudo_total_mxn": 0.00,
        "ultima_actualizacion": "2026-01-15",
        "tipo_inmueble": "habitacional",
    }


def mock_tenencia(placa: str) -> dict[str, Any]:
    return {
        "placa": placa.upper(),
        "marca": "Toyota",
        "modelo": "Corolla",
        "año": 2022,
        "ejercicio": date.today().year,
        "status": "AL_CORRIENTE",
        "monto_pagado_mxn": 0.00,
        "subsidio_aplicado": True,
        "razon_subsidio": "Vehículo con valor < $300,000 MXN — subsidio 100% gobierno CDMX",
    }


def mock_multas(placa: str) -> dict[str, Any]:
    return {
        "placa": placa.upper(),
        "total_multas": 2,
        "monto_adeudo_mxn": 1_656.00,
        "multas": [
            {
                "folio": "FCM-2026-001234",
                "tipo": "fotoinfraccion",
                "infraccion": "Exceso de velocidad 70 km/h en zona 50 km/h",
                "fecha": (date.today() - timedelta(days=18)).isoformat(),
                "monto_mxn": 1_037.00,
                "ubicacion": "Av. Reforma esq. Gandhi",
                "evidencia_foto_url": None,
                "vence_descuento": (date.today() + timedelta(days=12)).isoformat(),
            },
            {
                "folio": "FCM-2026-001120",
                "tipo": "estacionamiento",
                "infraccion": "Estacionar en zona prohibida",
                "fecha": (date.today() - timedelta(days=5)).isoformat(),
                "monto_mxn": 619.00,
                "ubicacion": "Calle Demo 123, Col. Roma Norte",
                "evidencia_foto_url": None,
            },
        ],
    }


def mock_calendario_hoy_no_circula(fecha: str) -> dict[str, Any]:
    return {
        "fecha": fecha,
        "contingencia_activa": False,
        "fase_contingencia": None,
        "restricciones_del_dia": [
            {
                "ultimo_digito_placa": "5,6",
                "engomado": "amarillo",
                "holograma_aplica": ["1", "2"],
            }
        ],
        "exentos": [
            "Holograma 00 (eléctricos/híbridos)",
            "Holograma 0 (verificados recientemente)",
            "Servicio público",
            "Transporte de personas con discapacidad",
        ],
    }
