"""Entry point del webhook receiver.

Ejecuta con: `uvicorn app.main:app --host 0.0.0.0 --port 8787`
"""

from __future__ import annotations

import logging

from fastapi import FastAPI

from . import __version__
from .config import get_settings
from .routes import admin, health, webhooks


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    app = FastAPI(
        title="plugins-mx webhook receiver",
        version=__version__,
        description=(
            "Webhook receiver para plugins-mx — 12 handlers (Stripe, MP, Conekta, "
            "Facturama, Meta WhatsApp, GitHub, Calendly, Typeform, ML, Banxico CEP, "
            f"IMSS Buzón, CONDUSEF). Modo: {settings.mode}."
        ),
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(webhooks.router, tags=["webhooks"])
    app.include_router(admin.router, tags=["admin"])

    return app


app = create_app()
