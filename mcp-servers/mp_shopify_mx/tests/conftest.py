"""Shared fixtures para mp_shopify_mx tests."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_state(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))
    monkeypatch.delenv("SHOPIFY_SHOP", raising=False)
    monkeypatch.delenv("SHOPIFY_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("SHOPIFY_API_VERSION", raising=False)
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
