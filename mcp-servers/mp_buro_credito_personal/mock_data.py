"""Mock data Buró de Crédito personal."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any


def mock_score(rfc_hash: str) -> dict[str, Any]:
    return {
        "rfc_hash": rfc_hash,
        "score_actual": 712,
        "categoria": "bueno",
        "fecha_consulta": date.today().isoformat(),
        "tendencia_3_meses": "+15",
        "factores_positivos": [
            "Historial de pagos puntuales > 24 meses",
            "Mix saludable de tipos de crédito",
            "Uso de TDC < 30% del límite",
        ],
        "factores_negativos": [
            "Antigüedad de cuentas relativamente corta",
            "1 consulta de solicitud de crédito en últimos 90 días",
        ],
    }


def mock_reporte_completo(rfc_hash: str) -> dict[str, Any]:
    hoy = date.today()
    return {
        "rfc_hash": rfc_hash,
        "fecha_reporte": hoy.isoformat(),
        "score_actual": 712,
        "categoria": "bueno",
        "info_personal_mascarada": {
            "nombre_iniciales": "J.M.G.",
            "rfc_parcial": "MAJG800***XYZ",
            "domicilios_count": 3,
            "telefonos_count": 4,
            "ultimo_domicilio_estado": "CDMX",
        },
        "cuentas_activas": [
            {
                "tipo": "tdc_revolvente",
                "institucion": "BBVA",
                "limite_credito_mxn": 150_000.00,
                "saldo_actual_mxn": 22_500.00,
                "porcentaje_uso": 0.15,
                "status": "al_corriente",
                "antiguedad_meses": 84,
                "ultimo_pago_mxn": 5_000.00,
            },
            {
                "tipo": "credito_hipotecario",
                "institucion": "BBVA",
                "monto_original_mxn": 2_500_000.00,
                "saldo_actual_mxn": 1_850_000.00,
                "pago_mensual_mxn": 25_000.00,
                "status": "al_corriente",
                "antiguedad_meses": 36,
            },
            {
                "tipo": "credito_automotriz",
                "institucion": "Santander",
                "monto_original_mxn": 350_000.00,
                "saldo_actual_mxn": 125_000.00,
                "pago_mensual_mxn": 6_500.00,
                "status": "al_corriente",
                "antiguedad_meses": 30,
            },
        ],
        "cuentas_cerradas": [
            {
                "tipo": "tdc_revolvente",
                "institucion": "Banamex",
                "fecha_cierre": (hoy - timedelta(days=900)).isoformat(),
                "status": "cerrada_al_corriente",
            },
        ],
        "consultas_recientes": [
            {
                "fecha": (hoy - timedelta(days=45)).isoformat(),
                "tipo": "solicitud_credito",
                "institucion": "Banorte",
                "afecta_score": True,
            },
            {
                "fecha": (hoy - timedelta(days=190)).isoformat(),
                "tipo": "autoconsulta",
                "institucion": "MiScore App",
                "afecta_score": False,
            },
        ],
        "claves_observacion": [],
    }


def mock_alertas_recientes(rfc_hash: str) -> dict[str, Any]:
    return {
        "rfc_hash": rfc_hash,
        "total_alertas_30dias": 2,
        "alertas": [
            {
                "fecha": (date.today() - timedelta(days=12)).isoformat(),
                "tipo": "consulta_tercero",
                "descripcion": "Banorte consultó tu reporte (solicitud de crédito personal)",
                "accion_recomendada": "Si NO solicitaste crédito, reportar como consulta no autorizada",
            },
            {
                "fecha": (date.today() - timedelta(days=25)).isoformat(),
                "tipo": "cambio_status",
                "descripcion": "Crédito automotriz cambió a 'al_corriente' (era 'atraso_30d')",
                "accion_recomendada": "Sin acción — buena noticia",
            },
        ],
    }
