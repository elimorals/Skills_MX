"""Endpoints admin (protegidos por API key)."""

from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Query

from ..audit import WebhookAudit
from ..config import get_settings

router = APIRouter()


def _require_admin(x_admin_key: str | None) -> None:
    settings = get_settings()
    if not x_admin_key or x_admin_key != settings.admin_key:
        raise HTTPException(status_code=401, detail="invalid admin key")


@router.get("/webhooks/recent")
def recent(
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
    n: int = Query(default=100, ge=1, le=1000),
    source: str | None = Query(default=None),
) -> dict[str, object]:
    _require_admin(x_admin_key)
    audit = WebhookAudit()
    entries = audit.tail(n)
    if source:
        entries = [e for e in entries if e.get("source") == source]
    return {"count": len(entries), "entries": entries}
