"""Shared fixtures for mp_mercado_libre tests."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_state(monkeypatch, tmp_path: Path) -> None:
    """Isolate cache + audit + no real ML credentials."""
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))
    monkeypatch.delenv("ML_APP_ID", raising=False)
    monkeypatch.delenv("ML_SECRET", raising=False)
    monkeypatch.delenv("ML_REFRESH_TOKEN", raising=False)
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
