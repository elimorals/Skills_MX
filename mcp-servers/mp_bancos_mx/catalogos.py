"""Catálogos de bancos MX soportados por mp_bancos_mx.

⚠ Cada banco tiene auth distinto: token físico, app autenticadora, SMS.
El path Playwright real requiere ~60-100h por banco para construirse.
"""

from __future__ import annotations


BANCOS_SOPORTADOS: dict[str, dict] = {
    "bbva": {
        "nombre": "BBVA México",
        "portal": "https://www.bbva.mx/personas/banca-en-linea.html",
        "portal_empresarial": "https://www.bbvanetcash.mx/",
        "auth_methods": ["usuario_password", "token_fisico", "app_codigo"],
        "share_pyme": "~30%",
        "path_real_implementado": False,
    },
    "banamex": {
        "nombre": "Banamex (Citibanamex)",
        "portal": "https://bancanetempresarial.banamex.com",
        "portal_personal": "https://www.banamex.com",
        "auth_methods": ["usuario_password", "token_fisico", "challenge"],
        "share_pyme": "~20%",
        "path_real_implementado": False,
    },
    "santander": {
        "nombre": "Santander México",
        "portal": "https://www.santandernet.com.mx",
        "auth_methods": ["usuario_password", "token", "biometric"],
        "share_pyme": "~15%",
        "path_real_implementado": False,
    },
    "banorte": {
        "nombre": "Banorte",
        "portal": "https://www.banorte.com",
        "portal_empresarial": "https://www.banorte.com/portales/empresarial",
        "auth_methods": ["usuario_password", "token", "app_token"],
        "share_pyme": "~12%",
        "path_real_implementado": False,
    },
    "hsbc": {
        "nombre": "HSBC México",
        "portal": "https://www.hsbc.com.mx",
        "auth_methods": ["usuario_password", "token", "secure_key"],
        "share_pyme": "~5%",
        "path_real_implementado": False,
    },
    "banregio": {
        "nombre": "Banregio",
        "portal": "https://www.banregio.com",
        "auth_methods": ["usuario_password", "token"],
        "share_pyme": "~3% (fuerte en norte)",
        "path_real_implementado": False,
    },
    "inbursa": {
        "nombre": "Inbursa",
        "portal": "https://www.inbursa.com",
        "auth_methods": ["usuario_password", "token"],
        "share_pyme": "~5%",
        "path_real_implementado": False,
    },
    "azteca": {
        "nombre": "Banco Azteca",
        "portal": "https://www.bancoazteca.com.mx",
        "auth_methods": ["usuario_password", "sms"],
        "share_pyme": "~3% (popular B2C)",
        "path_real_implementado": False,
    },
    "scotiabank": {
        "nombre": "Scotiabank México",
        "portal": "https://www.scotiabank.com.mx",
        "auth_methods": ["usuario_password", "token"],
        "share_pyme": "~4%",
        "path_real_implementado": False,
    },
}


TIPOS_MOVIMIENTO: dict[str, str] = {
    "deposito": "Depósito (entrada)",
    "retiro": "Retiro (salida)",
    "transferencia_recibida": "SPEI recibido",
    "transferencia_enviada": "SPEI enviado",
    "pago_servicio": "Pago de servicios (luz, agua, etc.)",
    "comision": "Comisión bancaria",
    "intereses": "Pago/cobro de intereses",
    "cheque_cobrado": "Cheque cobrado",
    "deposito_efectivo": "Depósito en efectivo (atención reglas SAT)",
    "tdc_compra": "Compra con tarjeta crédito",
    "tdd_compra": "Compra con tarjeta débito",
}


# Formatos de export más comunes por banco
FORMATOS_EXPORT: dict[str, list[str]] = {
    "bbva": ["pdf", "xls", "csv", "txt"],
    "banamex": ["pdf", "xls", "csv"],
    "santander": ["pdf", "xls", "csv", "ofx"],
    "banorte": ["pdf", "xls", "txt"],
    "hsbc": ["pdf", "xls", "csv"],
}


def banco_info(codigo: str) -> dict | None:
    return BANCOS_SOPORTADOS.get(codigo.lower())


def es_movimiento_efectivo_grande(monto: float, tipo: str) -> bool:
    """True si es depósito efectivo > $15,000 MXN (trigger Art. 32-D)."""
    return tipo == "deposito_efectivo" and abs(monto) > 15000.0
