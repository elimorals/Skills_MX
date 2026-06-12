"""Mock data para mp_aspel_contpaqi.

Estructura plausible de pólizas, balanzas y catálogos en formato
estandarizado (no atado a un ERP específico).
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any


def mock_polizas(
    ejercicio: int, mes: int, tipo: str | None = None
) -> dict[str, Any]:
    """Lista mock de pólizas del periodo."""
    fecha_base = date(ejercicio, mes, 1)
    polizas: list[dict[str, Any]] = [
        {
            "numero": "D-001",
            "fecha": (fecha_base + timedelta(days=2)).isoformat(),
            "tipo": "DIARIO",
            "concepto": "Pago renta de oficina mes en curso",
            "lineas": [
                {"cuenta": "601-001", "debe": "30000.00", "haber": "0.00", "nombre": "Renta oficina"},
                {"cuenta": "120-001", "debe": "4800.00", "haber": "0.00", "nombre": "IVA acreditable 16%"},
                {"cuenta": "102-001", "debe": "0.00", "haber": "34800.00", "nombre": "Bancos BBVA"},
            ],
            "total_cargos": "34800.00",
            "total_abonos": "34800.00",
            "balanceada": True,
        },
        {
            "numero": "I-002",
            "fecha": (fecha_base + timedelta(days=5)).isoformat(),
            "tipo": "INGRESOS",
            "concepto": "Cobro de factura cliente Tech Demo SA",
            "lineas": [
                {"cuenta": "102-001", "debe": "58000.00", "haber": "0.00", "nombre": "Bancos BBVA"},
                {"cuenta": "401-001", "debe": "0.00", "haber": "50000.00", "nombre": "Ingresos por servicios"},
                {"cuenta": "215-001", "debe": "0.00", "haber": "8000.00", "nombre": "IVA trasladado 16%"},
            ],
            "total_cargos": "58000.00",
            "total_abonos": "58000.00",
            "balanceada": True,
        },
        {
            "numero": "E-003",
            "fecha": (fecha_base + timedelta(days=10)).isoformat(),
            "tipo": "EGRESOS",
            "concepto": "Pago nómina quincenal",
            "lineas": [
                {"cuenta": "601-101", "debe": "85000.00", "haber": "0.00", "nombre": "Sueldos y salarios"},
                {"cuenta": "208-002", "debe": "0.00", "haber": "12000.00", "nombre": "ISR retenido"},
                {"cuenta": "208-005", "debe": "0.00", "haber": "3500.00", "nombre": "IMSS empleados"},
                {"cuenta": "102-001", "debe": "0.00", "haber": "69500.00", "nombre": "Bancos BBVA"},
            ],
            "total_cargos": "85000.00",
            "total_abonos": "85000.00",
            "balanceada": True,
        },
    ]
    if tipo:
        polizas = [p for p in polizas if p["tipo"] == tipo.upper()]
    return {
        "ejercicio": ejercicio,
        "mes": mes,
        "tipo_filtrado": tipo,
        "total_polizas": len(polizas),
        "polizas": polizas,
    }


def mock_poliza_detalle(numero: str) -> dict[str, Any]:
    """Detalle de una póliza específica."""
    return {
        "numero": numero,
        "fecha": "2026-03-15",
        "tipo": "DIARIO",
        "concepto": "Asiento contable demo",
        "lineas": [
            {"cuenta": "102-001", "nombre": "Bancos BBVA", "debe": "10000.00", "haber": "0.00"},
            {"cuenta": "401-001", "nombre": "Ingresos por servicios", "debe": "0.00", "haber": "10000.00"},
        ],
        "total_cargos": "10000.00",
        "total_abonos": "10000.00",
        "balanceada": True,
        "capturada_por": "demo",
        "fecha_captura": "2026-03-15T10:30:00",
    }


def mock_balanza(ejercicio: int, mes: int) -> dict[str, Any]:
    """Balanza de comprobación mock."""
    return {
        "ejercicio": ejercicio,
        "mes": mes,
        "fecha_corte": date(ejercicio, mes, 28).isoformat(),
        "cuentas": [
            {
                "cuenta": "102-001",
                "nombre": "Bancos BBVA",
                "saldo_inicial": "350000.00",
                "cargos": "58000.00",
                "abonos": "104300.00",
                "saldo_final": "303700.00",
            },
            {
                "cuenta": "105-001",
                "nombre": "Clientes — Tech Demo SA",
                "saldo_inicial": "58000.00",
                "cargos": "0.00",
                "abonos": "58000.00",
                "saldo_final": "0.00",
            },
            {
                "cuenta": "120-001",
                "nombre": "IVA acreditable",
                "saldo_inicial": "0.00",
                "cargos": "4800.00",
                "abonos": "0.00",
                "saldo_final": "4800.00",
            },
            {
                "cuenta": "215-001",
                "nombre": "IVA trasladado",
                "saldo_inicial": "0.00",
                "cargos": "0.00",
                "abonos": "8000.00",
                "saldo_final": "-8000.00",
            },
            {
                "cuenta": "401-001",
                "nombre": "Ingresos por servicios",
                "saldo_inicial": "0.00",
                "cargos": "0.00",
                "abonos": "50000.00",
                "saldo_final": "-50000.00",
            },
            {
                "cuenta": "601-001",
                "nombre": "Renta oficina",
                "saldo_inicial": "0.00",
                "cargos": "30000.00",
                "abonos": "0.00",
                "saldo_final": "30000.00",
            },
            {
                "cuenta": "601-101",
                "nombre": "Sueldos y salarios",
                "saldo_inicial": "0.00",
                "cargos": "85000.00",
                "abonos": "0.00",
                "saldo_final": "85000.00",
            },
        ],
        "total_cargos": "177800.00",
        "total_abonos": "220300.00",
    }


def mock_catalogo_cuentas() -> dict[str, Any]:
    """Catálogo de cuentas mock."""
    return {
        "total_cuentas": 7,
        "cuentas": [
            {"cuenta": "102-001", "nombre": "Bancos BBVA", "codigo_sat": "102", "naturaleza": "DEUDORA", "nivel": "3"},
            {"cuenta": "105-001", "nombre": "Clientes — Tech Demo", "codigo_sat": "105", "naturaleza": "DEUDORA", "nivel": "3"},
            {"cuenta": "120-001", "nombre": "IVA acreditable 16%", "codigo_sat": "120", "naturaleza": "DEUDORA", "nivel": "3"},
            {"cuenta": "215-001", "nombre": "IVA trasladado 16%", "codigo_sat": "215", "naturaleza": "ACREEDORA", "nivel": "3"},
            {"cuenta": "401-001", "nombre": "Ingresos por servicios", "codigo_sat": "401", "naturaleza": "ACREEDORA", "nivel": "3"},
            {"cuenta": "601-001", "nombre": "Renta oficina", "codigo_sat": "600", "naturaleza": "DEUDORA", "nivel": "3"},
            {"cuenta": "601-101", "nombre": "Sueldos y salarios", "codigo_sat": "600", "naturaleza": "DEUDORA", "nivel": "3"},
        ],
    }


def mock_estado_resultados(ejercicio: int, mes: int) -> dict[str, Any]:
    return {
        "ejercicio": ejercicio,
        "mes": mes,
        "fecha_corte": date(ejercicio, mes, 28).isoformat(),
        "ingresos": "50000.00",
        "costo_ventas": "0.00",
        "utilidad_bruta": "50000.00",
        "gastos_generales": "115000.00",
        "utilidad_operacion": "-65000.00",
        "otros_ingresos": "0.00",
        "otros_gastos": "0.00",
        "utilidad_antes_impuestos": "-65000.00",
        "impuestos": "0.00",
        "utilidad_neta": "-65000.00",
        "nota": "Datos demo — pérdida operativa por gastos > ingresos en el mes.",
    }


def mock_balance_general(ejercicio: int, mes: int) -> dict[str, Any]:
    return {
        "ejercicio": ejercicio,
        "mes": mes,
        "fecha_corte": date(ejercicio, mes, 28).isoformat(),
        "activo": {
            "circulante": "308500.00",
            "fijo": "0.00",
            "diferido": "0.00",
            "total": "308500.00",
        },
        "pasivo": {
            "corto_plazo": "23500.00",
            "largo_plazo": "0.00",
            "total": "23500.00",
        },
        "capital": {
            "social": "350000.00",
            "utilidades_acumuladas": "0.00",
            "utilidad_ejercicio": "-65000.00",
            "total": "285000.00",
        },
        "total_pasivo_capital": "308500.00",
        "ecuacion_contable_cuadra": True,
    }
