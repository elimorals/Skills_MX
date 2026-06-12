"""Tests mp_buro_credito_personal — incluye validación de autorización legal."""

from __future__ import annotations

import pytest

from mp_buro_credito_personal.client import BuroAutorizacionError, BuroCreditoClient
from mp_buro_credito_personal.server import (
    ConsultaInput,
    buro_consultar_score,
    buro_descargar_reporte_completo,
    buro_listar_catalogos,
    buro_monitorear_alertas,
)
from mp_buro_credito_personal.tests.conftest import SHORT_TOKEN, VALID_TOKEN
from shared.errors import ValidationError


@pytest.fixture
def client() -> BuroCreditoClient:
    return BuroCreditoClient()


# ---------- compliance: autorización ----------


def test_consultar_score_sin_token_falla(client: BuroCreditoClient) -> None:
    with pytest.raises(BuroAutorizacionError):
        client.consultar_score("MAJG800101XYZ", "")


def test_consultar_score_token_corto_falla(client: BuroCreditoClient) -> None:
    with pytest.raises(BuroAutorizacionError):
        client.consultar_score("MAJG800101XYZ", SHORT_TOKEN)


def test_reporte_sin_token_falla(client: BuroCreditoClient) -> None:
    with pytest.raises(BuroAutorizacionError):
        client.descargar_reporte_completo("MAJG800101XYZ", None)  # type: ignore


def test_alertas_sin_token_falla(client: BuroCreditoClient) -> None:
    with pytest.raises(BuroAutorizacionError):
        client.monitorear_alertas("MAJG800101XYZ", "")


# ---------- con autorización válida ----------


def test_score_con_autorizacion_mock(client: BuroCreditoClient) -> None:
    r = client.consultar_score("MAJG800101XYZ", VALID_TOKEN)
    assert r["simulated"] is True
    assert "score_actual" in r
    # El RFC debe estar hasheado, no en claro
    assert "rfc_hash" in r
    assert "MAJG800101XYZ" not in str(r)


def test_reporte_con_autorizacion_mock(client: BuroCreditoClient) -> None:
    r = client.descargar_reporte_completo("MAJG800101XYZ", VALID_TOKEN)
    assert r["simulated"] is True
    assert len(r["cuentas_activas"]) >= 1


def test_alertas_con_autorizacion_mock(client: BuroCreditoClient) -> None:
    r = client.monitorear_alertas("MAJG800101XYZ", VALID_TOKEN)
    assert r["simulated"] is True
    assert "alertas" in r


# ---------- validación RFC ----------


def test_rfc_corto_falla(client: BuroCreditoClient) -> None:
    with pytest.raises(ValidationError):
        client.consultar_score("ABC123", VALID_TOKEN)


# ---------- server tools ----------


@pytest.mark.asyncio
async def test_score_tool_sin_autorizacion_devuelve_error() -> None:
    # Pydantic ValidationError porque min_length=16
    from pydantic import ValidationError as PydValError
    with pytest.raises(PydValError):
        ConsultaInput(rfc="MAJG800101XYZ", autorizacion_token="short")


@pytest.mark.asyncio
async def test_score_tool_con_autorizacion() -> None:
    r = await buro_consultar_score(
        ConsultaInput(rfc="MAJG800101XYZ", autorizacion_token=VALID_TOKEN)
    )
    assert "score_actual" in r


@pytest.mark.asyncio
async def test_reporte_tool() -> None:
    r = await buro_descargar_reporte_completo(
        ConsultaInput(rfc="MAJG800101XYZ", autorizacion_token=VALID_TOKEN)
    )
    assert "cuentas_activas" in r


@pytest.mark.asyncio
async def test_alertas_tool() -> None:
    r = await buro_monitorear_alertas(
        ConsultaInput(rfc="MAJG800101XYZ", autorizacion_token=VALID_TOKEN)
    )
    assert "alertas" in r


@pytest.mark.asyncio
async def test_catalogos_tool() -> None:
    r = await buro_listar_catalogos()
    assert "rangos_score" in r
    assert "marco_legal" in r
    assert "advertencia_critica" in r
    assert "DELITO" in r["advertencia_critica"]


# ---------- bitácora ----------


def test_bitacora_no_loguea_rfc_en_claro(client: BuroCreditoClient, tmp_path) -> None:
    client.consultar_score("MAJG800101XYZ", VALID_TOKEN)
    candidates = list((tmp_path / "audit").rglob("*.jsonl"))
    assert candidates
    content = candidates[0].read_text()
    assert "MAJG800101XYZ" not in content
    assert "consultar_score" in content


def test_bitacora_no_loguea_token_en_claro(client: BuroCreditoClient, tmp_path) -> None:
    client.consultar_score("MAJG800101XYZ", VALID_TOKEN)
    candidates = list((tmp_path / "audit").rglob("*.jsonl"))
    content = candidates[0].read_text()
    assert VALID_TOKEN not in content
