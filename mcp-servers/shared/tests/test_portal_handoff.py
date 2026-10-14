"""Tests shared.portal_handoff (unitarios con respx + live opt-in)."""

from __future__ import annotations

import time

import httpx
import pytest
import respx

from shared import portal_handoff as ph
from shared.errors import UpstreamError

TODOS = [
    ph.SAF_CDMX_ADEUDOS, ph.OVICA_CDMX_PREDIAL, ph.EDOMEX_INFRACCIONES,
    ph.EDOMEX_RECAUDACION, ph.SAN_PEDRO_MULTAS, ph.JALISCO_ADEUDOS,
    ph.ICVNL_ESTADO_CUENTA, ph.IGECEM_EDOMEX,
]


@respx.mock
def test_handoff_portal_ok() -> None:
    respx.get(ph.SAF_CDMX_ADEUDOS.url).respond(200, text='<input id="captcha_code">')
    r = ph.handoff_humano(ph.SAF_CDMX_ADEUDOS, placa="ABC123")
    assert r["simulated"] is False
    assert r["status"] == "requiere_humano"
    assert r["captcha_tipo"] == "imagen"
    assert r["placa"] == "ABC123"
    assert r["portal_verificado"]["status_code"] == 200
    assert r["url"] == ph.SAF_CDMX_ADEUDOS.url and r["requiere_humano"] is True


def test_armar_handoff_forma_unica() -> None:
    r = ph.armar_handoff(motivo="login", url="https://x", pasos=("a",), folio="F1")
    assert set(r) == {
        "requiere_humano", "status", "consultado", "simulated", "motivo", "detalle",
        "portal", "url", "pasos", "captcha_tipo", "campos_prellenados",
        "portal_verificado", "folio",
    }
    assert r["requiere_humano"] is True and r["status"] == "requiere_humano"
    assert r["consultado"] is False and r["simulated"] is False
    assert r["pasos"] == ["a"] and r["campos_prellenados"] == {}


@respx.mock
def test_portal_caido_es_upstream_error() -> None:
    respx.get(ph.SAF_CDMX_ADEUDOS.url).respond(503)
    with pytest.raises(UpstreamError):
        ph.handoff_humano(ph.SAF_CDMX_ADEUDOS)


@respx.mock
def test_portal_cambiado_es_upstream_error() -> None:
    respx.get(ph.OVICA_CDMX_PREDIAL.url).respond(200, text="<html>sin verificacion</html>")
    with pytest.raises(UpstreamError, match="cambió"):
        ph.verificar_portal(ph.OVICA_CDMX_PREDIAL)


@respx.mock
def test_error_de_red_es_upstream_error() -> None:
    respx.get(ph.JALISCO_ADEUDOS.url).mock(side_effect=httpx.ConnectError("dns"))
    with pytest.raises(UpstreamError):
        ph.verificar_portal(ph.JALISCO_ADEUDOS)


def test_mock_forzado(monkeypatch) -> None:
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    assert ph.mock_forzado() is False
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    assert ph.mock_forzado() is True


@pytest.mark.live
def test_live_todos_los_portales() -> None:
    """Un GET por portal, ≥5 s entre llamadas. Ninguno recibe datos de particulares."""
    for i, portal in enumerate(TODOS):
        if i:
            time.sleep(5)
        ev = ph.verificar_portal(portal)
        assert ev["status_code"] == 200, portal.clave
