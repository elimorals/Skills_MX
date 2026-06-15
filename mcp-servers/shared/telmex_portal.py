"""Telmex Mi Cuenta — portal helpers.

Mi Telmex (https://miespacio.telmex.com) requiere login con número telefónico
+ contraseña. Path real es opt-in vía PLUGINS_MX_TELMEX_LIVE=1 + credenciales
TELMEX_TELEFONO / TELMEX_PASSWORD. Persistimos cookies por 12h en cache.
"""
from __future__ import annotations

from dataclasses import dataclass


URL_MI_TELMEX_LOGIN = "https://miespacio.telmex.com/login"
URL_MI_TELMEX_FACTURAS = "https://miespacio.telmex.com/web/hogar/factura-electronica"
URL_MI_TELMEX_CONSUMO = "https://miespacio.telmex.com/web/hogar/consumo"

SESSION_TTL_HOURS = 12
LIVE_ENV_FLAG = "PLUGINS_MX_TELMEX_LIVE"


@dataclass
class TelmexCredentials:
    telefono: str
    password: str

    def __post_init__(self) -> None:
        # Telmex acepta 10 dígitos (lada+número) sin guiones.
        self.telefono = self.telefono.strip().replace(" ", "").replace("-", "")
        if not self.telefono.isdigit() or len(self.telefono) != 10:
            raise ValueError(f"Teléfono Telmex debe ser 10 dígitos: {self.telefono!r}")


def validar_telefono(telefono: str) -> str:
    """Normaliza un teléfono 10 dígitos; devuelve canónico."""
    t = telefono.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if t.startswith("+52"):
        t = t[3:]
    if t.startswith("52") and len(t) == 12:
        t = t[2:]
    if not t.isdigit() or len(t) != 10:
        raise ValueError(f"Teléfono Telmex inválido: {telefono!r} → {t!r}")
    return t


__all__ = [
    "URL_MI_TELMEX_LOGIN", "URL_MI_TELMEX_FACTURAS", "URL_MI_TELMEX_CONSUMO",
    "SESSION_TTL_HOURS", "LIVE_ENV_FLAG", "TelmexCredentials", "validar_telefono",
]
