"""Fixtures mp_buro_credito_personal."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.delenv("PLUGINS_MX_PLAYWRIGHT_REAL", raising=False)
    monkeypatch.delenv("BURO_API_KEY", raising=False)
    monkeypatch.delenv("BURO_USUARIO", raising=False)
    monkeypatch.delenv("BURO_PASSWORD", raising=False)


VALID_TOKEN = "demo_authorization_token_signed_by_titular_2026_abc123def456"
SHORT_TOKEN = "short"
