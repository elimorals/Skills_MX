"""Tests mp_edomex_municipal."""

from __future__ import annotations

import pytest

from mp_edomex_municipal.client import EdomexMunicipalClient
from mp_edomex_municipal.server import (
    PlacaInput,
    PredialInput,
    TenenciaInput,
    edomex_consultar_multas,
    edomex_consultar_predial,
    edomex_consultar_tenencia,
    edomex_listar_catalogos,
)


@pytest.fixture
def client() -> EdomexMunicipalClient:
    return EdomexMunicipalClient()


def test_predial_mock(client: EdomexMunicipalClient) -> None:
    r = client.consultar_predial("Naucalpan", "123456")
    assert r["municipio"] == "Naucalpan"
    assert r["simulated"] is True


def test_tenencia_mock(client: EdomexMunicipalClient) -> None:
    r = client.consultar_tenencia("ABC-123-D", 2026)
    assert r["ejercicio"] == 2026


def test_multas_mock(client: EdomexMunicipalClient) -> None:
    r = client.consultar_multas("ABC-123-D")
    assert r["total_multas"] >= 1


def test_municipios_lista(client: EdomexMunicipalClient) -> None:
    lista = client.municipios_soportados()
    assert "Toluca" in lista
    assert "Naucalpan" in lista
    assert len(lista) >= 5


@pytest.mark.asyncio
async def test_predial_tool() -> None:
    r = await edomex_consultar_predial(
        PredialInput(municipio="Naucalpan", cuenta_predial="123456")
    )
    assert "valor_catastral_mxn" in r


@pytest.mark.asyncio
async def test_tenencia_tool() -> None:
    r = await edomex_consultar_tenencia(TenenciaInput(placa="ABC-123-D", ejercicio=2026))
    assert r["ejercicio"] == 2026


@pytest.mark.asyncio
async def test_multas_tool() -> None:
    r = await edomex_consultar_multas(PlacaInput(placa="ABC-123-D"))
    assert "multas" in r


@pytest.mark.asyncio
async def test_catalogos() -> None:
    r = await edomex_listar_catalogos()
    assert "municipios_predial_digital" in r
    assert "Toluca" in r["municipios_predial_digital"]
