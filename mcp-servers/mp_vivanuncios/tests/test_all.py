"""Tests mp_vivanuncios."""

from __future__ import annotations

import pytest

from mp_vivanuncios.client import VivanunciosClient
from mp_vivanuncios.server import (
    BuscarInput,
    IdInput,
    PublicarInput,
    viv_buscar_anuncios,
    viv_listar_catalogos,
    viv_obtener_detalle,
    viv_publicar_anuncio,
)
from shared.errors import ValidationError


@pytest.fixture
def client() -> VivanunciosClient:
    return VivanunciosClient()


def test_buscar_mock(client: VivanunciosClient) -> None:
    r = client.buscar_anuncios("vehiculos", "Toyota Corolla", "Monterrey")
    assert r["total_encontrados"] > 0


def test_buscar_categoria_invalida(client: VivanunciosClient) -> None:
    with pytest.raises(ValidationError):
        client.buscar_anuncios("xxx_invalida", "demo", "CDMX")


def test_buscar_query_vacia(client: VivanunciosClient) -> None:
    with pytest.raises(ValidationError):
        client.buscar_anuncios("vehiculos", "", "CDMX")


def test_detalle_mock(client: VivanunciosClient) -> None:
    r = client.obtener_detalle("VIV-987654321")
    assert r["id"] == "VIV-987654321"


def test_publicar_mock(client: VivanunciosClient) -> None:
    r = client.publicar_anuncio("Toyota Corolla 2022 SE — único dueño", "vehiculos", 285000)
    assert r["status"] == "moderacion"


@pytest.mark.asyncio
async def test_buscar_tool() -> None:
    r = await viv_buscar_anuncios(
        BuscarInput(categoria="inmuebles", query="casa", ciudad="GDL", limit=3)
    )
    assert "resultados" in r


@pytest.mark.asyncio
async def test_detalle_tool() -> None:
    r = await viv_obtener_detalle(IdInput(id_anuncio="VIV-987654321"))
    assert "vendedor" in r


@pytest.mark.asyncio
async def test_publicar_tool() -> None:
    r = await viv_publicar_anuncio(
        PublicarInput(
            titulo="iPhone 14 Pro 256GB excelente estado",
            categoria="electronica",
            precio_mxn=18500.00,
        )
    )
    assert r["status"] == "moderacion"


@pytest.mark.asyncio
async def test_catalogos() -> None:
    r = await viv_listar_catalogos()
    assert "vehiculos" in r["categorias"]
    assert "diferencias_vs_inmuebles24" in r
