"""Tests para BanxicoCepClient (modo mock + validaciones)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from mp_banxico_cep.client import BanxicoCepClient
from shared.bitacora import Bitacora
from shared.errors import McpError, ValidationError


# ---------- modo mock detección ----------


def test_default_es_mock(monkeypatch) -> None:
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.delenv("BANXICO_CEP_PLAYWRIGHT", raising=False)
    c = BanxicoCepClient()
    assert c.is_mock is True


def test_plugins_mx_mock_gana(monkeypatch) -> None:
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    monkeypatch.setenv("BANXICO_CEP_PLAYWRIGHT", "1")
    c = BanxicoCepClient()
    assert c.is_mock is True


def test_modo_real_con_playwright_env(monkeypatch) -> None:
    monkeypatch.setenv("BANXICO_CEP_PLAYWRIGHT", "1")
    c = BanxicoCepClient()
    assert c.is_mock is False


# ---------- generar_cep mock ----------


@pytest.mark.asyncio
async def test_generar_cep_mock_shape() -> None:
    c = BanxicoCepClient()
    cep = await c.generar_cep(
        clave_rastreo="MBAN0100123456789012",
        fecha_operacion=date(2026, 3, 15),
        banco_emisor="012",  # BBVA
        banco_receptor="002",  # Banamex
        monto=11600.00,
    )
    assert cep["simulated"] is True
    assert cep["cep_disponible"] is True
    assert cep["banco_emisor"]["nombre"] == "BBVA México"
    assert cep["banco_receptor"]["nombre"] == "Banamex"
    assert cep["monto"] == 11600.00


@pytest.mark.asyncio
async def test_generar_cep_es_determinístico() -> None:
    """Misma clave + datos → mismo CEP en mock."""
    c1 = BanxicoCepClient()
    a = await c1.generar_cep(
        clave_rastreo="MBAN0100ZZZ",
        fecha_operacion=date(2026, 3, 15),
        banco_emisor="012",
        banco_receptor="002",
        monto=100.00,
    )
    # Otro cliente, mismos params
    c2 = BanxicoCepClient()
    b = await c2.generar_cep(
        clave_rastreo="MBAN0100ZZZ",
        fecha_operacion=date(2026, 3, 15),
        banco_emisor="012",
        banco_receptor="002",
        monto=100.00,
    )
    # La hora y referencia derivadas del hash deben ser iguales
    assert a["hora_operacion"] == b["hora_operacion"]
    assert a["referencia"] == b["referencia"]


@pytest.mark.asyncio
async def test_generar_cep_rechaza_banco_desconocido() -> None:
    c = BanxicoCepClient()
    with pytest.raises(ValidationError):
        await c.generar_cep(
            clave_rastreo="MBAN0100123",
            fecha_operacion=date(2026, 3, 15),
            banco_emisor="999",  # no existe
            banco_receptor="002",
            monto=100.00,
        )


@pytest.mark.asyncio
async def test_generar_cep_rechaza_monto_cero() -> None:
    c = BanxicoCepClient()
    with pytest.raises(ValidationError):
        await c.generar_cep(
            clave_rastreo="MBAN0100123",
            fecha_operacion=date(2026, 3, 15),
            banco_emisor="012",
            banco_receptor="002",
            monto=0.0,
        )


@pytest.mark.asyncio
async def test_generar_cep_segunda_llamada_viene_de_cache() -> None:
    c = BanxicoCepClient()
    a = await c.generar_cep(
        clave_rastreo="MBAN0100AAA",
        fecha_operacion=date(2026, 3, 15),
        banco_emisor="012",
        banco_receptor="002",
        monto=100.00,
    )
    b = await c.generar_cep(
        clave_rastreo="MBAN0100AAA",
        fecha_operacion=date(2026, 3, 15),
        banco_emisor="012",
        banco_receptor="002",
        monto=100.00,
    )
    assert a == b


@pytest.mark.asyncio
async def test_generar_cep_loguea_clave_hasheada(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit3"))
    bit = Bitacora("banxico_cep_mcp")
    c = BanxicoCepClient(bitacora=bit)
    await c.generar_cep(
        clave_rastreo="MBAN0100SECRETO123",
        fecha_operacion=date(2026, 3, 15),
        banco_emisor="012",
        banco_receptor="002",
        monto=100.00,
    )
    entries = bit.tail(10)
    entry = entries[-1]
    assert entry["tool"] == "generar_cep"
    # La clave NO debe aparecer en claro
    assert "SECRETO123" not in json.dumps(entry)
    assert "clave_hash" in entry["params"]


# ---------- validar_cep mock ----------


@pytest.mark.asyncio
async def test_validar_cep_mock_devuelve_existe() -> None:
    c = BanxicoCepClient()
    r = await c.validar_cep("MBAN0100123456789012")
    assert r["simulated"] is True
    assert isinstance(r["existe_en_banxico"], bool)


@pytest.mark.asyncio
async def test_validar_cep_rechaza_formato_invalido() -> None:
    c = BanxicoCepClient()
    with pytest.raises(ValidationError):
        await c.validar_cep("XX")  # demasiado corta


# ---------- descargar pdf mock ----------


@pytest.mark.asyncio
async def test_descargar_pdf_mock_devuelve_path() -> None:
    c = BanxicoCepClient()
    r = await c.descargar_pdf_cep(
        clave_rastreo="MBAN0100ABCDEF",
        fecha_operacion=date(2026, 3, 15),
        banco_emisor="012",
        banco_receptor="002",
        monto=100.00,
    )
    assert r["simulated"] is True
    assert "MBAN0100ABCDEF" in r["pdf_path"].upper()


# ---------- consultar_pago_por_clave ----------


@pytest.mark.asyncio
async def test_consultar_pago_por_clave_mock() -> None:
    c = BanxicoCepClient()
    r = await c.consultar_pago_por_clave("MBAN0100SAMPLE123")
    assert r["simulated"] is True
    assert r["emisor_probable"] == "BBVA México"


@pytest.mark.asyncio
async def test_consultar_pago_por_clave_real_devuelve_validation_error(
    monkeypatch,
) -> None:
    """En modo real, sin fecha+bancos+monto Banxico no puede emitir CEP."""
    monkeypatch.setenv("BANXICO_CEP_PLAYWRIGHT", "1")
    c = BanxicoCepClient()
    with pytest.raises(ValidationError):
        await c.consultar_pago_por_clave("MBAN0100SAMPLE")


# ---------- modo real sin Playwright ----------


@pytest.mark.asyncio
async def test_generar_cep_modo_real_devuelve_not_implemented(monkeypatch) -> None:
    monkeypatch.setenv("BANXICO_CEP_PLAYWRIGHT", "1")
    c = BanxicoCepClient()
    with pytest.raises(McpError) as exc:
        await c.generar_cep(
            clave_rastreo="MBAN0100ZZZ",
            fecha_operacion=date(2026, 3, 15),
            banco_emisor="012",
            banco_receptor="002",
            monto=100.00,
        )
    assert exc.value.code == "not_implemented_error"
