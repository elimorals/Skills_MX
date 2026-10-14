"""Utilidades para REPUVE — Registro Público Vehicular.

Portal:   https://www2.repuve.gob.mx:8443/ciudadania/
Stack:    Angular SPA + reCAPTCHA v3 invisible
Endpoint: POST https://www2.repuve.gob.mx:8443/consulta/consulta/repuve
          (body JSON cifrado en el navegador: criterio, llave + token reCAPTCHA).
          Verificado 2026-10-14: un navegador automatizado recibe 401
          "El reCaptcha no fue superado correctamente" → el MCP hace handoff humano.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


PORTAL_URL = "https://www2.repuve.gob.mx:8443/ciudadania/"
RECAPTCHA_SITE_KEY = "6Lfy8AEoAAAAANclz0Doczn6y826fM0BjOPXEn9B"
API_URL = "https://www2.repuve.gob.mx:8443/consulta/consulta/repuve"


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
    "VehiculoREPUVE",
    "validar_niv",
    "validar_placa",
]
