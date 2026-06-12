"""Catálogos IMSS Patronal — IDSE (IMSS Desde su Empresa).

Portal: https://idse.imss.gob.mx
Auth: e.firma o tarjeta inteligente NPIE.
"""

from __future__ import annotations


TIPOS_MOVIMIENTO_AFILIATORIO: dict[str, str] = {
    "08": "Alta de trabajador",
    "02": "Baja de trabajador",
    "07": "Modificación de salario",
    "11": "Cambio de empresa (alta + baja simultánea)",
    "09": "Aviso de incapacidad",
    "01": "Reingreso",
}


CAUSA_BAJA: dict[str, str] = {
    "01": "Termino del contrato",
    "02": "Separación voluntaria",
    "03": "Abandono de empleo",
    "04": "Defunción",
    "05": "Cese por circunstancias del trabajo",
    "06": "Otra",
    "07": "Ausentismo",
    "08": "Rescisión del contrato (Art. 47 LFT)",
    "09": "Pensión por invalidez",
    "10": "Pensión por riesgo de trabajo",
    "11": "Jubilación",
    "12": "Cesantía edad avanzada",
    "13": "Vejez",
}


# Conceptos típicos de la cédula de autodeterminación
CONCEPTOS_CEDULA: dict[str, str] = {
    "cuotas_obrero_patronales": "Cuotas obrero-patronales del bimestre",
    "amortizacion_credito_infonavit": "Descuento crédito INFONAVIT",
    "aportacion_patronal_retiro": "2% retiro a Afore",
    "aportacion_patronal_cyv": "Cesantía y Vejez",
    "actualizacion": "Actualización por mora (Art. 21 LCFF)",
    "recargos": "Recargos por mora",
    "multas": "Multas (si aplica)",
}


# Status típicos del trabajador en padrón IMSS
STATUS_TRABAJADOR: dict[str, str] = {
    "ALTA_VIGENTE": "Activo con alta vigente",
    "BAJA_VIGENTE": "Dado de baja",
    "PENDIENTE_ALTA": "Alta en proceso (24-48h)",
    "PENDIENTE_BAJA": "Baja en proceso",
    "INCAPACIDAD": "En periodo de incapacidad",
}


# Tipos de salario base de cotización (SBC)
TIPO_SALARIO: dict[str, str] = {
    "fijo": "Salario fijo (variable cero)",
    "variable": "Salario variable (calculado bimestralmente)",
    "mixto": "Mixto (parte fija + parte variable)",
}


# Límites SBC anuales (en UMAs) — Art. 28 LSS
LIMITES_SBC = {
    "minimo": "1 UMA diaria",
    "maximo": "25 UMAs diarias",
    "nota_2026": "Verificar UMA vigente 2026 contra Banxico/INEGI",
}


# Riesgos de trabajo (Art. 196 LSS) — clases
CLASE_RIESGO: dict[str, str] = {
    "I": "Riesgo mínimo (oficinas, comercio)",
    "II": "Riesgo bajo (servicios, ventas)",
    "III": "Riesgo medio (construcción ligera, manufactura)",
    "IV": "Riesgo alto (industria pesada)",
    "V": "Riesgo máximo (minería, construcción pesada)",
}
