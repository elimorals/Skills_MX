"""Telmex — portal helpers.

Path real recomendado: `pago_sin_login` (sin credenciales de usuario).
Verificado con Playwright el 2026-06-15 — ver docs/discovery-portales-2026-06-15.md.

Mi Telmex (NetIQ SSO) opcional para descarga de XML CFDI y consumo extendido,
requiere TELMEX_TELEFONO + TELMEX_PASSWORD.
"""
from __future__ import annotations

from dataclasses import dataclass


# Ruta sin login (descubierta 2026-06-15) — opción recomendada
URL_TELMEX_PAGO_SIN_LOGIN = "https://telmex.com/web/guest/pago_sin_login"
URL_TELMEX_PORTLET_POST = (
    "https://telmex.com/web/contrata/portlet-login-ip"
    "?p_p_id=com_telmex_payportlet_PayPortlet_INSTANCE_qwuu"
    "&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view"
    "&p_p_resource_id=%2Fpay%2FresourceURL"
    "&p_p_cacheability=cacheLevelPage&servicio=rcas"
)
TELMEX_RECAPTCHA_SITE_KEY = "6LfamtYlAAAAALlKmKUh8CDQPaAvAFoY_2ScQ8HF"
TELMEX_PAGO_FIELDS = {
    "telefono": "telefono",
    "telefono_confirm": "telConfirm",
    "correo": "correo",
}

# Mi Telmex con SSO (opcional)
URL_MI_TELMEX_LOGIN_SSO = "https://loginsso.telmex.com/nidp/idff/sso?id=custom-telmex"
URL_MI_TELMEX_HOGAR = "https://mitelmex.telmex.com/web/mitelmex-hogar"

SESSION_TTL_HOURS = 12
LIVE_ENV_FLAG = "PLUGINS_MX_TELMEX_LIVE"

# Alias legacy (mantener para compatibilidad con tests viejos)
URL_MI_TELMEX_LOGIN = URL_MI_TELMEX_LOGIN_SSO
URL_MI_TELMEX_FACTURAS = URL_TELMEX_PAGO_SIN_LOGIN


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
