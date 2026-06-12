"""End-to-end tests de los tools FastMCP."""

from __future__ import annotations

import pytest

from mp_aspel_contpaqi.server import (
    InstruccionesInput,
    ParsearExportInput,
    PeriodoInput,
    PeriodoSimpleInput,
    PolizaIdInput,
    aspel_get_poliza,
    aspel_listar_catalogos,
    aspel_listar_polizas,
    aspel_obtener_balance_general,
    aspel_obtener_balanza,
    aspel_obtener_catalogo_cuentas,
    aspel_obtener_estado_resultados,
    aspel_obtener_instrucciones_configuracion,
    aspel_parsear_export_csv,
)
from mp_aspel_contpaqi.tests.conftest import CSV_POLIZAS_DEMO


@pytest.mark.asyncio
async def test_listar_polizas() -> None:
    r = await aspel_listar_polizas(PeriodoInput(ejercicio=2026, mes=3))
    assert r["simulated"] is True
    assert r["total_polizas"] >= 1


@pytest.mark.asyncio
async def test_listar_polizas_filtro_tipo() -> None:
    r = await aspel_listar_polizas(
        PeriodoInput(ejercicio=2026, mes=3, tipo="INGRESOS")
    )
    assert all(p["tipo"] == "INGRESOS" for p in r["polizas"])


@pytest.mark.asyncio
async def test_get_poliza() -> None:
    r = await aspel_get_poliza(PolizaIdInput(numero="D-001"))
    assert r["numero"] == "D-001"


@pytest.mark.asyncio
async def test_balanza() -> None:
    r = await aspel_obtener_balanza(PeriodoSimpleInput(ejercicio=2026, mes=3))
    assert "cuentas" in r
    assert len(r["cuentas"]) > 0


@pytest.mark.asyncio
async def test_catalogo() -> None:
    r = await aspel_obtener_catalogo_cuentas()
    assert "cuentas" in r


@pytest.mark.asyncio
async def test_estado_resultados() -> None:
    r = await aspel_obtener_estado_resultados(
        PeriodoSimpleInput(ejercicio=2026, mes=3)
    )
    assert "utilidad_neta" in r


@pytest.mark.asyncio
async def test_balance_general() -> None:
    r = await aspel_obtener_balance_general(
        PeriodoSimpleInput(ejercicio=2026, mes=3)
    )
    assert "activo" in r


@pytest.mark.asyncio
async def test_parsear_export_csv() -> None:
    r = await aspel_parsear_export_csv(
        ParsearExportInput(tipo="polizas", contenido_csv=CSV_POLIZAS_DEMO)
    )
    assert r["tipo"] == "polizas"
    assert r["total"] == 2


@pytest.mark.asyncio
async def test_instrucciones_aspel() -> None:
    r = await aspel_obtener_instrucciones_configuracion(
        InstruccionesInput(erp="aspel_coi")
    )
    assert r["erp"] == "aspel_coi"
    assert len(r["pasos"]) > 5


@pytest.mark.asyncio
async def test_instrucciones_contpaqi() -> None:
    r = await aspel_obtener_instrucciones_configuracion(
        InstruccionesInput(erp="contpaqi")
    )
    assert r["erp"] == "contpaqi"


@pytest.mark.asyncio
async def test_listar_catalogos() -> None:
    r = await aspel_listar_catalogos()
    assert "tipo_poliza" in r
    assert "codigo_agrupador_sat" in r
    assert "401" in r["codigo_agrupador_sat"]
