"""Driver Playwright Banorte.

⚠ Stub: 2FA SMS o soft token (TOTP). Si `BANORTE_SOFT_TOKEN_SEED` setado,
puede generar el código automáticamente con pyotp.
"""

from __future__ import annotations

from .base import BancoPlaywrightDriver


class BanorteDriver(BancoPlaywrightDriver):
    BANCO_CODIGO = "banorte"
    BANCO_NOMBRE = "Banorte"
    PORTAL_URL = "https://www.banorte.com"
    SESION_TTL_MINUTOS = 15
    ENV_USUARIO = "BANORTE_USUARIO"
    ENV_PASSWORD = "BANORTE_PASSWORD"
    ENV_EXTRAS = ("BANORTE_SOFT_TOKEN_SEED",)

    def _real_login(self) -> None:
        return  # stub

    def _generar_totp(self) -> str | None:
        """Genera código TOTP si BANORTE_SOFT_TOKEN_SEED está disponible.

        Requiere pyotp instalado. Si falta seed → None (login asistido).
        """
        seed = self.config.extra.get("BANORTE_SOFT_TOKEN_SEED")
        if not seed:
            return None
        try:
            import pyotp

            return pyotp.TOTP(seed).now()
        except ImportError:
            return None
