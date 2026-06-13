"""Tests cliente standalone predial_mx."""

from __future__ import annotations

import pytest

from predial_mx_client import (
    PredialMxClient,
    PredialResponse,
    MunicipioInfo,
    NoSoportadoError,
)


@pytest.fixture
def client() -> PredialMxClient:
    return PredialMxClient(modo="mock")


def test_init_modo_mock():
    c = PredialMxClient(modo="mock")
    assert c.modo == "mock"


def test_init_modo_invalido():
    with pytest.raises(ValueError, match="mock.*real"):
        PredialMxClient(modo="otro")


def test_consultar_devuelve_response(client: PredialMxClient):
    r = client.consultar("jal", "guadalajara", "U12345678")
    assert isinstance(r, PredialResponse)
    assert r.estado == "jal"
    assert r.simulated is True


def test_consultar_response_helpers(client: PredialMxClient):
    r = client.consultar("jal", "guadalajara", "U001")
    # Properties accesibles
    assert isinstance(r.al_corriente, bool)
    assert isinstance(r.es_real, bool)
    assert r.es_real == (not r.simulated)


def test_consultar_municipio_no_existe(client: PredialMxClient):
    with pytest.raises(NoSoportadoError):
        client.consultar("jal", "municipio_imaginario", "12345")


def test_listar_municipios(client: PredialMxClient):
    muns = client.listar_municipios()
    assert len(muns) >= 200
    assert all(isinstance(m, MunicipioInfo) for m in muns)


def test_listar_validados(client: PredialMxClient):
    validados = client.listar_validados()
    assert all(m.validado for m in validados)
    assert len(validados) >= 30


def test_listar_validados_por_estado(client: PredialMxClient):
    validados_jal = client.listar_validados(estado="jal")
    assert all(m.estado == "jal" and m.validado for m in validados_jal)


def test_buscar_fuzzy(client: PredialMxClient):
    res = client.buscar("guadal")
    assert len(res) >= 1
    assert any("guadalajara" in m.clave.lower() for m in res)


def test_estadisticas(client: PredialMxClient):
    s = client.estadisticas()
    assert s["municipios_totales"] >= 200
    assert s["municipios_validados"] >= 30
    assert "saas" in s


def test_es_soportado(client: PredialMxClient):
    assert client.es_soportado("jal", "guadalajara") is True
    assert client.es_soportado("xx", "fake") is False


def test_es_validado(client: PredialMxClient):
    # Guadalajara validado en el catálogo
    assert client.es_validado("jal", "guadalajara") is True
    # Tlaquepaque en catálogo pero NO validado
    assert client.es_validado("jal", "tlaquepaque") is False
