"""Driver Playwright Citibanamex.

⚠ Stub: implementar `_real_login()` con flujo:
1. https://www.banamex.com → BancaNet
2. Usuario + password
3. Token físico/challenge — usuario ingresa código asistido
"""

from __future__ import annotations

from .base import BancoPlaywrightDriver


class BanamexDriver(BancoPlaywrightDriver):
    BANCO_CODIGO = "banamex"
    BANCO_NOMBRE = "Citibanamex"
    PORTAL_URL = "https://www.banamex.com"
    SESION_TTL_MINUTOS = 10
    ENV_USUARIO = "BANAMEX_USUARIO"
    ENV_PASSWORD = "BANAMEX_PASSWORD"
    ENV_EXTRAS = ("BANAMEX_TOKEN_TYPE",)  # "fisico" | "challenge"

    def _real_login(self) -> None:
        return  # stub
