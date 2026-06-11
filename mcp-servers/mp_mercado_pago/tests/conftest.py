"""Shared fixtures for mp_mercado_pago tests."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_state(monkeypatch, tmp_path: Path) -> None:
    """Isolate cache + audit + no real MP credentials."""
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))
    monkeypatch.delenv("MERCADOPAGO_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)


@pytest.fixture
def simple_preference() -> dict:
    """A minimal preference payload for create_preference."""
    return {
        "items": [
            {
                "title": "Consultoría 1 hora",
                "quantity": 1,
                "unit_price": 1500.00,
                "currency_id": "MXN",
            }
        ],
        "external_reference": "cot-123",
    }
