"""Fixtures compartidos para mp_conekta tests."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_state(monkeypatch, tmp_path: Path) -> None:
    """Aisla cache + audit y default a mock (sin CONEKTA_API_KEY)."""
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))
    monkeypatch.delenv("CONEKTA_API_KEY", raising=False)
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)


# Constants for tests
DEMO_SECRET = "whsec_demo_1234567890abcdef"
DEMO_CUSTOMER = {
    "name": "Juan Demo",
    "email": "juan.demo@example.mx",
    "phone": "+525512345678",
}
