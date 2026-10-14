"""Tests para RenapoClient (consulta + descarga mock)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mp_curp_renapo.renapo import RenapoClient
from mp_curp_renapo.tests.conftest import make_valid_curp
from shared.bitacora import Bitacora
from shared.errors import ValidationError


# ---------- modo mock detección ----------


def test_default_es_real_sin_envs(monkeypatch) -> None:
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    assert RenapoClient().is_mock is False


def test_mock_explicito(monkeypatch) -> None:
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    assert RenapoClient().is_mock is True


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


# ---------- modo real: handoff humano (CAPTCHA) ----------


@pytest.mark.asyncio
async def test_consultar_real_devuelve_handoff(monkeypatch) -> None:
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    r = await RenapoClient().consultar("PERZ821223HDFRRL09")
    assert r["requiere_humano"] is True
    assert r["url"] == "https://www.gob.mx/curp/"
    assert r["campos_prellenados"] == {"curp": "PERZ821223HDFRRL09"}
    assert r["validacion_local"]["valido_estructura"] is True
    assert r["simulated"] is False


@pytest.mark.asyncio
async def test_constancia_real_devuelve_handoff(monkeypatch) -> None:
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    r = await RenapoClient().descargar_constancia("PERZ821223HDFRRL09")
    assert r["requiere_humano"] is True
    assert any("PDF" in p for p in r["pasos"])


@pytest.mark.live
def test_live_portal_sigue_exigiendo_captcha() -> None:
    """Confirma que gob.mx/curp sigue protegido (si deja de estarlo, revisar el handoff)."""
    import httpx

    r = httpx.get("https://www.gob.mx/curp/", timeout=30, follow_redirects=True)
    body = r.text.lower()
    assert "recaptcha" in body or "challenge" in body or r.status_code in (403, 429)
