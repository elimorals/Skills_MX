"""Tests mp_edomex_municipal."""

from __future__ import annotations

import os

import pytest
import respx

from mp_edomex_municipal import toluca
from mp_edomex_municipal.client import EdomexMunicipalClient
from mp_edomex_municipal.server import (
    PlacaInput,
    TenenciaInput,
    edomex_consultar_multas,
    edomex_consultar_tenencia,
    edomex_listar_catalogos,
)
from shared.errors import NotFoundError, UpstreamError, ValidationError
from shared.portal_handoff import EDOMEX_INFRACCIONES, EDOMEX_RECAUDACION

FORM = (
    '<form id="form1"><input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="vs" />'
    '<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="ev" />'
    '<input name="txtCuenta" id="txtCuenta"></form>'
)
NO_REGISTRADA = FORM + '<span id="LabelMsg">La Clave Catastral no está registrada</span>'
CON_ADEUDO = FORM + (
    '<span id="LabelMsg"></span><table id="grdliquidacion">'
    "<tr><th>Concepto</th><th>Importe</th></tr>"
    "<tr><td>Impuesto predial 2026</td><td>$1,234.50</td></tr>"
    "<tr><td>TOTAL</td><td>$1,234.50</td></tr></table>"
)


@pytest.fixture
def client() -> EdomexMunicipalClient:
    return EdomexMunicipalClient()


@respx.mock
def test_toluca_con_adeudo(client: EdomexMunicipalClient) -> None:
    respx.get(toluca.URL).respond(200, text=FORM)
    post = respx.post(toluca.URL).respond(200, text=CON_ADEUDO)
    r = client.consultar_predial("Toluca de Lerdo", "1010101010000000")
    assert r["simulated"] is False
    assert r["adeudo_total_mxn"] == 1234.50
    assert r["estatus"] == "con_adeudo"
    body = post.calls.last.request.content.decode()
    assert "txtCuenta=1010101010000000" in body and "__VIEWSTATE=vs" in body


@respx.mock
def test_toluca_no_registrada() -> None:
    respx.get(toluca.URL).respond(200, text=FORM)
    respx.post(toluca.URL).respond(200, text=NO_REGISTRADA)
    with pytest.raises(NotFoundError):
        toluca.consultar("0000000000000000")


@respx.mock
def test_toluca_respuesta_desconocida_es_upstream() -> None:
    respx.get(toluca.URL).respond(200, text=FORM)
    respx.post(toluca.URL).respond(200, text=FORM)
    with pytest.raises(UpstreamError):
        toluca.consultar("1010101010000000")


def test_toluca_clave_invalida() -> None:
    with pytest.raises(ValidationError):
        toluca.consultar("123")


@respx.mock
def test_tenencia_handoff(client: EdomexMunicipalClient) -> None:
    respx.get(EDOMEX_RECAUDACION.url).respond(200, text="<title>Portal de Servicios al Contribuyente</title>")
    r = client.consultar_tenencia("ABC-123-D", 2026)
    assert r["status"] == "requiere_humano"
    assert r["reglas_2026"]["subsidio_100_pct_si_valor_factura_hasta_mxn"] == 638_000


@respx.mock
def test_multas_turnstile(client: EdomexMunicipalClient) -> None:
    respx.get(EDOMEX_INFRACCIONES.url).respond(
        200, text='<script src="https://challenges.cloudflare.com/turnstile/v0/api.js"></script>')
    r = client.consultar_multas("ABC-123-D")
    assert r["captcha_tipo"] == "turnstile"


def test_mock_solo_con_flag(client: EdomexMunicipalClient, monkeypatch) -> None:
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    assert client.consultar_predial("Naucalpan", "123456")["simulated"] is True


def test_municipios_lista(client: EdomexMunicipalClient) -> None:
    assert "Toluca" in client.municipios_soportados()


@respx.mock
@pytest.mark.asyncio
async def test_tools() -> None:
    respx.get(EDOMEX_RECAUDACION.url).respond(500)
    respx.get(EDOMEX_INFRACCIONES.url).respond(200, text="turnstile challenges.cloudflare.com/turnstile")
    err = await edomex_consultar_tenencia(TenenciaInput(placa="ABC-123-D", ejercicio=2026))
    assert err["code"] == "upstream_error"
    assert (await edomex_consultar_multas(PlacaInput(placa="ABC-123-D")))["status"] == "requiere_humano"
    assert "Toluca" in (await edomex_listar_catalogos())["municipios_predial_digital"]


@pytest.mark.live
def test_live_toluca_clave_inexistente() -> None:
    """Clave ficticia: valida el endpoint sin tocar datos de un particular."""
    with pytest.raises(NotFoundError):
        toluca.consultar("0000000000000000")


@pytest.mark.live
@pytest.mark.skipif(not os.getenv("TOLUCA_CLAVE_CATASTRAL"), reason="exporta TOLUCA_CLAVE_CATASTRAL (16 dígitos, tuya)")
def test_live_toluca_clave_real() -> None:
    r = toluca.consultar(os.environ["TOLUCA_CLAVE_CATASTRAL"])
    assert r["conceptos"]
