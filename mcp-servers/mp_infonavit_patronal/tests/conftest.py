"""Fixtures mp_infonavit_patronal."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.delenv("PLUGINS_MX_PLAYWRIGHT_REAL", raising=False)
    monkeypatch.delenv("INFONAVIT_RFC_PATRONAL", raising=False)
    monkeypatch.delenv("INFONAVIT_USUARIO", raising=False)
    monkeypatch.delenv("INFONAVIT_PASSWORD", raising=False)
