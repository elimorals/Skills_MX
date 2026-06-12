"""Settings cargadas desde .env / variables de entorno.

En modo `mock` todas las firmas se aceptan (para tests/dev). En `production`
todas las firmas son validadas estrictamente.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings del webhook receiver.

    Importante: ningún secret se loguea. `bitacora.py` los hashea.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- general ---
    host: str = Field(default="0.0.0.0", alias="PLUGINS_MX_WEBHOOKS_HOST")
    port: int = Field(default=8787, alias="PLUGINS_MX_WEBHOOKS_PORT")
    log_level: str = Field(default="info", alias="PLUGINS_MX_WEBHOOKS_LOG_LEVEL")
    mode: Literal["mock", "production"] = Field(
        default="mock", alias="PLUGINS_MX_WEBHOOKS_MODE"
    )
    admin_key: str = Field(
        default="dev-only-key", alias="PLUGINS_MX_WEBHOOKS_ADMIN_KEY"
    )

    # --- idempotency ---
    idempotency_backend: Literal["sqlite", "memory"] = Field(
        default="sqlite", alias="PLUGINS_MX_WEBHOOKS_IDEMPOTENCY_BACKEND"
    )
    idempotency_path: str = Field(
        default="~/.cache/plugins-mx/webhooks/idempotency.db",
        alias="PLUGINS_MX_WEBHOOKS_IDEMPOTENCY_PATH",
    )

    # --- per-service secrets (None permitido en mock) ---
    stripe_secret: str | None = Field(default=None, alias="STRIPE_WEBHOOK_SECRET")
    mercadopago_secret: str | None = Field(
        default=None, alias="MERCADOPAGO_WEBHOOK_SECRET"
    )
    conekta_secret: str | None = Field(default=None, alias="CONEKTA_WEBHOOK_SECRET")
    facturama_bearer: str | None = Field(
        default=None, alias="FACTURAMA_WEBHOOK_BEARER"
    )
    facturama_allowed_ips: str = Field(
        default="", alias="FACTURAMA_WEBHOOK_ALLOWED_IPS"
    )
    meta_whatsapp_verify_token: str | None = Field(
        default=None, alias="META_WHATSAPP_VERIFY_TOKEN"
    )
    meta_whatsapp_app_secret: str | None = Field(
        default=None, alias="META_WHATSAPP_APP_SECRET"
    )
    github_secret: str | None = Field(default=None, alias="GITHUB_WEBHOOK_SECRET")
    calendly_secret: str | None = Field(default=None, alias="CALENDLY_WEBHOOK_SECRET")
    typeform_secret: str | None = Field(default=None, alias="TYPEFORM_WEBHOOK_SECRET")
    mercadolibre_allowed_ips: str = Field(
        default="", alias="MERCADOLIBRE_ALLOWED_IPS"
    )

    @property
    def is_mock(self) -> bool:
        return self.mode == "mock"

    @property
    def idempotency_resolved_path(self) -> Path:
        return Path(self.idempotency_path).expanduser()


def get_settings() -> Settings:
    """Factory function para Settings (override-able en tests)."""
    return Settings()
