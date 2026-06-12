"""Fixtures comunes para tests del webhook receiver."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _isolate_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Mantén audit log + idempotency DB fuera del filesystem del usuario."""
    audit_dir = tmp_path / "audit"
    audit_dir.mkdir()
    idemp_db = tmp_path / "idempotency.db"
    monkeypatch.setenv("PLUGINS_MX_WEBHOOKS_AUDIT_DIR", str(audit_dir))
    monkeypatch.setenv("PLUGINS_MX_WEBHOOKS_IDEMPOTENCY_PATH", str(idemp_db))
    monkeypatch.setenv("PLUGINS_MX_WEBHOOKS_IDEMPOTENCY_BACKEND", "memory")
    monkeypatch.setenv("PLUGINS_MX_WEBHOOKS_MODE", "mock")
    monkeypatch.setenv("PLUGINS_MX_WEBHOOKS_ADMIN_KEY", "test-admin-key")
    # Reset singletons that capture settings at import
    from app.routes import webhooks as routes_webhooks

    routes_webhooks._STORE = None
    yield


@pytest.fixture()
def app_client() -> TestClient:
    from app.config import get_settings
    # Re-leer settings desde env del test
    get_settings.cache_clear() if hasattr(get_settings, "cache_clear") else None

    from app.main import create_app

    return TestClient(create_app())
