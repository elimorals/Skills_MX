"""Tests mp_inmuebles24."""

from __future__ import annotations

import pytest

from mp_inmuebles24.client import Inmuebles24Client
from mp_inmuebles24.server import (
    BuscarInput,
    ComparablesInput,
    IdInput,
    PublicarInput,
    inm24_buscar_comparables_zona,
    inm24_buscar_inmuebles,
    inm24_listar_catalogos,
    inm24_obtener_detalle,
    inm24_publicar_listing,
)
from shared.errors import ValidationError


@pytest.fixture
def client() -> Inmuebles24Client:
    return Inmuebles24Client()


def test_buscar_mock(client: Inmuebles24Client) -> None:
    r = client.buscar_inmuebles("venta", "casa", "CDMX", limit=5)
    assert r["total_encontrados"] > 0
    assert len(r["resultados"]) >= 1


def test_buscar_tipo_invalido(client: Inmuebles24Client) -> None:
    with pytest.raises(ValidationError):
        client.buscar_inmuebles("alquiler", "casa", "CDMX")


def test_buscar_precio_inconsistente(client: Inmuebles24Client) -> None:
    with pytest.raises(ValidationError):
        client.buscar_inmuebles(
            "venta", "casa", "CDMX", precio_min=5000000, precio_max=1000000
        )


def test_detalle_mock(client: Inmuebles24Client) -> None:
    r = client.obtener_detalle("MLM-INM24-1234567")
    assert r["id"] == "MLM-INM24-1234567"
    assert "fotos_count" in r


def test_comparables_mock(client: Inmuebles24Client) -> None:
    r = client.buscar_comparables_zona("Polanco, CDMX", "departamento")
    assert "estadisticas_precio_mxn" in r
    assert r["estadisticas_precio_mxn"]["mediana"] > 0


def test_publicar_mock(client: Inmuebles24Client) -> None:
    r = client.publicar_listing("Casa demo en Polanco", 5_000_000, "venta", "casa")
    assert r["status"] == "borrador"
    assert "id_listing" in r


@pytest.mark.asyncio
async def test_buscar_tool() -> None:
    r = await inm24_buscar_inmuebles(
        BuscarInput(
            tipo_operacion="venta", tipo_inmueble="casa", ciudad="GDL", limit=3,
        )
    )
    assert "resultados" in r


@pytest.mark.asyncio
async def test_detalle_tool() -> None:
    r = await inm24_obtener_detalle(IdInput(id_inmueble="MLM-INM24-1234567"))
    assert r["id"] == "MLM-INM24-1234567"


@pytest.mark.asyncio
async def test_comparables_tool() -> None:
    r = await inm24_buscar_comparables_zona(
        ComparablesInput(ubicacion="Polanco", tipo_inmueble="departamento")
    )
    assert "estadisticas_precio_mxn" in r


@pytest.mark.asyncio
async def test_publicar_tool() -> None:
    r = await inm24_publicar_listing(
        PublicarInput(
            titulo="Departamento moderno con vista",
            precio_mxn=3500000,
            tipo_operacion="venta",
            tipo_inmueble="departamento",
        )
    )
    assert r["status"] == "borrador"


@pytest.mark.asyncio
async def test_catalogos() -> None:
    r = await inm24_listar_catalogos()
    assert "planes_publicacion" in r
    assert "premium" in r["planes_publicacion"]
