"""Utilidades para Constancia de No Antecedentes Penales (CDMX + EdoMex).

Universo: RRHH (contratación masiva), conductor-plataforma (Uber/DiDi/Cabify
exigen no antecedentes), didi-partners, leasing, security clearance.

Portales:
  CDMX  → https://www.cdmx.gob.mx/servicios/servicio/no-antecedentes-penales
         Requiere Llave CDMX SSO (cuenta ciudadana).
  EdoMex → https://carta-no-antecedentes.edomex.gob.mx
         100% digital, sin captcha visible.

Otros estados (no implementados en v1, pendientes de discovery):
  Jalisco, Nuevo León, Puebla, Querétaro, Guanajuato — cada uno con portal propio.

Costo: $77 MXN CDMX, $87 MXN EdoMex (al ciudadano, NO al consultor).
El MCP no genera el documento — solo consulta el estatus de una constancia
ya emitida o verifica autenticidad de un folio.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal


# Portales
CDMX_PORTAL_URL = "https://www.cdmx.gob.mx/servicios/servicio/no-antecedentes-penales"
CDMX_LLAVE_SSO_URL = "https://servicios.cdmx.gob.mx/"
EDOMEX_PORTAL_URL = "https://carta-no-antecedentes.edomex.gob.mx"
EDOMEX_VERIFICA_URL = "https://carta-no-antecedentes.edomex.gob.mx/verificar"

# Estados soportados en v1
EstadoCarta = Literal["VIGENTE", "EXPIRADA", "ANULADA", "NO_ENCONTRADA", "DESCONOCIDO"]
Entidad = Literal["cdmx", "edomex"]

# Validación CURP (idéntica a la regex SAT — reutilizable)
_CURP_PATTERN = re.compile(
    r"^([A-Z][AEIOUX][A-Z]{2}\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])"
    r"[HM](?:AS|B[CS]|C[CLMSH]|D[FG]|G[TR]|HG|JC|M[CNS]|N[ETL]|OC|PL|Q[TR]|"
    r"S[PLR]|T[CSL]|VZ|YN|ZS)[B-DF-HJ-NP-TV-Z]{3}[A-Z\d])(\d)$"
)


@dataclass
class ConstanciaNoAntecedentes:
    """Resultado de consulta de constancia."""
    curp: str
    entidad: Entidad
    estado: EstadoCarta
    folio: str = ""
    fecha_emision: str = ""
    fecha_vigencia: str = ""
    tiene_antecedentes: bool = False  # True si la persona tiene antecedentes registrados
    raw: dict | None = None

    def to_dict(self) -> dict:
        return {
            "curp": self.curp,
            "entidad": self.entidad,
            "estado": self.estado,
            "folio": self.folio,
            "fecha_emision": self.fecha_emision,
            "fecha_vigencia": self.fecha_vigencia,
            "tiene_antecedentes": self.tiene_antecedentes,
            "es_apta_para_contratacion": (
                self.estado == "VIGENTE" and not self.tiene_antecedentes
            ),
        }


def validar_curp(curp: str) -> str:
    """Valida estructura CURP. Levanta ValueError si inválida."""
    curp = (curp or "").strip().upper()
    if not _CURP_PATTERN.match(curp):
        raise ValueError(f"CURP inválido (estructura SAT): {curp}")
    return curp


def validar_folio(folio: str) -> str:
    """Normaliza folio de constancia (formato libre por entidad)."""
    folio = (folio or "").strip().upper()
    if len(folio) < 4 or len(folio) > 50:
        raise ValueError(f"Folio inválido (longitud {len(folio)}, esperado 4-50).")
    return folio


def validar_entidad(entidad: str) -> Entidad:
    """Valida que la entidad sea una de las soportadas en v1."""
    e = (entidad or "").strip().lower()
    if e in ("cdmx", "ciudad de méxico", "ciudad de mexico", "df"):
        return "cdmx"
    if e in ("edomex", "estado de mexico", "estado de méxico", "mexico", "mex"):
        return "edomex"
    raise ValueError(
        f"Entidad '{entidad}' no soportada en v1. "
        "Solo CDMX y EdoMex. Otros estados pendientes de discovery."
    )


__all__ = [
    "CDMX_PORTAL_URL",
    "CDMX_LLAVE_SSO_URL",
    "EDOMEX_PORTAL_URL",
    "EDOMEX_VERIFICA_URL",
    "EstadoCarta",
    "Entidad",
    "ConstanciaNoAntecedentes",
    "validar_curp",
    "validar_folio",
    "validar_entidad",
]
