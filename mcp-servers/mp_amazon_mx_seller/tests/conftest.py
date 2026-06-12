"""Fixtures mp_amazon_mx_seller."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.delenv("AMAZON_SP_REFRESH_TOKEN", raising=False)
    monkeypatch.delenv("AMAZON_SP_CLIENT_ID", raising=False)
    monkeypatch.delenv("AMAZON_SP_CLIENT_SECRET", raising=False)
