"""Tests mp_cdmx_municipal."""

from __future__ import annotations

import pytest
import respx

from mp_cdmx_municipal.client import CdmxMunicipalClient
from mp_cdmx_municipal.server import (
    FechaInput,
    PlacaInput,
    PredialInput,
    cdmx_consultar_hoy_no_circula,
    cdmx_consultar_multas,
    cdmx_consultar_predial,
    cdmx_listar_catalogos,
)
from shared.errors import UpstreamError, ValidationError
from shared.portal_handoff import OVICA_CDMX_PREDIAL, SAF_CDMX_ADEUDOS

SAF_HTML = '<form id="form_adeudos"><input id="captcha_code" name="captcha_code"></form>'
OVICA_HTML = '<script src="https://cdn.jsdelivr.net/npm/altcha@1.0.0/dist/altcha.min.js"></script>'


@pytest.fixture
def client() -> CdmxMunicipalClient:
    return CdmxMunicipalClient()


@respx.mock
def test_predial_handoff_ovica(client: CdmxMunicipalClient) -> None:
    respx.get(OVICA_CDMX_PREDIAL.url).respond(200, text=OVICA_HTML)
    r = client.consultar_predial("123456789012")
    assert r["simulated"] is False
    assert r["status"] == "requiere_humano"
    assert r["captcha_tipo"] == "altcha"
    assert "123456789012" not in str(r)


@respx.mock
def test_tenencia_handoff_saf(client: CdmxMunicipalClient) -> None:
    respx.get(SAF_CDMX_ADEUDOS.url).respond(200, text=SAF_HTML)
    r = client.consultar_tenencia("ABC-123-D")
    assert r["placa"] == "ABC123D"
    assert r["seccion"] == "Tenencia"
    assert r["url"] == SAF_CDMX_ADEUDOS.url


@respx.mock
def test_saf_caido_no_cae_a_mock(client: CdmxMunicipalClient) -> None:
    respx.get(SAF_CDMX_ADEUDOS.url).respond(502)
    with pytest.raises(UpstreamError):
        client.consultar_multas("ABC-123-D")


def test_mock_solo_con_flag(client: CdmxMunicipalClient, monkeypatch) -> None:
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    r = client.consultar_predial("1234567890")
    assert r["simulated"] is True
    assert "valor_catastral_mxn" in r


def test_predial_invalido(client: CdmxMunicipalClient) -> None:
    with pytest.raises(ValidationError):
        client.consultar_predial("ab")


@pytest.mark.parametrize("fecha,esperado", [
    ("2026-10-12", "5,6"),  # lunes
    ("2026-10-16", "9,0"),  # viernes
])
def test_hnc_entre_semana(client: CdmxMunicipalClient, fecha: str, esperado: str) -> None:
    r = client.consultar_calendario_hoy_no_circula(fecha)
    assert r["simulated"] is False
    assert r["restricciones_del_dia"][0]["ultimo_digito_placa"] == esperado


def test_hnc_sabados(client: CdmxMunicipalClient) -> None:
    primero = client.consultar_calendario_hoy_no_circula("2026-10-03")["restricciones_del_dia"]
    segundo = client.consultar_calendario_hoy_no_circula("2026-10-10")["restricciones_del_dia"]
    quinto = client.consultar_calendario_hoy_no_circula("2026-10-31")["restricciones_del_dia"]
    assert {"ultimo_digito_placa": "1,3,5,7,9", "holograma_aplica": ["1"]} in primero
    assert {"ultimo_digito_placa": "0,2,4,6,8", "holograma_aplica": ["1"]} in segundo
    assert quinto == [{"ultimo_digito_placa": "todos", "holograma_aplica": ["2"]}]


def test_hnc_domingo_sin_restriccion(client: CdmxMunicipalClient) -> None:
    assert client.consultar_calendario_hoy_no_circula("2026-10-18")["restricciones_del_dia"] == []


@respx.mock
@pytest.mark.asyncio
async def test_tools() -> None:
    respx.get(OVICA_CDMX_PREDIAL.url).respond(200, text=OVICA_HTML)
    respx.get(SAF_CDMX_ADEUDOS.url).respond(503)
    assert (await cdmx_consultar_predial(PredialInput(cuenta_predial="123456789012")))["status"] == "requiere_humano"
    err = await cdmx_consultar_multas(PlacaInput(placa="ABC-123-D"))
    assert err["error"] is True and err["code"] == "upstream_error"
    assert (await cdmx_consultar_hoy_no_circula(FechaInput(fecha="2026-10-12")))["restricciones_del_dia"]
    assert "00" in (await cdmx_listar_catalogos())["hologramas"]


@pytest.mark.live
def test_live_saf_handoff(client: CdmxMunicipalClient) -> None:
    r = client.consultar_tenencia("ABC123D")  # placa ficticia: solo se carga la página
    assert r["portal_verificado"]["status_code"] == 200
