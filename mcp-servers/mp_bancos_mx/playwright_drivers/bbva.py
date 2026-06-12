"""Driver Playwright BBVA México.

⚠ Stub: implementar `_real_login()` con flujo:
1. https://www.bbva.mx → Banca en línea
2. Ingresar usuario + password
3. App push (espera asistida ~60s)
4. Capturar cookies
"""

from __future__ import annotations

from .base import BancoPlaywrightDriver


class BbvaDriver(BancoPlaywrightDriver):
    BANCO_CODIGO = "bbva"
    BANCO_NOMBRE = "BBVA México"
    PORTAL_URL = "https://www.bbva.mx"
    SESION_TTL_MINUTOS = 15
    ENV_USUARIO = "BBVA_USUARIO"
    ENV_PASSWORD = "BBVA_PASSWORD"
    ENV_EXTRAS = ()  # 2FA es app push, no env var

    def _real_login(self) -> None:
        """Pending: navegar a https://www.bbva.mx, login + 2FA app push asistido."""
        return  # stub
