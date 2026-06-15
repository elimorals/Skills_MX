"""SAF CDMX (Secretaría de Administración y Finanzas) — consulta de adeudos vehiculares.

Descubierto el 2026-06-15 vía Playwright. Endpoint público sin Llave CDMX.
Útil para mp_verificacion_vehicular_mx y mp_tenencia_mx en CDMX.

Form:
- URL: https://data.finanzas.cdmx.gob.mx/sma/Consultaciudadana
- Method: GET (form_adeudos)
- Inputs: inputPlaca (texto), captcha_code (imagen alfanumérica)
"""
from __future__ import annotations

URL_SAF_CDMX_CONSULTA = "https://data.finanzas.cdmx.gob.mx/sma/Consultaciudadana"
URL_SAF_CDMX_ADEUDOS = "https://data.finanzas.cdmx.gob.mx/consulta_adeudos"
URL_SAF_CDMX_PAGOS = "https://data.finanzas.cdmx.gob.mx/consultas_pagos/consulta_pagos"

SAF_CDMX_FORM_ID = "form_adeudos"
SAF_CDMX_FIELDS = {
    "placa": "inputPlaca",
    "captcha": "captcha_code",
}
SAF_CDMX_METHOD = "GET"


def normalizar_placa(placa: str) -> str:
    """Quita espacios/guiones y mayúsculas."""
    return placa.strip().upper().replace(" ", "").replace("-", "")


__all__ = [
    "URL_SAF_CDMX_CONSULTA", "URL_SAF_CDMX_ADEUDOS", "URL_SAF_CDMX_PAGOS",
    "SAF_CDMX_FORM_ID", "SAF_CDMX_FIELDS", "SAF_CDMX_METHOD",
    "normalizar_placa",
]
