"""Tests para mp_imss_patronal."""

from __future__ import annotations

import pytest

from mp_imss_patronal.client import ImssPatronalClient
from mp_imss_patronal.server import (
    CedulaInput,
    EmcrInput,
    MovimientoInput,
    RegistroInput,
    SbcInput,
    imss_consultar_avisos_pendientes,
    imss_consultar_emcr,
    imss_consultar_padron_trabajadores,
    imss_consultar_sbc,
    imss_descargar_cedula_autodeterminacion,
    imss_enviar_movimiento_afiliatorio,
    imss_listar_catalogos,
)
from shared.errors import UpstreamError, ValidationError


@pytest.fixture
def client() -> ImssPatronalClient:
    return ImssPatronalClient()


# ---------- client ----------


def test_avisos_mock(client: ImssPatronalClient) -> None:
    r = client.consultar_avisos_pendientes("ABC1234567X")
    assert r["simulated"] is True
    assert r["total_pendientes"] >= 1


def test_alta_trabajador_mock(client: ImssPatronalClient) -> None:
    r = client.enviar_movimiento_afiliatorio(
        "ABC1234567X", "12345678901", "08", salario_diario=850.00
    )
    assert r["simulated"] is True
    assert r["tipo_movimiento"] == "08"


def test_baja_trabajador_mock(client: ImssPatronalClient) -> None:
    r = client.enviar_movimiento_afiliatorio(
        "ABC1234567X", "12345678901", "02", causa_baja="02"
    )
    assert r["tipo_movimiento"] == "02"
    assert r["causa_baja"] == "02"


def test_alta_sin_salario_falla(client: ImssPatronalClient) -> None:
    with pytest.raises(ValidationError):
        client.enviar_movimiento_afiliatorio(
            "ABC1234567X", "12345678901", "08", salario_diario=None
        )


def test_baja_sin_causa_falla(client: ImssPatronalClient) -> None:
    with pytest.raises(ValidationError):
        client.enviar_movimiento_afiliatorio(
            "ABC1234567X", "12345678901", "02", causa_baja=None
        )


def test_tipo_movimiento_invalido_falla(client: ImssPatronalClient) -> None:
    with pytest.raises(ValidationError):
        client.enviar_movimiento_afiliatorio(
            "ABC1234567X", "12345678901", "99",
        )


def test_cedula_mock(client: ImssPatronalClient) -> None:
    r = client.descargar_cedula_autodeterminacion("ABC1234567X", 1, 2026)
    assert r["bimestre"] == 1
    assert r["total_a_pagar"] > 0


def test_cedula_bimestre_invalido(client: ImssPatronalClient) -> None:
    with pytest.raises(ValidationError):
        client.descargar_cedula_autodeterminacion("ABC1234567X", 9, 2026)


def test_sbc_mock(client: ImssPatronalClient) -> None:
    r = client.consultar_salario_diario_integrado("ABC1234567X", "12345678901")
    assert r["simulated"] is True
    assert "sbc_diario" in r


def test_padron_mock(client: ImssPatronalClient) -> None:
    r = client.consultar_padron_trabajadores("ABC1234567X")
    assert r["total_trabajadores"] > 0


def test_path_real_bloqueado(monkeypatch) -> None:
    monkeypatch.setenv("IMSS_EFIRMA_CERT", "/tmp/demo.cer")
    c = ImssPatronalClient()
    with pytest.raises(UpstreamError):
        c.consultar_avisos_pendientes("ABC1234567X")


# ---------- server tools ----------


@pytest.mark.asyncio
async def test_avisos_tool() -> None:
    r = await imss_consultar_avisos_pendientes(RegistroInput(registro_patronal="ABC1234567X"))
    assert "avisos" in r


@pytest.mark.asyncio
async def test_alta_tool() -> None:
    r = await imss_enviar_movimiento_afiliatorio(
        MovimientoInput(
            registro_patronal="ABC1234567X",
            nss="12345678901",
            tipo_movimiento="08",
            salario_diario=850.00,
        )
    )
    assert r["estatus"] == "PENDIENTE_ALTA"


@pytest.mark.asyncio
async def test_cedula_tool() -> None:
    r = await imss_descargar_cedula_autodeterminacion(
        CedulaInput(registro_patronal="ABC1234567X", bimestre=1, ejercicio=2026)
    )
    assert r["bimestre"] == 1


@pytest.mark.asyncio
async def test_emcr_tool() -> None:
    r = await imss_consultar_emcr(
        EmcrInput(registro_patronal="ABC1234567X", mes=3, ejercicio=2026)
    )
    assert r["mes"] == 3


@pytest.mark.asyncio
async def test_sbc_tool() -> None:
    r = await imss_consultar_sbc(
        SbcInput(registro_patronal="ABC1234567X", nss="12345678901")
    )
    assert "sbc_diario" in r


@pytest.mark.asyncio
async def test_padron_tool() -> None:
    r = await imss_consultar_padron_trabajadores(RegistroInput(registro_patronal="ABC1234567X"))
    assert "trabajadores" in r


@pytest.mark.asyncio
async def test_catalogos() -> None:
    r = await imss_listar_catalogos()
    assert "tipos_movimiento_afiliatorio" in r
    assert "08" in r["tipos_movimiento_afiliatorio"]
