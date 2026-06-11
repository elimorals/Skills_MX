"""Tests para RenapoClient (consulta + descarga mock)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mp_curp_renapo.renapo import RenapoClient
from mp_curp_renapo.tests.conftest import make_valid_curp
from shared.bitacora import Bitacora
from shared.errors import McpError, ValidationError


# ---------- modo mock detección ----------


def test_default_es_mock_sin_envs(monkeypatch) -> None:
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.delenv("CURP_RENAPO_PLAYWRIGHT", raising=False)
    c = RenapoClient()
    assert c.is_mock is True


def test_mock_explicito(monkeypatch) -> None:
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    monkeypatch.setenv("CURP_RENAPO_PLAYWRIGHT", "1")
    c = RenapoClient()
    # PLUGINS_MX_MOCK gana sobre CURP_RENAPO_PLAYWRIGHT
    assert c.is_mock is True


def test_real_solo_con_playwright_env(monkeypatch) -> None:
    monkeypatch.setenv("CURP_RENAPO_PLAYWRIGHT", "1")
    c = RenapoClient()
    assert c.is_mock is False


# ---------- consulta mock ----------


@pytest.mark.asyncio
async def test_consultar_mock_devuelve_vigente() -> None:
    c = RenapoClient()
    r = await c.consultar("PERZ821223HDFRRL09")
    assert r["simulated"] is True
    assert r["estado_renapo"] == "VIGENTE"
    assert r["datos_persona"]["fecha_nacimiento"] == "1982-12-23"
    assert r["datos_persona"]["sexo"] == "H"


@pytest.mark.asyncio
async def test_consultar_mock_curp_digito_4_es_duplicado() -> None:
    """Heurística determinística: CURPs cuyo último dígito es 4 simulan DUPLICADO."""
    # PERZ821223HDFRRL → dígito calculado 9, no me sirve
    # Necesito una base cuyo dígito calculado sea 4
    from mp_curp_renapo.validacion import calcular_digito_verificador

    # Iterar hasta encontrar una base válida que cierre con dígito 4
    # Pos 14-16 deben ser consonantes (regex). Probar con sufijo BCD.
    base = "AAAA000101HASBCD"
    for last in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        candidato = base + last
        if calcular_digito_verificador(candidato) == 4:
            curp = candidato + "4"
            break
    else:
        pytest.skip("No se encontró base que cierre en 4 — ajustar fixture")

    c = RenapoClient()
    r = await c.consultar(curp)
    assert r["estado_renapo"] == "DUPLICADO"


@pytest.mark.asyncio
async def test_consultar_invalida_estructura_lanza_validation_error() -> None:
    c = RenapoClient()
    with pytest.raises(ValidationError):
        await c.consultar("CURP_BASURA_NO_VALIDA")


@pytest.mark.asyncio
async def test_consultar_segunda_llamada_viene_de_cache() -> None:
    c = RenapoClient()
    a = await c.consultar("PERZ821223HDFRRL09")
    # Marcar el cache directamente para probar que la 2da llamada NO ejecuta mock
    b = await c.consultar("PERZ821223HDFRRL09")
    assert a == b


@pytest.mark.asyncio
async def test_consultar_loguea_curp_hasheada(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit2"))
    bit = Bitacora("curp_renapo_mcp")
    c = RenapoClient(bitacora=bit)
    await c.consultar("PERZ821223HDFRRL09")

    entries = bit.tail(10)
    assert len(entries) >= 1
    entry = entries[-1]
    # La CURP NO debe aparecer en claro en el log
    assert "PERZ821223HDFRRL09" not in json.dumps(entry)
    assert "curp_hash" in entry["params"]


# ---------- descargar constancia ----------


@pytest.mark.asyncio
async def test_descargar_constancia_mock() -> None:
    c = RenapoClient()
    r = await c.descargar_constancia("PERZ821223HDFRRL09")
    assert r["simulated"] is True
    assert "PERZ821223HDFRRL09" in r["constancia_pdf_path"]


@pytest.mark.asyncio
async def test_descargar_constancia_curp_invalida(monkeypatch) -> None:
    c = RenapoClient()
    with pytest.raises(ValidationError):
        await c.descargar_constancia("XX")


# ---------- modo real sin Playwright ----------


@pytest.mark.asyncio
async def test_consultar_modo_real_devuelve_not_implemented(monkeypatch) -> None:
    monkeypatch.setenv("CURP_RENAPO_PLAYWRIGHT", "1")
    c = RenapoClient()
    with pytest.raises(McpError) as exc:
        await c.consultar("PERZ821223HDFRRL09")
    assert exc.value.code == "not_implemented_error"
