"""Tests mp_cre_hidrocarburos — respx + fixture real del padrón de estaciones."""
from __future__ import annotations

import sys
from pathlib import Path

import httpx
import pytest
import respx

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))

from mp_cre_hidrocarburos.client import URL_PLACES, CREClient, parse_places  # noqa: E402
from shared.errors import UpstreamError, ValidationError  # noqa: E402

PLACES = (_HERE / "fixtures" / "places.xml").read_bytes()


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))


def test_parse_fixture_real():
    est = parse_places(PLACES.decode("utf-8"))
    assert len(est) == 6
    assert est[0] == {"place_id": "2039", "nombre": "ESTACION HIPODROMO SA DE CV",
                      "permiso": "PL/658/EXP/ES/2015", "lon": -116.9214, "lat": 32.47641}


@respx.mock
def test_consultar_por_permiso_cne():
    route = respx.get(URL_PLACES).mock(return_value=httpx.Response(200, content=PLACES))
    c = CREClient()
    r = c.consultar_permiso("CNE/PL/2/EXP/ES/2025")
    assert r["simulated"] is False
    assert r["encontrado"] is True
    assert r["estaciones"][0]["nombre"] == "MEGA GASOLINERAS SA DE CV"
    c.consultar_permiso("PL/658/EXP/ES/2015")
    assert route.call_count == 1  # padrón cacheado 24 h


@respx.mock
def test_consultar_por_razon_social_sin_acentos():
    respx.get(URL_PLACES).mock(return_value=httpx.Response(200, content=PLACES))
    r = CREClient().consultar_permiso("estación de servicios atenas")
    assert r["buscado_por"] == "razon_social"
    assert r["total"] == 1


@respx.mock
def test_no_encontrado_no_afirma_invalidez():
    respx.get(URL_PLACES).mock(return_value=httpx.Response(200, content=PLACES))
    r = CREClient().consultar_permiso("G/1234/TRA/DUC/2016")
    assert r["encontrado"] is False
    assert "NO prueba" in r["nota"]
    assert r["handoff_humano"]


@respx.mock
def test_upstream_caido_es_error():
    respx.get(URL_PLACES).mock(return_value=httpx.Response(502))
    with pytest.raises(UpstreamError):
        CREClient().consultar_permiso("PL/658/EXP/ES/2015")


def test_consultar_permiso_corto():
    with pytest.raises(ValidationError):
        CREClient().consultar_permiso("ab")


def test_mock_solo_con_flag(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    assert CREClient().consultar_permiso("PL/658/EXP/ES/2015")["simulated"] is True


def test_calendar_12_periodos_sin_fecha_inventada():
    r = CREClient().calendar_reporte_mensual(2026, 11)
    assert len(r["periodos"]) == 12
    assert r["periodos"][2]["periodo"] == "2027-01"
    assert r["fecha_limite"] is None


def test_anexo30_umbral_litros():
    c = CREClient()
    assert c.evaluar_anexo30(75_714, False)["aplica_anexo30_sat"] is True
    assert c.evaluar_anexo30(75_713, False)["aplica_anexo30_sat"] is False
    assert c.evaluar_anexo30(0, True)["aplica_anexo30_sat"] is True
    assert c.evaluar_anexo30(0, False, gas_natural_gj_anio=5_001)["aplica_anexo30_sat"] is True


def test_reportar_zeros_es_handoff_nunca_envia():
    r = CREClient().reportar_zeros("PL/658/EXP/ES/2015", "2026-09")
    assert r["enviado"] is False
    assert r["handoff_humano"] is True
    assert "folio" not in r
    with pytest.raises(ValidationError):
        CREClient().reportar_zeros("PL/658/EXP/ES/2015", "2026/09")


def test_listar_tipos_permiso():
    assert CREClient().listar_tipos_permiso()["total"] == 6


@pytest.mark.live
def test_live_padron_estaciones():
    r = CREClient().consultar_permiso("PL/658/EXP/ES/2015")
    assert r["simulated"] is False
    assert r["encontrado"] is True
