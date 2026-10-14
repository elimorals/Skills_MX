"""Cédula profesional SEP (Registro Nacional de Profesionistas).

Portal: https://cedulaprofesional.sep.gob.mx/ (Angular). Verificado 2026-10-14
leyendo `assets/config.json` y `main.*.js`:

- Token: GET  https://cedulaprofesional.sep.gob.mx/api/auth/token
         (headers X-Client-Id / X-API-Key públicos del bundle)
- Consulta: POST https://cedulaprofesional.sep.gob.mx/api/rnp/solr/profesionista/consultar/byDetalle
         body {"numCedula": ...}, headers Authorization: Bearer + **X-Recaptcha-Token**
         (reCAPTCHA v3, site key 6Leb1M4rAAAAAP_gRcAyMiOo99-j6eqQajKuMlB9).

Cada consulta exige un token reCAPTCHA v3 emitido en un navegador real; el MCP
no lo genera ni lo evade. El modo real devuelve un **handoff humano**.
Mock solo con PLUGINS_MX_MOCK=1.
"""

from __future__ import annotations

import os
import re
from typing import Any, Optional

from shared.errors import ValidationError

URL_SEP_CEDULA = "https://cedulaprofesional.sep.gob.mx/"
API_CONSULTA = f"{URL_SEP_CEDULA}api/rnp/solr/profesionista/consultar/byDetalle"


def validar_formato_cedula(cedula: str) -> bool:
    """Cédula SEP es 7-8 dígitos numéricos."""
    if not cedula or not isinstance(cedula, str):
        return False
    return bool(re.match(r"^\d{7,8}$", cedula.strip()))


def handoff_sep(campos: dict[str, Any]) -> dict[str, Any]:
    return {
        "requiere_humano": True,
        "motivo": "captcha_requerido",
        "url": URL_SEP_CEDULA,
        "pasos": [
            "Abrir la URL en un navegador.",
            "En 'Búsqueda de Cédulas Profesionales' capturar los datos prellenados.",
            "Pulsar 'Buscar' (reCAPTCHA v3 se valida en el navegador).",
            "Verificar nombre, profesión, institución y año de expedición.",
        ],
        "campos_prellenados": {k: v for k, v in campos.items() if v},
        "fuente": "SEP-RNP",
        "simulated": False,
    }


def consultar_cedula_sep(
    cedula: Optional[str] = None,
    nombre: Optional[str] = None,
    primer_apellido: Optional[str] = None,
    segundo_apellido: Optional[str] = None,
    curp: Optional[str] = None,
) -> dict[str, Any]:
    """Consulta cédula SEP: handoff humano en real, mock con PLUGINS_MX_MOCK=1."""
    if cedula and not validar_formato_cedula(cedula):
        raise ValidationError(f"Cédula '{cedula}' no tiene formato válido (7-8 dígitos).")
    if not any([cedula, nombre, curp]):
        raise ValidationError(
            "Debe proveer al menos uno: cedula, nombre+apellido, o curp."
        )
    if os.environ.get("PLUGINS_MX_MOCK") == "1":
        return _mock_response(cedula, nombre, primer_apellido)
    return handoff_sep({
        "cedula": cedula,
        "nombre": nombre,
        "primer_apellido": primer_apellido,
        "segundo_apellido": segundo_apellido,
        "curp": curp,
    })


def _mock_response(
    cedula: Optional[str], nombre: Optional[str], primer_apellido: Optional[str]
) -> dict[str, Any]:
    """Respuesta mock realista para desarrollo."""
    return {
        "cedula": cedula or "1234567",
        "nombre_completo": f"{nombre or 'JUAN'} {primer_apellido or 'PEREZ'} GARCIA",
        "profesion": "Médico Cirujano",
        "institucion": "Universidad Nacional Autónoma de México",
        "fecha_expedicion": "2015-06-15",
        "vigente": True,
        "fuente": "SEP-RNP",
        "url_consultada": URL_SEP_CEDULA,
        "simulated": True,
    }
