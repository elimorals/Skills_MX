"""Catálogos CDMX Municipal (finanzas + semovi + sumate)."""

from __future__ import annotations


PORTALES_CDMX: dict[str, str] = {
    "predial_ovica": "https://ovica.finanzas.cdmx.gob.mx/cuenta-predial-liquidacion",
    "adeudos_vehiculares_saf": "https://data.finanzas.cdmx.gob.mx/sma/Consultaciudadana",
    "hoy_no_circula_sedema": "https://www.sedema.cdmx.gob.mx/programas/programa/hoy-no-circula",
    "calidad_aire": "http://www.aire.cdmx.gob.mx",
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
    "sabados": {"dia": "sabado", "nota": "Holograma 2: todos los sábados. Holograma 1: 1º y 3º si placa impar, 2º y 4º si par."},
}


# Holograma de verificación vehicular CDMX
HOLOGRAMAS: dict[str, str] = {
    "00": "Cero (vehículos eléctricos/híbridos) — exento No Circula",
    "0": "Cero — exento del Hoy No Circula (salvo contingencia)",
    "1": "Uno — un día entre semana + 2 sábados al mes (1º/3º impar, 2º/4º par)",
    "2": "Dos — un día entre semana + todos los sábados",
}
