"""Health endpoint para liveness/readiness probes."""

from __future__ import annotations

from fastapi import APIRouter

from .. import __version__
from ..config import Settings, get_settings

router = APIRouter()


@router.get("/webhooks/health")
def health() -> dict[str, object]:
    settings = get_settings()
    return {
        "ok": True,
        "version": __version__,
        "mode": settings.mode,
        "idempotency_backend": settings.idempotency_backend,
    }
