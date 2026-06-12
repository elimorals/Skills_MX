"""Tests mp_infonavit_patronal."""

from __future__ import annotations

import pytest

from mp_infonavit_patronal.client import InfonavitPatronalClient
from mp_infonavit_patronal.server import (
    DescuentoTrabajadorInput,
    EmisInput,
    RegistroInput,
    infonavit_consultar_avisos_pendientes,
    infonavit_consultar_creditos_trabajadores,
    infonavit_consultar_descuentos_mensuales,
    infonavit_descargar_emis,
    infonavit_listar_catalogos,
)
from shared.errors import UpstreamError, ValidationError


@pytest.fixture
def client() -> InfonavitPatronalClient:
    return InfonavitPatronalClient()


def test_creditos_mock(client: InfonavitPatronalClient) -> None:
    r = client.consultar_creditos_trabajadores("ABC1234567X")
    assert r["simulated"] is True
    assert r["total_trabajadores_con_credito"] >= 1
    assert any(c["status"] == "VIGENTE" for c in r["creditos"])


def test_emis_mock(client: InfonavitPatronalClient) -> None:
    r = client.descargar_emis("ABC1234567X", 3, 2026)
    assert r["total_a_pagar"] > 0
    assert len(r["detalle_por_trabajador"]) > 0


def test_emis_mes_invalido(client: InfonavitPatronalClient) -> None:
    with pytest.raises(ValidationError):
        client.descargar_emis("ABC1234567X", 13, 2026)


def test_descuentos_mensuales(client: InfonavitPatronalClient) -> None:
    r = client.consultar_descuentos_mensuales("ABC1234567X", "12345678901", 3, 2026)
    assert r["tiene_credito"] is True


def test_avisos_mock(client: InfonavitPatronalClient) -> None:
    r = client.consultar_avisos_pendientes("ABC1234567X")
    assert r["total_avisos"] >= 1


def test_path_real_bloqueado(monkeypatch) -> None:
    monkeypatch.setenv("INFONAVIT_USUARIO", "demo")
    monkeypatch.setenv("INFONAVIT_PASSWORD", "demo")
    c = InfonavitPatronalClient()
    with pytest.raises(UpstreamError):
        c.consultar_creditos_trabajadores("ABC1234567X")


@pytest.mark.asyncio
async def test_creditos_tool() -> None:
    r = await infonavit_consultar_creditos_trabajadores(
        RegistroInput(registro_patronal="ABC1234567X")
    )
    assert "creditos" in r


@pytest.mark.asyncio
async def test_emis_tool() -> None:
    r = await infonavit_descargar_emis(
        EmisInput(registro_patronal="ABC1234567X", mes=3, ejercicio=2026)
    )
    assert r["mes"] == 3


@pytest.mark.asyncio
async def test_descuentos_tool() -> None:
    r = await infonavit_consultar_descuentos_mensuales(
        DescuentoTrabajadorInput(
            registro_patronal="ABC1234567X",
            nss="12345678901",
            mes=3,
            ejercicio=2026,
        )
    )
    assert "valor_descuento" in r


@pytest.mark.asyncio
async def test_avisos_tool() -> None:
    r = await infonavit_consultar_avisos_pendientes(
        RegistroInput(registro_patronal="ABC1234567X")
    )
    assert "avisos" in r


@pytest.mark.asyncio
async def test_catalogos_tool() -> None:
    r = await infonavit_listar_catalogos()
    assert "tipos_descuento" in r
    assert "VSM" in r["tipos_descuento"]
