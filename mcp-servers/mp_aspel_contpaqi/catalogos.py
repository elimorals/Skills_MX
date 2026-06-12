"""Catálogos contables Aspel COI / ContPAQi.

Estructura típica del Plan de Cuentas SAT (Código Agrupador):
- 100 Activo
  - 101 Caja
  - 102 Bancos
  - 105 Clientes
- 200 Pasivo
  - 201 Proveedores
- 300 Capital Contable
- 400 Ingresos
  - 401 Ingresos por servicios
- 500 Costos
- 600 Gastos
- 700 Otros ingresos
- 800 Otros gastos
- 900 Cuentas de orden

⚠ El código agrupador SAT (Anexo 24 RMF) es la base obligatoria.
Cada cuenta auxiliar del contribuyente cuelga de un código SAT padre.
Verificar vigencia del anexo 24 contra RMF 2026.
"""

from __future__ import annotations


# ---------- Tipos de Póliza ----------

TIPO_POLIZA: dict[str, str] = {
    "DIARIO": "Póliza de diario (movimientos generales)",
    "INGRESOS": "Póliza de ingresos (cobros y ventas)",
    "EGRESOS": "Póliza de egresos (pagos y gastos)",
    "AJUSTE": "Póliza de ajuste contable",
    "CIERRE": "Póliza de cierre de ejercicio",
    "APERTURA": "Póliza de apertura de ejercicio",
    "TRASPASO": "Póliza de traspasos internos",
}


# ---------- Naturaleza de cuenta ----------

NATURALEZA_CUENTA: dict[str, str] = {
    "DEUDORA": "Aumenta con CARGO (DEBE), disminuye con ABONO (HABER)",
    "ACREEDORA": "Aumenta con ABONO (HABER), disminuye con CARGO (DEBE)",
}


# ---------- Código agrupador SAT (Anexo 24 RMF) — muestra ----------

CODIGO_AGRUPADOR_SAT: dict[str, dict] = {
    "100": {
        "nombre": "Activo",
        "naturaleza": "DEUDORA",
        "tipo": "BALANCE",
    },
    "101": {
        "nombre": "Caja",
        "naturaleza": "DEUDORA",
        "tipo": "BALANCE",
        "padre": "100",
    },
    "102": {
        "nombre": "Bancos",
        "naturaleza": "DEUDORA",
        "tipo": "BALANCE",
        "padre": "100",
    },
    "105": {
        "nombre": "Clientes",
        "naturaleza": "DEUDORA",
        "tipo": "BALANCE",
        "padre": "100",
    },
    "107": {
        "nombre": "Deudores diversos",
        "naturaleza": "DEUDORA",
        "tipo": "BALANCE",
        "padre": "100",
    },
    "115": {
        "nombre": "Inventarios",
        "naturaleza": "DEUDORA",
        "tipo": "BALANCE",
        "padre": "100",
    },
    "120": {
        "nombre": "IVA acreditable",
        "naturaleza": "DEUDORA",
        "tipo": "BALANCE",
        "padre": "100",
    },
    "121": {
        "nombre": "IVA pendiente de acreditar",
        "naturaleza": "DEUDORA",
        "tipo": "BALANCE",
        "padre": "100",
    },
    "200": {
        "nombre": "Pasivo",
        "naturaleza": "ACREEDORA",
        "tipo": "BALANCE",
    },
    "201": {
        "nombre": "Proveedores",
        "naturaleza": "ACREEDORA",
        "tipo": "BALANCE",
        "padre": "200",
    },
    "205": {
        "nombre": "Acreedores diversos",
        "naturaleza": "ACREEDORA",
        "tipo": "BALANCE",
        "padre": "200",
    },
    "208": {
        "nombre": "Impuestos por pagar",
        "naturaleza": "ACREEDORA",
        "tipo": "BALANCE",
        "padre": "200",
    },
    "215": {
        "nombre": "IVA trasladado",
        "naturaleza": "ACREEDORA",
        "tipo": "BALANCE",
        "padre": "200",
    },
    "216": {
        "nombre": "IVA pendiente de trasladar",
        "naturaleza": "ACREEDORA",
        "tipo": "BALANCE",
        "padre": "200",
    },
    "300": {
        "nombre": "Capital contable",
        "naturaleza": "ACREEDORA",
        "tipo": "BALANCE",
    },
    "401": {
        "nombre": "Ingresos",
        "naturaleza": "ACREEDORA",
        "tipo": "RESULTADO",
    },
    "500": {
        "nombre": "Costo de ventas",
        "naturaleza": "DEUDORA",
        "tipo": "RESULTADO",
    },
    "600": {
        "nombre": "Gastos generales",
        "naturaleza": "DEUDORA",
        "tipo": "RESULTADO",
    },
    "700": {
        "nombre": "Otros ingresos",
        "naturaleza": "ACREEDORA",
        "tipo": "RESULTADO",
    },
    "800": {
        "nombre": "Otros gastos",
        "naturaleza": "DEUDORA",
        "tipo": "RESULTADO",
    },
}


# ---------- Conceptos típicos ----------

CONCEPTOS_INGRESOS: list[str] = [
    "Venta de productos",
    "Servicios profesionales",
    "Consultoría",
    "Capacitación",
    "Suscripciones",
    "Licencias",
    "Rentas",
    "Comisiones",
]

CONCEPTOS_GASTOS: list[str] = [
    "Renta de oficina",
    "Servicios públicos (luz, agua, internet)",
    "Sueldos y salarios",
    "Honorarios profesionales",
    "Papelería y artículos de oficina",
    "Combustibles y lubricantes",
    "Mantenimiento",
    "Viáticos",
    "Publicidad y propaganda",
    "Comisiones bancarias",
    "Asesoría legal",
    "Software y suscripciones",
]


# ---------- Métodos de exportación ----------

METODOS_EXPORTACION_ASPEL: dict[str, str] = {
    "CSV_POLIZAS": "Exportación de pólizas a CSV desde Aspel COI menú Reportes → Pólizas",
    "CSV_BALANZA": "Exportación de balanza de comprobación a CSV desde Aspel COI",
    "XML_CONTABILIDAD_ELECTRONICA": (
        "Exportación oficial SAT — XML de Catálogo, Balanza, Pólizas y Auxiliares "
        "(obligatorio para contabilidad electrónica, Art. 28 CFF)"
    ),
    "EXCEL_DIRECTO": "Exportación a Excel desde cualquier reporte de COI",
    "ODBC": "Conexión ODBC directa a la base de datos SQL Server (requiere agente local)",
}

METODOS_EXPORTACION_CONTPAQI: dict[str, str] = {
    "ADD_API_COM": "API ADD del ContPAQi (.NET COM, solo Windows + ContPAQi instalado)",
    "CSV_PROCESAMIENTO": "Procesamiento por lotes de archivos CSV",
    "EXCEL_DIRECTO": "Exportación a Excel desde cualquier reporte",
    "XML_CONTABILIDAD_ELECTRONICA": "Exportación XML para SAT (obligatorio)",
}


# ---------- helpers ----------


def get_codigo_sat(codigo: str) -> dict | None:
    """Lookup de código agrupador SAT."""
    return CODIGO_AGRUPADOR_SAT.get(codigo)


def es_cuenta_resultado(codigo_sat: str) -> bool:
    """True si la cuenta es de resultados (Estado de Resultados)."""
    info = get_codigo_sat(codigo_sat)
    return info is not None and info.get("tipo") == "RESULTADO"


def es_cuenta_balance(codigo_sat: str) -> bool:
    """True si la cuenta es de balance (Balance General)."""
    info = get_codigo_sat(codigo_sat)
    return info is not None and info.get("tipo") == "BALANCE"
