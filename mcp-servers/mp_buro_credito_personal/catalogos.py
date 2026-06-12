"""Catálogos Buró de Crédito personal MX.

⚠ Consultar buró de crédito de OTRA persona sin su autorización formal
constituye DELITO (violación de datos personales, abuso de información).
Este MCP exige autorización explícita registrada antes de operar.
"""

from __future__ import annotations


# Rangos de score Buró de Crédito (Mi Score)
RANGOS_SCORE: dict[str, dict] = {
    "excelente": {
        "rango": "725-850",
        "descripcion": "Sujetos de crédito ideales — mejores tasas y montos",
        "color": "verde",
    },
    "bueno": {
        "rango": "650-724",
        "descripcion": "Sujetos de crédito muy aceptables",
        "color": "verde",
    },
    "regular": {
        "rango": "549-649",
        "descripcion": "Aceptable con tasas medias",
        "color": "amarillo",
    },
    "malo": {
        "rango": "450-548",
        "descripcion": "Difícil aprobación, tasas altas",
        "color": "naranja",
    },
    "muy_malo": {
        "rango": "300-449",
        "descripcion": "Rechazo probable",
        "color": "rojo",
    },
}


# Tipos de cuenta en reporte
TIPO_CUENTA: dict[str, str] = {
    "tdc_revolvente": "Tarjeta de crédito revolvente",
    "tdd": "Tarjeta de débito (no aparece en buró)",
    "credito_hipotecario": "Crédito hipotecario",
    "credito_automotriz": "Crédito automotriz",
    "credito_personal": "Crédito personal/nómina",
    "credito_pyme": "Crédito empresarial PyME",
    "telefonia": "Línea telefónica con financiamiento",
    "departamental": "Crédito de tienda departamental",
    "fonacot": "Crédito Fonacot (trabajadores)",
}


# Status del crédito
STATUS_CUENTA: dict[str, str] = {
    "al_corriente": "Sin atrasos",
    "atraso_30d": "Atraso 1-30 días",
    "atraso_60d": "Atraso 31-60 días",
    "atraso_90d": "Atraso 61-90 días",
    "atraso_120d": "Atraso 91-120 días",
    "vencida": "Vencida > 120 días",
    "perdida": "Pérdida (castigada por la institución)",
    "cerrada_al_corriente": "Cerrada al corriente (positivo)",
    "cerrada_quebranto": "Cerrada por quebranto (negativo)",
    "convenio": "En convenio de reestructura",
}


# Tipos de consulta del buró (importan para el score — muchas bajan)
TIPO_CONSULTA: dict[str, str] = {
    "autoconsulta": "El usuario consulta su propio reporte (no afecta score)",
    "preautorizacion": "Institución analiza si pre-aprobar crédito (suave, mínimo impacto)",
    "solicitud_credito": "Usuario solicitó crédito formal (dura, afecta score)",
    "actualizacion": "Institución actualiza datos de crédito vigente (no afecta)",
    "extincion_obligacion": "Pagó crédito completo (positivo)",
}


# Niveles de monitoreo
NIVELES_MONITOREO: dict[str, dict] = {
    "basico": {
        "precio_mxn_mes": 0,
        "frecuencia_alertas": "ninguna",
        "incluye_score": False,
        "incluye_reporte_completo": False,
    },
    "alerta_basica": {
        "precio_mxn_mes": 99,
        "frecuencia_alertas": "consultas terceros",
        "incluye_score": True,
        "incluye_reporte_completo": False,
    },
    "monitoreo_completo": {
        "precio_mxn_mes": 199,
        "frecuencia_alertas": "todos los cambios",
        "incluye_score": True,
        "incluye_reporte_completo": True,
    },
}


# Marco legal — referencia
MARCO_LEGAL_BURO: dict[str, str] = {
    "ley_aplicable": "Ley para Regular las Sociedades de Información Crediticia",
    "autorizacion_obligatoria": (
        "Art. 28 LRSIC — consultar reporte de otra persona REQUIERE autorización "
        "expresa por escrito o medio electrónico verificable. Vigencia 1 año si "
        "no se especifica."
    ),
    "consultas_propias_gratuitas": "1 reporte anual completo gratuito (Art. 35)",
    "rectificacion": "30 días naturales para rectificar errores (Art. 42)",
    "vigencia_informacion": "Negativa permanece 72 meses (6 años) desde último adeudo",
    "penalidades_consulta_sin_autorizacion": (
        "Multa $50,000 a $5,000,000 MXN + responsabilidad penal por violación "
        "de datos personales (Art. 32 LFPDPPP + LRSIC)"
    ),
}
