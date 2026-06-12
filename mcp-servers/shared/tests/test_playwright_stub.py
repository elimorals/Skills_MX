"""Tests para shared/playwright_stub.py."""

from __future__ import annotations

import pytest

from shared.errors import UpstreamError
from shared.playwright_stub import (
    detectar_modo_playwright,
    info_path_real,
    mock_response_playwright,
    raise_playwright_real_no_implementado,
)


def test_modo_mock_sin_credenciales(monkeypatch) -> None:
    monkeypatch.delenv("DEMO_TOKEN", raising=False)
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.delenv("PLUGINS_MX_PLAYWRIGHT_REAL", raising=False)
    assert detectar_modo_playwright(["DEMO_TOKEN"]) == "mock"


def test_modo_mock_forzado(monkeypatch) -> None:
    monkeypatch.setenv("DEMO_TOKEN", "demo")
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    assert detectar_modo_playwright(["DEMO_TOKEN"]) == "mock"


def test_modo_blocked_credenciales_sin_optin(monkeypatch) -> None:
    monkeypatch.setenv("DEMO_TOKEN", "demo")
    monkeypatch.delenv("PLUGINS_MX_PLAYWRIGHT_REAL", raising=False)
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    assert detectar_modo_playwright(["DEMO_TOKEN"]) == "blocked"


def test_modo_real_con_optin(monkeypatch) -> None:
    monkeypatch.setenv("DEMO_TOKEN", "demo")
    monkeypatch.setenv("PLUGINS_MX_PLAYWRIGHT_REAL", "1")
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    assert detectar_modo_playwright(["DEMO_TOKEN"]) == "real"


def test_mock_response_marca_simulated() -> None:
    r = mock_response_playwright({"data": "x"}, portal="banco_demo")
    assert r["simulated"] is True
    assert "data" in r
    assert any("banco_demo" in a for a in r["advertencias"])


def test_mock_response_con_nota_extra() -> None:
    r = mock_response_playwright({}, portal="x", nota_extra="Detalle adicional.")
    assert any("Detalle adicional." in a for a in r["advertencias"])


def test_raise_playwright_real_no_implementado() -> None:
    with pytest.raises(UpstreamError) as exc_info:
        raise_playwright_real_no_implementado("portal_x")
    assert "portal_x" in str(exc_info.value)


def test_info_path_real_retorna_dict() -> None:
    info = info_path_real()
    assert "como_activar_real" in info
    assert "PLUGINS_MX_PLAYWRIGHT_REAL" in info["como_activar_real"]
