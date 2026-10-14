"""Tests mp_conagua_repda — unitarios con respx + fixture real, y live opt-in."""
from __future__ import annotations

import sys
from pathlib import Path

import httpx
import pytest
import respx

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))

from mp_conagua_repda.client import (  # noqa: E402
    URL_CONSULTA_REPDA,
    CONAGUARepdaClient,
    parse_resultados,
)
from shared.errors import UpstreamError, ValidationError  # noqa: E402

FIXTURE_CFE = (_HERE / "fixtures" / "repda_cfe.html").read_text(encoding="utf-8")
FORM_GET = (
    '<form><input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="abc" />'
    '<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="F2FC524A" />'
    "</form>"
)


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))


def test_parse_fixture_real():
    r = parse_resultados(FIXTURE_CFE)
    assert r["total_registros"] == 265
    assert len(r["registros"]) == 3
    primero = r["registros"][0]
    assert primero["titular"] == "COMISION FEDERAL DE ELECTRICIDAD E.P.E."
    assert primero["num_titulo"] == "11CHS158257/30EMDA26"
    assert primero["uso"] == "SERVICIOS"
    assert primero["fecha_registro"] == "09/07/2026"
    assert primero["volumen_extraccion_m3_anual"] == 2043.92
    assert r["registros"][1]["titular"] == "COMISIÓN FEDERAL DE ELECTRICIDAD"


def test_parse_sin_conteo_es_upstream_error():
    with pytest.raises(UpstreamError):
        parse_resultados("<html>mantenimiento</html>")


@respx.mock
def test_consultar_titular_real_por_nombre():
    respx.get(URL_CONSULTA_REPDA).mock(return_value=httpx.Response(200, text=FORM_GET))
    post = respx.post(URL_CONSULTA_REPDA).mock(return_value=httpx.Response(200, text=FIXTURE_CFE))
    r = CONAGUARepdaClient().consultar_titular("COMISION FEDERAL DE ELECTRICIDAD")
    assert r["simulated"] is False
    assert r["buscado_por"] == "titular"
    assert r["total_registros"] == 265
    body = post.calls.last.request.content.decode()
    assert "__VIEWSTATE=abc" in body
    assert "txtTitular=COMISION+FEDERAL" in body


@respx.mock
def test_consultar_por_titulo_detecta_formato():
    respx.get(URL_CONSULTA_REPDA).mock(return_value=httpx.Response(200, text=FORM_GET))
    post = respx.post(URL_CONSULTA_REPDA).mock(return_value=httpx.Response(200, text=FIXTURE_CFE))
    r = CONAGUARepdaClient().consultar_titular("11CHS158257/30EMDA26")
    assert r["buscado_por"] == "num_titulo"
    assert "txtTitulo=11CHS158257%2F30EMDA26" in post.calls.last.request.content.decode()


@respx.mock
def test_upstream_500_no_cae_a_mock():
    respx.get(URL_CONSULTA_REPDA).mock(return_value=httpx.Response(503, text="down"))
    with pytest.raises(UpstreamError):
        CONAGUARepdaClient().consultar_titular("COMISION FEDERAL")


def test_rfc_no_soportado():
    with pytest.raises(ValidationError):
        CONAGUARepdaClient().consultar_titular("CFE370814QI0")


def test_mock_solo_con_flag(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    r = CONAGUARepdaClient().consultar_titular("EMPRESA DEMO")
    assert r["simulated"] is True


def test_calendario_trimestral_es_handoff():
    r = CONAGUARepdaClient().estado_reporte_semestral("11CHS158257/30EMDA26", "T2")
    assert r["presentado"] is None
    assert r["requiere_humano"] is True
    assert "julio" in r["fecha_limite"]
    with pytest.raises(ValidationError):
        CONAGUARepdaClient().estado_reporte_semestral("11CHS158257/30EMDA26", "1er_semestre")


def test_lfd_cuotas_rmf_2026():
    c = CONAGUARepdaClient()
    r = c.calcular_pago_lfd("874717", 100_000, 1, "subterranea")
    assert r["cuota_m3_mxn"] == 31.8622
    assert r["derecho_mxn"] == 3_186_220.0
    assert c.calcular_pago_lfd("874717", 1000, 4, "superficial")["cuota_m3_mxn"] == 2.7295
    with pytest.raises(ValidationError):
        c.calcular_pago_lfd("874717", 1000, 9)


def test_medidor_siempre_obligatorio():
    c = CONAGUARepdaClient()
    assert c.requiere_medidor(10)["requiere_medidor_obligatorio"] is True
    assert c.requiere_medidor(10, "agricola")["puede_usar_metodo_indirecto"] is True


def test_listar_tipos_uso():
    r = CONAGUARepdaClient().listar_tipos_uso()
    assert "industrial" in r["tipos_uso"]
    assert len(r["tipos_uso"]) == 17


@pytest.mark.live
def test_live_consulta_titular():
    r = CONAGUARepdaClient().consultar_titular("COMISION FEDERAL DE ELECTRICIDAD")
    assert r["simulated"] is False
    assert r["total_registros"] > 0
    assert r["registros"][0]["num_titulo"]
