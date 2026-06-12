"""Catálogos Estado de México (EdoMex)."""

from __future__ import annotations


PORTALES_EDOMEX: dict[str, str] = {
    "secretaria_finanzas": "https://sfinanzas.edomex.gob.mx",
    "tenencia": "https://sfinanzas.edomex.gob.mx/tenencia",
    "verificentros": "https://verificacionvehicular.edomex.gob.mx",
    "predial_municipal": "Variable por municipio (Toluca, Naucalpan, Ecatepec, etc.)",
    "multas_transito": "https://multas.edomex.gob.mx",
}


# EdoMex tiene tenencia (CDMX no, salvo subsidio); cobro real
STATUS_TENENCIA_EDOMEX: dict[str, str] = {
    "AL_CORRIENTE": "Pagada del ejercicio",
    "PENDIENTE_PAGO": "Pendiente",
    "VENCIDA_RECARGOS": "Con recargos por mora",
    "SUBSIDIADA": "Aplicación de subsidio (criterio puede variar)",
}


# Municipios EdoMex con sistema de predial digital
MUNICIPIOS_PREDIAL_DIGITAL: list[str] = [
    "Toluca", "Naucalpan", "Ecatepec", "Tlalnepantla", "Atizapán de Zaragoza",
    "Cuautitlán Izcalli", "Coacalco", "Huixquilucan", "Metepec", "Nezahualcóyotl",
    "Tultitlán", "Chimalhuacán",
]


HOY_NO_CIRCULA_EDOMEX: dict[str, dict] = {
    "engomado_amarillo": {"dia": "lunes", "ultimo_digito_placa": "5,6"},
    "engomado_rosa": {"dia": "martes", "ultimo_digito_placa": "7,8"},
    "engomado_rojo": {"dia": "miercoles", "ultimo_digito_placa": "3,4"},
    "engomado_verde": {"dia": "jueves", "ultimo_digito_placa": "1,2"},
    "engomado_azul": {"dia": "viernes", "ultimo_digito_placa": "9,0"},
    "nota": "Aplica solo en municipios mexiquenses conurbados al ZMVM",
}
