"""Tests mp_multas_mx."""

from __future__ import annotations

import os

import pytest
import respx

from mp_multas_mx.catalogo_multas import PORTALES_MULTAS
from mp_multas_mx.client import MultasMxClient
from shared.errors import UpstreamError, ValidationError


@pytest.fixture
def client() -> MultasMxClient:
    return MultasMxClient()


@pytest.fixture
def mock_on(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")


@respx.mock
def test_cdmx_handoff_real(client: MultasMxClient):
    respx.get(PORTALES_MULTAS["cdmx"].url).respond(200, text='<input id="captcha_code">')
    r = client.consultar_multas("cdmx", "XYZ-98-76")
    assert r["simulated"] is False
    assert r["status"] == "requiere_humano"
    assert r["placa"] == "XYZ9876"


@respx.mock
def test_portal_caido_no_cae_a_mock(client: MultasMxClient):
    respx.get(PORTALES_MULTAS["jal"].url).respond(503)
    with pytest.raises(UpstreamError):
        client.consultar_multas("jal", "ABC-12-34")


def test_estado_sin_portal_vigente(client: MultasMxClient):
    with pytest.raises(ValidationError, match="sin portal vigente"):
        client.consultar_multas("yuc", "ABC-12-34")


def test_consultar_jal_mock(client: MultasMxClient, mock_on):
    r = client.consultar_multas("jal", "ABC-12-34")
    assert r["simulated"] is True
    assert "ABC-12-34" not in str(r)


def test_consultar_placa_invalida(client: MultasMxClient):
    with pytest.raises(ValidationError, match="formato"):
        client.consultar_multas("jal", "X")


def test_consultar_estado_invalido(client: MultasMxClient):
    with pytest.raises(ValidationError, match="no soportado"):
        client.consultar_multas("yyy", "ABC-12-34")


def test_estados_disponibles(client: MultasMxClient):
    r = client.estados_disponibles()
    assert set(r["soportados"]) == {"cdmx", "edomex", "jal", "nl", "nl_sanpedro"}
    assert "cdmx" in r["requieren_captcha"]
    assert "nl" not in r["requieren_captcha"]
    assert "yuc" in r["sin_portal_vigente"]


def test_no_leak_placa_en_bitacora(client: MultasMxClient, mock_on):
    client.consultar_multas("jal", "ABC-12-34")
    audit_dir = os.environ.get("PLUGINS_MX_AUDIT_DIR")
    if audit_dir and os.path.exists(audit_dir):
        for root, _, files in os.walk(audit_dir):
            for f in files:
                assert "ABC-12-34" not in open(os.path.join(root, f)).read()


@pytest.mark.live
def test_live_cdmx(client: MultasMxClient):
    assert client.consultar_multas("cdmx", "ABC1234")["portal_verificado"]["status_code"] == 200
