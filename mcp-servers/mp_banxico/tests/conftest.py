"""Shared pytest fixtures for mp_banxico tests.

Every test runs with isolated cache + audit dirs and no real BANXICO_TOKEN.
That keeps the suite deterministic and offline.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_state(monkeypatch, tmp_path: Path) -> None:
    """Isolate cache + audit log per test so they never collide."""
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))
    # Ensure no real token leaks in from the developer's environment
    monkeypatch.delenv("BANXICO_TOKEN", raising=False)
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
