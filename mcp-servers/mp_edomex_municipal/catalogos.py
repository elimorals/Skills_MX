"""Catálogos Estado de México (EdoMex)."""

from __future__ import annotations


PORTALES_EDOMEX: dict[str, str] = {
    "recaudacion": "https://pagosytramites.edomex.gob.mx/recaudacion/",
    "citas_verificacion": "https://citaverificacion.edomex.gob.mx/RegistroCitas/",
    "infracciones": "https://infracciones.ssedomex.gob.mx/Search",
    "predial_toluca": "http://predial.toluca.gob.mx/Formas/ImpuestoPredial.aspx",
    "predial_municipal": "Variable por municipio (ver shared.catalogo_municipios_mx)",
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
