"""Catálogos del portal SAT.

Referencias:
- Status RFC: posibles estados en el padrón
- Tipos de obligación fiscal
- Motivos de presencia en listas 69 y 69-B
- Auth methods aceptados por endpoint

⚠ Estos catálogos son aproximados — verificar contra portal SAT 2026 vigente.
"""

from __future__ import annotations

from typing import Final


STATUS_RFC: Final[dict[str, str]] = {
    "ACTIVO": "Contribuyente localizado y activo en el padrón.",
    "SUSPENDIDO": "Contribuyente con actividades suspendidas (Art. 27 CFF).",
    "CANCELADO": "RFC cancelado (defunción, fusión, liquidación).",
    "NO_LOCALIZADO": "Domicilio fiscal no localizado por SAT (riesgo alto).",
    "DESCONOCIDO": "No se pudo determinar el status.",
}


# Lista 69 (incumplidos del Art. 69 CFF) — motivos
MOTIVOS_69_INCUMPLIDOS: Final[dict[str, str]] = {
    "NO_LOCALIZADO": "No localizado por SAT en su domicilio fiscal.",
    "NO_PRESENTO_DECLARACIONES": "Omitió la presentación de declaraciones.",
    "CREDITO_FIRME": "Tiene crédito fiscal firme y vigente.",
    "CREDITO_NO_PAGADO": "Tiene crédito fiscal no pagado.",
    "SENTENCIA_FIRME": "Sentencia condenatoria firme.",
    "CANCELADO_FALTA_COBRO": "Crédito fiscal cancelado por incosteabilidad.",
    "CONDONACION": "Beneficiado con condonación / no pagada.",
    "DOMICILIO_FALSO": "Domicilio fiscal falso o supuesto.",
}


# Lista 69-B (operaciones simuladas / EFOS) — definitividad
ESTADO_69B: Final[dict[str, str]] = {
    "PRESUNTO": "Presunto — el SAT presume operaciones inexistentes (Art. 69-B párrafo segundo).",
    "DEFINITIVO": "Definitivo — confirmado por el SAT tras procedimiento (Art. 69-B párrafo cuarto).",
    "DESVIRTUADO": "El contribuyente desvirtuó la presunción.",
    "SENTENCIA_FAVORABLE": "Sentencia favorable al contribuyente (debe removerse).",
}


# Métodos de autenticación SAT por tool
AUTH_METHODS: Final[dict[str, str]] = {
    "RFC_CIEC": "RFC + Contraseña (CIEC) — para descargas básicas y consultas.",
    "EFIRMA": "e.firma (FIEL) — .cer + .key + contraseña. Requerido para Buzón, descarga masiva.",
    "PUBLICO": "Sin autenticación — endpoints públicos (padrón, listas 69, validación UUID).",
}


# Tipos de obligación fiscal que aparecen en CSF (Art. 27 CFF)
TIPOS_OBLIGACION: Final[dict[str, str]] = {
    "ISR_PROVISIONAL": "ISR pago provisional mensual.",
    "ISR_ANUAL": "ISR declaración anual.",
    "ISR_RETENCIONES_SALARIOS": "ISR retenciones por sueldos y salarios.",
    "ISR_RETENCIONES_HONORARIOS": "ISR retenciones por servicios profesionales.",
    "IVA_MENSUAL": "IVA pago mensual definitivo.",
    "IVA_RETENCIONES": "IVA retenciones (Art. 1-A LIVA).",
    "IEPS_MENSUAL": "IEPS pago mensual.",
    "ISN": "Impuesto sobre nómina (estatal).",
    "DECLARACION_INFORMATIVA": "Declaración informativa anual de operaciones con terceros.",
}


# Tipos de notificación del Buzón Tributario
TIPOS_NOTIFICACION_BUZON: Final[dict[str, str]] = {
    "REQUERIMIENTO": "Requerimiento de información o documentación.",
    "CITATORIO": "Citatorio para comparecencia.",
    "INVITACION": "Invitación a regularizarse.",
    "ACTO_ADMINISTRATIVO": "Acto administrativo (multa, crédito, resolución).",
    "AVISO": "Aviso informativo.",
    "ACUSE": "Acuse de recibo de un trámite presentado.",
}


# Status de e.firma (FIEL)
STATUS_EFIRMA: Final[dict[str, str]] = {
    "VIGENTE": "Vigente — opera normalmente.",
    "POR_VENCER_90D": "Vence en menos de 90 días — renovar pronto.",
    "VENCIDA": "Vencida — no opera. Requiere renovación presencial o en línea.",
    "REVOCADA": "Revocada por el SAT o por el contribuyente.",
    "DESCONOCIDO": "Status no determinado.",
}


def es_riesgo_alto_69b(estado: str) -> bool:
    """True si la presencia en lista 69-B representa riesgo fiscal alto.

    Definitivo y presunto son ambos riesgo alto para deducibilidad: el SAT
    presume operaciones inexistentes y los receptores no pueden deducir IVA/ISR.
    """
    return estado.upper() in {"PRESUNTO", "DEFINITIVO"}


def es_riesgo_alto_69(motivo: str) -> bool:
    """True si la presencia en lista 69 representa riesgo alto."""
    return motivo.upper() in {
        "DOMICILIO_FALSO",
        "NO_LOCALIZADO",
        "CREDITO_FIRME",
        "SENTENCIA_FIRME",
    }
