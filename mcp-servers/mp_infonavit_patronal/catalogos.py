"""Catálogos INFONAVIT Patronal — SUA / Portal Empresarial.

Portales:
- SUA (Sistema Único de Autodeterminación): app local Windows
- Portal Empresarial INFONAVIT: https://empresarios.infonavit.org.mx
- Mi Cuenta Infonavit: https://micuenta.infonavit.org.mx
"""

from __future__ import annotations


TIPOS_DESCUENTO: dict[str, str] = {
    "VSM": "Veces Salario Mínimo (descuento porcentaje sobre SBC)",
    "PCP": "Pesos (cantidad fija mensual)",
    "PVS": "Pesos sobre Veces Salario Mínimo",
    "FACTOR_DESCUENTO": "Factor de descuento (% del SBC)",
}


STATUS_CREDITO: dict[str, str] = {
    "VIGENTE": "Crédito activo con descuentos en proceso",
    "TERMINADO": "Crédito pagado totalmente",
    "SUSPENDIDO": "Suspendido (incapacidad, sin descuentos)",
    "OMISO": "Omiso de pagos por > 3 meses",
    "PRORROGA": "En prórroga (sin descuentos temporalmente)",
    "REESTRUCTURADO": "Crédito reestructurado",
}


CONCEPTOS_EMIS: dict[str, str] = {
    "amortizacion_credito": "Amortización mensual del crédito",
    "intereses": "Intereses pendientes",
    "actualizacion": "Actualización por mora",
    "comisiones": "Comisiones administrativas",
    "saldo_pendiente": "Saldo pendiente de pagar",
}


# Mensajes típicos de aviso INFONAVIT a patrón
TIPOS_AVISO_PATRONAL: dict[str, str] = {
    "ALTA_CREDITO": "Trabajador con nuevo crédito — iniciar descuento",
    "BAJA_CREDITO": "Crédito terminado — detener descuento",
    "MODIFICACION_DESCUENTO": "Cambio en monto/factor descuento",
    "INCAPACIDAD": "Trabajador con incapacidad temporal — suspender",
    "REQUERIMIENTO": "Diferencias en EMIS, requiere corrección",
    "SUBROGACION": "Subrogación de pagos a INFONAVIT",
}


# Catálogo de productos crédito Infonavit (referencia)
PRODUCTOS_CREDITO: dict[str, str] = {
    "tradicional": "Crédito tradicional (compra)",
    "mejoravit": "Mejoravit (reparación/ampliación)",
    "construyo": "ConstruYO (construir en terreno propio)",
    "remodela": "Remodela tu casa",
    "credito_seguro": "Crédito Seguro",
    "infonavit_total": "Infonavit Total (con co-financiamiento bancario)",
    "unamos_credito": "Unamos Crédito (con cónyuge)",
}
