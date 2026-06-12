"""Tests mp_softrestaurant."""

from __future__ import annotations

from pathlib import Path

import pytest

from mp_softrestaurant.client import SoftRestaurantClient
from mp_softrestaurant.export_parser import (
    parsear_csv_corte_z,
    parsear_csv_platillos_vendidos,
)
from mp_softrestaurant.server import (
    FechaInput,
    ParsearInput,
    PeriodoInput,
    PeriodoSimpleInput,
    softrest_corte_z,
    softrest_inventario_actual,
    softrest_listar_catalogos,
    softrest_meseros_ventas,
    softrest_mesas_estatus,
    softrest_parsear_export,
    softrest_platillos_vendidos,
    softrest_ventas_periodo,
)
from mp_softrestaurant.tests.conftest import CSV_CORTE_Z_DEMO, CSV_PLATILLOS_DEMO
from shared.errors import McpError, ValidationError


# ---------- export parser ----------


def test_parsear_corte_z() -> None:
    r = parsear_csv_corte_z(CSV_CORTE_Z_DEMO)
    assert r["total_dia_mxn"] == "12100.00"
    assert "efectivo" in r["metodos_pago"]
    assert r["metodos_pago"]["efectivo"] == "8200.00"


def test_parsear_platillos() -> None:
    r = parsear_csv_platillos_vendidos(CSV_PLATILLOS_DEMO)
    assert len(r) == 4
    tacos = next(p for p in r if p["platillo"] == "Tacos al pastor")
    assert tacos["cantidad_vendida"] == 312


# ---------- client mock ----------


@pytest.fixture
def client() -> SoftRestaurantClient:
    return SoftRestaurantClient()


def test_corte_z_mock(client: SoftRestaurantClient) -> None:
    r = client.corte_z_del_dia("2026-03-15")
    assert r["simulated"] is True
    assert float(r["total_dia_mxn"]) > 0


def test_corte_z_fecha_invalida(client: SoftRestaurantClient) -> None:
    with pytest.raises(ValidationError):
        client.corte_z_del_dia("bad")


def test_ventas_periodo(client: SoftRestaurantClient) -> None:
    r = client.ventas_periodo("2026-03-01", "2026-03-15")
    assert "total_ventas_mxn" in r


def test_inventario(client: SoftRestaurantClient) -> None:
    r = client.inventario_actual()
    assert r["simulated"] is True


def test_platillos(client: SoftRestaurantClient) -> None:
    r = client.platillos_vendidos("2026-03")
    assert len(r["top_5_mas_vendidos"]) > 0


def test_meseros(client: SoftRestaurantClient) -> None:
    r = client.meseros_ventas("2026-03-15")
    assert "meseros" in r


def test_mesas_estatus(client: SoftRestaurantClient) -> None:
    r = client.mesas_estatus()
    assert "distribucion" in r
    assert r["distribucion"]["libre"] >= 0


def test_parsear_export_inline_corte_z(client: SoftRestaurantClient) -> None:
    r = client.parsear_export("corte_z", CSV_CORTE_Z_DEMO)
    assert r["tipo"] == "corte_z"


def test_parsear_export_tipo_invalido(client: SoftRestaurantClient) -> None:
    with pytest.raises(McpError):
        client.parsear_export("desconocido", "data,1\n")


# ---------- modo real con exports ----------


@pytest.fixture
def exports_dir(tmp_path: Path, monkeypatch) -> Path:
    d = tmp_path / "softrest_exports"
    d.mkdir()
    (d / "corte_z_20260315.csv").write_text(CSV_CORTE_Z_DEMO, encoding="utf-8")
    (d / "platillos_202603.csv").write_text(CSV_PLATILLOS_DEMO, encoding="utf-8")
    monkeypatch.setenv("SOFT_RESTAURANT_EXPORTS_DIR", str(d))
    return d


def test_corte_z_real(exports_dir: Path) -> None:
    client = SoftRestaurantClient()
    r = client.corte_z_del_dia("2026-03-15")
    assert r.get("simulated") is False
    assert float(r["total_dia_mxn"]) > 0


def test_platillos_real(exports_dir: Path) -> None:
    client = SoftRestaurantClient()
    r = client.platillos_vendidos("2026-03")
    assert r.get("simulated") is False
    assert r["total_platillos_distintos"] == 4


# ---------- server tools ----------


@pytest.mark.asyncio
async def test_corte_tool() -> None:
    r = await softrest_corte_z(FechaInput(fecha="2026-03-15"))
    assert "total_dia_mxn" in r


@pytest.mark.asyncio
async def test_ventas_tool() -> None:
    r = await softrest_ventas_periodo(
        PeriodoInput(desde="2026-03-01", hasta="2026-03-15")
    )
    assert "total_ventas_mxn" in r


@pytest.mark.asyncio
async def test_inventario_tool() -> None:
    r = await softrest_inventario_actual()
    assert "items_bajo_stock" in r


@pytest.mark.asyncio
async def test_platillos_tool() -> None:
    r = await softrest_platillos_vendidos(PeriodoSimpleInput(periodo="2026-03"))
    assert "top_5_mas_vendidos" in r


@pytest.mark.asyncio
async def test_meseros_tool() -> None:
    r = await softrest_meseros_ventas(FechaInput(fecha="2026-03-15"))
    assert "meseros" in r


@pytest.mark.asyncio
async def test_mesas_tool() -> None:
    r = await softrest_mesas_estatus()
    assert "tasa_ocupacion" in r


@pytest.mark.asyncio
async def test_parsear_tool() -> None:
    r = await softrest_parsear_export(
        ParsearInput(tipo="corte_z", contenido_csv=CSV_CORTE_Z_DEMO)
    )
    assert r["tipo"] == "corte_z"


@pytest.mark.asyncio
async def test_catalogos_tool() -> None:
    r = await softrest_listar_catalogos()
    assert "categorias_menu" in r
    assert "fuertes_carne" in r["categorias_menu"]
