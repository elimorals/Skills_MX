"""Driver Playwright Santander México.

⚠ Stub: 2FA biométrico/app — requiere usuario presente.
"""

from __future__ import annotations

from .base import BancoPlaywrightDriver


class SantanderDriver(BancoPlaywrightDriver):
    BANCO_CODIGO = "santander"
    BANCO_NOMBRE = "Santander México"
    PORTAL_URL = "https://www.santandernet.com.mx"
    SESION_TTL_MINUTOS = 20
    ENV_USUARIO = "SANTANDER_USUARIO"
    ENV_PASSWORD = "SANTANDER_PASSWORD"
    ENV_EXTRAS = ()

    def _real_login(self) -> None:
        return  # stub
