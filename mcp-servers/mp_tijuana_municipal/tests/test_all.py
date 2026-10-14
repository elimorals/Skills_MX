import os

import httpx
import pytest
import respx

from mp_tijuana_municipal.client import URL_SEGURO, TijuanaMunClient
from shared.errors import UpstreamError, ValidationError

FORM = '<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="vs" />'


def _resp(msg: str) -> httpx.Response:
    return httpx.Response(200, text=f'<span id="ContentPlaceHolder1_lbMsjSeguro" class="alert">{msg}</span>')


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)


def test_predial_es_handoff_login():
    r = TijuanaMunClient().consultar_predial("AB123456")
    assert r["requiere_humano"] is True and r["motivo"] == "login"
    assert r["simulated"] is False and r["pasos"]


@respx.mock
def test_vivienda_no_asegurada():
    respx.get(URL_SEGURO).mock(return_value=httpx.Response(200, text=FORM))
    post = respx.post(URL_SEGURO).mock(return_value=_resp("Clave catastral no asegurada"))
    r = TijuanaMunClient().consultar_vivienda_asegurada("aa000001")
    assert r["asegurada"] is False
    assert "__VIEWSTATE=vs" in post.calls.last.request.content.decode()


@respx.mock
def test_vivienda_asegurada():
    respx.get(URL_SEGURO).mock(return_value=httpx.Response(200, text=FORM))
    respx.post(URL_SEGURO).mock(return_value=_resp("Clave catastral asegurada"))
    assert TijuanaMunClient().consultar_vivienda_asegurada("AA000001")["asegurada"] is True


@respx.mock
def test_vivienda_portal_cambio():
    respx.get(URL_SEGURO).mock(return_value=httpx.Response(200, text=FORM))
    respx.post(URL_SEGURO).mock(return_value=httpx.Response(200, text="<html></html>"))
    with pytest.raises(UpstreamError):
        TijuanaMunClient().consultar_vivienda_asegurada("AA000001")


def test_vivienda_validacion():
    with pytest.raises(ValidationError):
        TijuanaMunClient().consultar_vivienda_asegurada("x")


def test_mock_solo_con_flag(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    assert TijuanaMunClient().consultar_predial("AB1")["simulated"] is True


@pytest.mark.live
def test_live_vivienda_clave_ficticia():
    r = TijuanaMunClient().consultar_vivienda_asegurada(os.environ.get("TIJ_CLAVE_CATASTRAL", "AA000001"))
    assert r["simulated"] is False and r["mensaje_portal"]
