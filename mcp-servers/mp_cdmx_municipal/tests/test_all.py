"""Tests mp_cdmx_municipal."""

from __future__ import annotations

import pytest

from mp_cdmx_municipal.client import CdmxMunicipalClient
from mp_cdmx_municipal.server import (
    FechaInput,
    PlacaInput,
    PredialInput,
    cdmx_consultar_hoy_no_circula,
    cdmx_consultar_multas,
    cdmx_consultar_predial,
    cdmx_consultar_tenencia,
    cdmx_listar_catalogos,
)
from shared.errors import ValidationError


@pytest.fixture
def client() -> CdmxMunicipalClient:
    return CdmxMunicipalClient()


def test_predial_mock(client: CdmxMunicipalClient) -> None:
    r = client.consultar_predial("1234567890")
    assert r["simulated"] is True
    assert "valor_catastral_mxn" in r


def test_predial_invalido(client: CdmxMunicipalClient) -> None:
    with pytest.raises(ValidationError):
        client.consultar_predial("ab")


def test_tenencia_mock(client: CdmxMunicipalClient) -> None:
    r = client.consultar_tenencia("ABC-123-D")
    assert r["placa"] == "ABC-123-D"
    assert r["status"] == "AL_CORRIENTE"


def test_multas_mock(client: CdmxMunicipalClient) -> None:
    r = client.consultar_multas("ABC-123-D")
    assert r["total_multas"] >= 1
    assert r["monto_adeudo_mxn"] > 0


def test_hoy_no_circula(client: CdmxMunicipalClient) -> None:
    r = client.consultar_calendario_hoy_no_circula("2026-03-15")
    assert r["fecha"] == "2026-03-15"
    assert "restricciones_del_dia" in r


@pytest.mark.asyncio
async def test_predial_tool() -> None:
    r = await cdmx_consultar_predial(PredialInput(cuenta_predial="1234567890"))
    assert "valor_catastral_mxn" in r


@pytest.mark.asyncio
async def test_tenencia_tool() -> None:
    r = await cdmx_consultar_tenencia(PlacaInput(placa="ABC-123-D"))
    assert r["placa"] == "ABC-123-D"


@pytest.mark.asyncio
async def test_multas_tool() -> None:
    r = await cdmx_consultar_multas(PlacaInput(placa="ABC-123-D"))
    assert "multas" in r


@pytest.mark.asyncio
async def test_hoy_no_circula_tool() -> None:
    r = await cdmx_consultar_hoy_no_circula(FechaInput(fecha="2026-03-15"))
    assert "restricciones_del_dia" in r


@pytest.mark.asyncio
async def test_catalogos() -> None:
    r = await cdmx_listar_catalogos()
    assert "hologramas" in r
    assert "00" in r["hologramas"]
