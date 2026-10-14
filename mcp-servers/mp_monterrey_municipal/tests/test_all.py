"""Tests mp_monterrey_municipal."""

from __future__ import annotations

import os

import httpx
import pytest
import respx

from mp_monterrey_municipal.client import URL_PREDIAL, MonterreyMunicipalClient, parse_resultado
from mp_monterrey_municipal.server import nl_listar_catalogos
from shared.errors import NotFoundError, UpstreamError, ValidationError

FORM = (
    '<form><input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="abc" />'
    '<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="def" /></form>'
)
NO_EXISTE = ('<span id="ctl00_ContentPlaceHolder1_lbl_warning" class="warning">El expediente '
             'consultado no existe. Favor de internarlo con otro numero de expediente.</span>')
GRID = """
<table id="ctl00_ContentPlaceHolder1_grv_Adeudos">
 <tr><th>Año</th><th>Total</th></tr>
 <tr><td><input id="x_chk_AdeudoId" type="checkbox"/></td><td>2026</td><td>PREDIAL</td>
   <td><span id="x_lbl_Totales_empty">$1,250.50</span><span id="x_lbl_Totales_bnf">$1,000.40</span></td></tr>
 <tr><td>2025</td><td><span id="y_lbl_Totales_empty">$300.00</span></td></tr>
 <tr><td>Total</td><td></td></tr>
</table>"""


def test_parse_grid():
    r = parse_resultado(GRID)
    assert r["adeudo_total_mxn"] == 1550.5
    assert r["conceptos"][0]["total_con_bonificacion_mxn"] == 1000.4
    assert r["estatus"] == "con_adeudo"


def test_parse_no_existe():
    with pytest.raises(NotFoundError):
        parse_resultado(NO_EXISTE)


def test_parse_estructura_desconocida():
    with pytest.raises(UpstreamError):
        parse_resultado("<html>otra cosa</html>")


@respx.mock
def test_predial_flujo_postback():
    respx.get(URL_PREDIAL).mock(return_value=httpx.Response(200, text=FORM))
    post = respx.post(URL_PREDIAL).mock(return_value=httpx.Response(200, text=GRID))
    r = MonterreyMunicipalClient().consultar_predial("Monterrey", "09009009")
    body = post.calls.last.request.content.decode()
    assert "__VIEWSTATE=abc" in body and "txt_buscar=09009009" in body
    assert r["adeudo_total_mxn"] == 1550.5 and r["simulated"] is False


@respx.mock
def test_predial_upstream_500():
    respx.get(URL_PREDIAL).mock(return_value=httpx.Response(500))
    with pytest.raises(UpstreamError):
        MonterreyMunicipalClient().consultar_predial("Monterrey", "09009009")


def test_otro_municipio_error_explicito():
    with pytest.raises(UpstreamError):
        MonterreyMunicipalClient().consultar_predial("Guadalupe", "09009009")


def test_municipio_invalido():
    with pytest.raises(ValidationError):
        MonterreyMunicipalClient().consultar_predial("Mérida", "123")


def test_mock_solo_con_flag(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    assert MonterreyMunicipalClient().consultar_predial("Monterrey", "1")["simulated"] is True


@pytest.mark.asyncio
async def test_catalogos():
    r = await nl_listar_catalogos()
    assert "Monterrey" in r["predial_real"]


@pytest.mark.live
def test_live_expediente_inexistente():
    with pytest.raises(NotFoundError):
        MonterreyMunicipalClient().consultar_predial("Monterrey", "00000001")


@pytest.mark.live
@pytest.mark.skipif(not os.environ.get("MTY_EXPEDIENTE"), reason="exporta MTY_EXPEDIENTE")
def test_live_expediente_real():
    r = MonterreyMunicipalClient().consultar_predial("Monterrey", os.environ["MTY_EXPEDIENTE"])
    assert r["simulated"] is False and "adeudo_total_mxn" in r
