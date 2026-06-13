"""Fixtures mp_predial_mx."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path: Path) -> None:
    """Aísla cada test: cache + bitácora en tmp + sin Playwright real."""
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))
    monkeypatch.delenv("MP_PLAYWRIGHT_PUBLIC", raising=False)
    monkeypatch.delenv("PLUGINS_MX_PLAYWRIGHT_REAL", raising=False)
