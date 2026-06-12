"""Mock data para mp_imss_patronal."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any


def mock_avisos_pendientes(registro_patronal: str) -> dict[str, Any]:
    return {
        "registro_patronal": registro_patronal,
        "total_pendientes": 2,
        "avisos": [
            {
                "folio": "IDSE-2026-001234",
                "tipo": "REQUERIMIENTO",
                "fecha": (date.today() - timedelta(days=3)).isoformat(),
                "asunto": "Diferencias en cédula bimestre 01-2026",
                "fecha_limite": (date.today() + timedelta(days=12)).isoformat(),
                "urgencia": "MEDIA",
            },
            {
                "folio": "IDSE-2026-001120",
                "tipo": "INVITACION",
                "fecha": (date.today() - timedelta(days=10)).isoformat(),
                "asunto": "Verificar SBC trabajadores con salario variable",
                "urgencia": "BAJA",
            },
        ],
    }


def mock_alta_trabajador(
    registro_patronal: str, nss: str, salario_diario: float
) -> dict[str, Any]:
    return {
        "registro_patronal": registro_patronal,
        "nss_mascarado": _mask(nss),
        "tipo_movimiento": "08",
        "fecha_alta": date.today().isoformat(),
        "salario_diario_integrado": salario_diario,
        "estatus": "PENDIENTE_ALTA",
        "folio_recepcion": f"IMSS-{date.today().isoformat()}-{nss[-4:]}",
        "tiempo_estimado_procesamiento_horas": 48,
    }


def mock_baja_trabajador(
    registro_patronal: str, nss: str, causa: str
) -> dict[str, Any]:
    return {
        "registro_patronal": registro_patronal,
        "nss_mascarado": _mask(nss),
        "tipo_movimiento": "02",
        "fecha_baja": date.today().isoformat(),
        "causa_baja": causa,
        "estatus": "PENDIENTE_BAJA",
        "folio_recepcion": f"IMSS-{date.today().isoformat()}-BAJA-{nss[-4:]}",
    }


def mock_cedula_autodeterminacion(
    registro_patronal: str, bimestre: int, ejercicio: int
) -> dict[str, Any]:
    return {
        "registro_patronal": registro_patronal,
        "bimestre": bimestre,
        "ejercicio": ejercicio,
        "trabajadores_activos": 12,
        "subtotales": {
            "cuotas_obrero_patronales": 85_000.00,
            "aportacion_retiro_2pct": 7_200.00,
            "aportacion_cyv": 18_500.00,
            "amortizacion_infonavit": 12_300.00,
        },
        "total_a_pagar": 123_000.00,
        "linea_captura": "0123 4567 8901 2345 6789",
        "fecha_limite_pago": _ultimo_dia_proximo_mes(),
    }


def mock_emcr(registro_patronal: str, mes: int, ejercicio: int) -> dict[str, Any]:
    """EMCR — Emisión Mensual Cédula Reposicionada."""
    return {
        "registro_patronal": registro_patronal,
        "mes": mes,
        "ejercicio": ejercicio,
        "total_a_pagar": 42_000.00,
        "fecha_emision": date.today().isoformat(),
        "url_descarga_pdf": None,
        "trabajadores": 12,
    }


def mock_sbc(registro_patronal: str, nss: str) -> dict[str, Any]:
    return {
        "registro_patronal": registro_patronal,
        "nss_mascarado": _mask(nss),
        "salario_diario": 850.00,
        "factor_integracion": 1.0493,  # 25.04 días aguinaldo + vacaciones / 365
        "sbc_diario": 891.91,
        "vigencia_desde": "2026-01-01",
        "tipo_salario": "fijo",
    }


def mock_padron_trabajadores(registro_patronal: str) -> dict[str, Any]:
    return {
        "registro_patronal": registro_patronal,
        "total_trabajadores": 12,
        "trabajadores": [
            {"nss_hash": "abc123", "alta": "2024-03-15", "sbc_diario": 891.91, "status": "ALTA_VIGENTE"},
            {"nss_hash": "def456", "alta": "2023-09-01", "sbc_diario": 1245.67, "status": "ALTA_VIGENTE"},
            {"nss_hash": "ghi789", "alta": "2024-11-10", "sbc_diario": 567.34, "status": "INCAPACIDAD"},
        ],
    }


def _mask(s: str) -> str:
    s = str(s).strip()
    return s[:2] + "*" * (len(s) - 4) + s[-2:] if len(s) > 4 else s


def _ultimo_dia_proximo_mes() -> str:
    hoy = date.today()
    if hoy.month == 12:
        return date(hoy.year + 1, 1, 17).isoformat()
    return date(hoy.year, hoy.month + 1, 17).isoformat()
