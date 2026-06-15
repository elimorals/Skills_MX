"""Utilidades para REPUVE — Registro Público Vehicular.

Portal:   https://www2.repuve.gob.mx:8443/ciudadania/
Stack:    Angular SPA + reCAPTCHA v3 invisible + jQuery
Site key: 6Lfy8AEoAAAAANclz0Doczn6y826fM0BjOPXEn9B

Discovery 2026-06-15 con Playwright MCP:
- 4 modos de búsqueda: placa, número de serie (NIV), folio, número de constancia
- reCAPTCHA v3 emitido al cargar la página (textarea g-recaptcha-response-100000)
- Endpoint backend exacto pendiente captura (Angular timing race conditions).
  Patrón esperado por familia: POST a /ciudadania/api/consulta o similar con
  body {tipo, valor, recaptcha_token}.

Cuando el endpoint se confirme en una sesión próxima de discovery, actualizar
API_URL_PATTERN y el handler de _normalizar_resultado.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


PORTAL_URL = "https://www2.repuve.gob.mx:8443/ciudadania/"
RECAPTCHA_SITE_KEY = "6Lfy8AEoAAAAANclz0Doczn6y826fM0BjOPXEn9B"

# Pendiente captura exacta — Angular timing race en discovery sesión actual.
# Patrón típico de los portales mexicanos similares (IMPI, CONDUSEF):
# probablemente POST a algo como /ciudadania/api/* con body JSON + token.
API_URL_PATTERN = r"/ciudadania/(api|services)/.*(consulta|busqueda|search)"

# Selectores Angular descubiertos (placa, NIV, folio, constancia)
SEARCH_INPUT_PLACA = 'input[placeholder*="placa" i]'
SEARCH_INPUT_NIV = 'input[placeholder*="serie" i], input[placeholder*="niv" i]'
SEARCH_INPUT_FOLIO = 'input[placeholder*="folio" i]'
SEARCH_INPUT_CONSTANCIA = 'input[placeholder*="constancia" i]'
SEARCH_BUTTON = 'button.btn.btn-primary'

# Regex NIV/VIN: 17 caracteres alfanuméricos (sin I, O, Q por estándar ISO 3779)
_NIV_PATTERN = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")

# Regex placa mexicana: 2-3 letras + 2-3 dígitos + 1-2 letras (variantes por estado)
_PLACA_PATTERN = re.compile(r"^[A-Z]{2,3}[-\s]?[0-9]{2,4}[-\s]?[A-Z0-9]{1,3}$")


@dataclass
class VehiculoREPUVE:
    """Resultado normalizado de consulta REPUVE."""
    niv: str = ""
    placa: str = ""
    marca: str = ""
    submarca: str = ""
    modelo: str = ""  # año del modelo
    color: str = ""
    tipo: str = ""
    estado: str = ""  # entidad federativa de registro
    estatus_robo: str = ""  # "SIN REPORTE DE ROBO" / "REPORTE DE ROBO ACTIVO"
    tiene_reporte_robo: bool = False
    raw: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "niv": self.niv,
            "placa": self.placa,
            "marca": self.marca,
            "submarca": self.submarca,
            "modelo": self.modelo,
            "color": self.color,
            "tipo": self.tipo,
            "estado": self.estado,
            "estatus_robo": self.estatus_robo,
            "tiene_reporte_robo": self.tiene_reporte_robo,
        }


def validar_niv(niv: str) -> str:
    """Valida y normaliza NIV/VIN.

    Estándar ISO 3779: 17 caracteres alfanuméricos sin I, O, Q.
    Es responsabilidad del caller verificar el dígito verificador (posición 9)
    si necesita validación estricta — REPUVE acepta NIVs aunque tengan typos.
    """
    niv = (niv or "").strip().upper().replace(" ", "").replace("-", "")
    if len(niv) != 17:
        raise ValueError(f"NIV debe tener 17 caracteres, recibido {len(niv)}.")
    if not _NIV_PATTERN.match(niv):
        raise ValueError(
            "NIV inválido. Solo letras A-Z (sin I/O/Q) y dígitos 0-9."
        )
    return niv


def validar_placa(placa: str) -> str:
    """Valida y normaliza placa mexicana."""
    placa = (placa or "").strip().upper()
    if not placa:
        raise ValueError("Placa requerida.")
    if not _PLACA_PATTERN.match(placa):
        raise ValueError(
            "Placa con formato inválido. Esperado: 2-3 letras + 2-4 dígitos + 1-3 caracteres."
        )
    return placa


__all__ = [
    "PORTAL_URL",
    "RECAPTCHA_SITE_KEY",
    "API_URL_PATTERN",
    "SEARCH_INPUT_NIV",
    "SEARCH_INPUT_PLACA",
    "SEARCH_BUTTON",
    "VehiculoREPUVE",
    "validar_niv",
    "validar_placa",
]
