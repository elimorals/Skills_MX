"""Catálogos CDMX Municipal (finanzas + semovi + sumate)."""

from __future__ import annotations


PORTALES_CDMX: dict[str, str] = {
    "finanzas_predial": "https://www.finanzas.cdmx.gob.mx/predial",
    "finanzas_tenencia": "https://www.finanzas.cdmx.gob.mx/tenencia",
    "semovi_multas": "https://www.semovi.cdmx.gob.mx/multas",
    "sumate_ciudadano": "https://sumate.cdmx.gob.mx",
    "verificacion_centro": "https://verificacionvehicular.cdmx.gob.mx",
}


STATUS_PREDIAL: dict[str, str] = {
    "AL_CORRIENTE": "Sin adeudo",
    "ADEUDO_BIMESTRE_ACTUAL": "Pendiente bimestre en curso",
    "ADEUDO_VENCIDO": "Adeudo de bimestres anteriores",
    "EXENTO": "Exento (cierto tipo de inmueble o titular)",
}


STATUS_TENENCIA: dict[str, str] = {
    "AL_CORRIENTE": "Tenencia pagada",
    "PENDIENTE": "Pendiente del ejercicio",
    "EXENTO": "Exento (vehículo < umbral o eléctrico/híbrido)",
    "SUBSIDIADO": "Aplicación de subsidio 100%",
}


TIPO_MULTA: dict[str, str] = {
    "fotoinfraccion": "Foto-infracción (cámaras automáticas)",
    "transito_manual": "Multa manual por agente de tránsito",
    "verificacion": "Multa por verificación vehicular vencida",
    "hoy_no_circula": "Multa por circular en restricción",
    "estacionamiento": "Multa por mal estacionamiento",
}


HOY_NO_CIRCULA: dict[str, dict] = {
    "engomado_amarillo": {"dia": "lunes", "ultimo_digito_placa": "5,6"},
    "engomado_rosa": {"dia": "martes", "ultimo_digito_placa": "7,8"},
    "engomado_rojo": {"dia": "miercoles", "ultimo_digito_placa": "3,4"},
    "engomado_verde": {"dia": "jueves", "ultimo_digito_placa": "1,2"},
    "engomado_azul": {"dia": "viernes", "ultimo_digito_placa": "9,0"},
    "todos_sabado_1y3": {"dia": "sabado 1er y 3er del mes", "nota": "depende holograma"},
}


# Holograma de verificación vehicular CDMX
HOLOGRAMAS: dict[str, str] = {
    "00": "Cero (vehículos eléctricos/híbridos) — exento No Circula",
    "0": "Cero — exento No Circula entre semana",
    "1": "Uno — sujeto a Hoy No Circula sábado 2do y 4to",
    "2": "Dos — sujeto a Hoy No Circula entre semana + sábados",
}
