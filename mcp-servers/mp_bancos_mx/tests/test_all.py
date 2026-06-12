"""Tests para mp_bancos_mx — client + tools."""

from __future__ import annotations

import pytest

from mp_bancos_mx.catalogos import banco_info, es_movimiento_efectivo_grande
from mp_bancos_mx.client import BancosMxClient
from mp_bancos_mx.server import (
    EstadoCuentaInput,
    MovimientosInput,
    VerificarPagoInput,
    bancos_descargar_estado_cuenta,
    bancos_listar_movimientos,
    bancos_listar_soportados,
    bancos_verificar_pago_por_referencia,
)
from shared.errors import McpError, UpstreamError, ValidationError


# ---------- catálogos ----------


def test_banco_info_existe() -> None:
    info = banco_info("BBVA")
    assert info is not None
    assert info["nombre"] == "BBVA México"


def test_banco_info_no_existe() -> None:
    assert banco_info("zzz_invalido") is None


def test_efectivo_grande() -> None:
    assert es_movimiento_efectivo_grande(20000.0, "deposito_efectivo") is True
    assert es_movimiento_efectivo_grande(10000.0, "deposito_efectivo") is False
    assert es_movimiento_efectivo_grande(50000.0, "transferencia_recibida") is False


# ---------- client mock ----------


@pytest.fixture
def client() -> BancosMxClient:
    return BancosMxClient()


def test_descargar_estado_mock(client: BancosMxClient) -> None:
    r = client.descargar_estado_cuenta("bbva", "012180001234567890", 2026, 3)
    assert r["simulated"] is True
    assert r["banco"] == "bbva"
    assert "saldo_final" in r


def test_listar_movimientos_mock(client: BancosMxClient) -> None:
    r = client.listar_movimientos("bbva", "012180001234567890", dias=30)
    assert r["simulated"] is True
    assert r["total_movimientos"] > 0


def test_verificar_pago_encontrado_mock(client: BancosMxClient) -> None:
    r = client.verificar_pago_por_referencia("bbva", "0021480042", 58000.00)
    assert r["simulated"] is True
    assert r["encontrado"] is True


def test_verificar_pago_no_encontrado_mock(client: BancosMxClient) -> None:
    r = client.verificar_pago_por_referencia("bbva", "9999999999", 100.00)
    assert r["encontrado"] is False


def test_banco_no_soportado(client: BancosMxClient) -> None:
    with pytest.raises(McpError):
        client.descargar_estado_cuenta("banco_falso", "12345", 2026, 3)


def test_dias_invalidos(client: BancosMxClient) -> None:
    with pytest.raises(ValidationError):
        client.listar_movimientos("bbva", "12345", dias=999)


def test_path_real_bloqueado(monkeypatch) -> None:
    """Con credenciales pero sin opt-in real → blocked → UpstreamError."""
    monkeypatch.setenv("BBVA_USUARIO", "demo")
    monkeypatch.setenv("BBVA_PASSWORD", "demo")
    c = BancosMxClient()
    with pytest.raises(UpstreamError):
        c.listar_movimientos("bbva", "12345", dias=30)


# ---------- server tools ----------


@pytest.mark.asyncio
async def test_listar_soportados() -> None:
    r = await bancos_listar_soportados()
    assert r["total"] >= 5
    assert "bbva" in r["bancos"]
    assert r["path_real_implementado_en_algun_banco"] is False
    assert "path_real_info" in r


@pytest.mark.asyncio
async def test_estado_cuenta_tool() -> None:
    r = await bancos_descargar_estado_cuenta(
        EstadoCuentaInput(banco="bbva", cuenta="012180001234567890", ejercicio=2026, mes=3)
    )
    assert r["simulated"] is True


@pytest.mark.asyncio
async def test_movimientos_tool() -> None:
    r = await bancos_listar_movimientos(
        MovimientosInput(banco="santander", cuenta="014320001234567890")
    )
    assert "movimientos" in r


@pytest.mark.asyncio
async def test_verificar_pago_tool() -> None:
    r = await bancos_verificar_pago_por_referencia(
        VerificarPagoInput(banco="bbva", referencia="0021480042", monto=58000.0)
    )
    assert r["encontrado"] is True


@pytest.mark.asyncio
async def test_tool_banco_invalido_devuelve_error() -> None:
    """Pydantic Literal rechaza bancos no soportados — error de validación al parsear."""
    # Esto se valida al construir el input — no llega al tool
    from pydantic import ValidationError as PydValidationError
    with pytest.raises(PydValidationError):
        EstadoCuentaInput(banco="banco_xxx", cuenta="123456", ejercicio=2026, mes=3)
