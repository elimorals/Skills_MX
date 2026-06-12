"""Tests mp_monterrey_municipal."""

from __future__ import annotations

import pytest

from mp_monterrey_municipal.client import MonterreyMunicipalClient
from mp_monterrey_municipal.server import (
    FechaInput,
    PlacaInput,
    PredialInput,
    nl_consultar_calidad_aire,
    nl_consultar_multas,
    nl_consultar_predial,
    nl_listar_catalogos,
)
from shared.errors import ValidationError


@pytest.fixture
def client() -> MonterreyMunicipalClient:
    return MonterreyMunicipalClient()


def test_predial_mock(client: MonterreyMunicipalClient) -> None:
    r = client.consultar_predial("Monterrey", "123456")
    assert r["municipio"] == "Monterrey"


def test_predial_municipio_invalido(client: MonterreyMunicipalClient) -> None:
    with pytest.raises(ValidationError):
        client.consultar_predial("Mérida", "123")  # no es del AMM


def test_multas_mock(client: MonterreyMunicipalClient) -> None:
    r = client.consultar_multas("ABC-123-D")
    assert r["estado"] == "NL"


def test_calidad_aire_mock(client: MonterreyMunicipalClient) -> None:
    r = client.consultar_calidad_aire_nl("2026-03-15")
    assert "calidad_aire_imeca" in r


@pytest.mark.asyncio
async def test_predial_tool() -> None:
    r = await nl_consultar_predial(
        PredialInput(municipio="San Pedro Garza García", cuenta_predial="123456")
    )
    assert r["municipio"] == "San Pedro Garza García"


@pytest.mark.asyncio
async def test_multas_tool() -> None:
    r = await nl_consultar_multas(PlacaInput(placa="ABC-123-D"))
    assert "multas" in r


@pytest.mark.asyncio
async def test_calidad_aire_tool() -> None:
    r = await nl_consultar_calidad_aire(FechaInput(fecha="2026-03-15"))
    assert "calidad_aire_imeca" in r


@pytest.mark.asyncio
async def test_catalogos() -> None:
    r = await nl_listar_catalogos()
    assert "Monterrey" in r["municipios_amm"]
    assert "San Pedro Garza García" in r["municipios_amm"]
