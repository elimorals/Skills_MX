"""Solver de CAPTCHA opt-in: respx simula 2captcha y los portales."""
import os

import httpx
import pytest
import respx

from mp_guadalajara_municipal import client as c
from shared.captcha_solver import API
from shared.errors import UpstreamError


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.setenv("PLUGINS_MX_CAPTCHA_SOLVER", "2captcha")
    monkeypatch.setenv("TWOCAPTCHA_API_KEY", "k")
    monkeypatch.setattr("shared.captcha_solver.time.sleep", lambda s: None)


def _dos_captcha(*tokens):
    respx.post(f"{API}/createTask").respond(200, json={"errorId": 0, "taskId": 1})
    respx.post(f"{API}/getTaskResult").mock(side_effect=[
        httpx.Response(200, json={"errorId": 0, "status": "ready", "solution": {"gRecaptchaResponse": t}})
        for t in tokens
    ])


@respx.mock
def test_predial_exito():
    _dos_captcha("TOK")
    respx.get(c.URL_PREDIAL + "main.js").respond(200, text="'sitekey': '6LfVIVOxxxxxxxxxxxxxxxxxxxx'")
    verif = respx.post(c.PREDIAL_CAPTCHA_URL).respond(200, json={"success": True})
    api = respx.post(c.PREDIAL_API).respond(200, json={
        "status": True, "tipo": "3", "message": "CUENTA PREDIAL CON ADEUDO, PROCEDE PAGO",
        "data": {"importe": "2100.00", "ClaveCatastral": "D65J1", "Calle": "JUAREZ", "adeudos": [{"AXO": 2026}]},
    })
    r = c.GuadalajaraMunClient().consultar_predial("123456", "1", "u")
    assert r["consultado"] is True and r["procede_pago"] is True and r["importe_mxn"] == "2100.00"
    assert r["captcha"]["sitekey"] == "6LfVIVOxxxxxxxxxxxxxxxxxxxx"
    assert b"response=TOK" in verif.calls.last.request.content
    assert b"tipo=U" in api.calls.last.request.content


@respx.mock
def test_predial_token_rechazado_reintenta_y_falla():
    _dos_captcha("a", "b", "c")
    respx.get(c.URL_PREDIAL + "main.js").respond(200, text="")
    verif = respx.post(c.PREDIAL_CAPTCHA_URL).respond(200, json={"success": False})
    api = respx.post(c.PREDIAL_API)
    with pytest.raises(UpstreamError):
        c.GuadalajaraMunClient().consultar_predial("123456", "1", "U")
    assert verif.call_count == 3 and api.call_count == 0


@respx.mock
def test_predial_reintento_exitoso():
    _dos_captcha("a", "b")
    respx.get(c.URL_PREDIAL + "main.js").respond(200, text="")
    respx.post(c.PREDIAL_CAPTCHA_URL).mock(side_effect=[
        httpx.Response(200, json={"success": False}), httpx.Response(200, json={"success": True})])
    respx.post(c.PREDIAL_API).respond(200, json={"status": True, "tipo": "1", "message": "CUENTA PREDIAL PAGADA", "data": {}})
    r = c.GuadalajaraMunClient().consultar_predial("123456", "2", "R")
    assert r["mensaje"] == "CUENTA PREDIAL PAGADA" and r["procede_pago"] is False


def test_predial_sin_recaudadora_es_handoff():
    assert c.GuadalajaraMunClient().consultar_predial("123456")["requiere_humano"] is True


def test_solver_apagado_es_handoff(monkeypatch):
    monkeypatch.delenv("PLUGINS_MX_CAPTCHA_SOLVER")
    r = c.GuadalajaraMunClient().consultar_predial("123456", "1", "U")
    assert r["requiere_humano"] is True and r["motivo"] == "captcha"
    r = c.GuadalajaraMunClient().consultar_adeudos_vehiculares("JAL1234", "ABCDE12345")
    assert r["requiere_humano"] is True and r["url"] == c.URL_VEHICULAR_JAL


JAL_HTML = ('<button class="g-recaptcha" data-action="submit" '
            'data-sitekey="6LehxCgfAAAAAE_6lvOTiXBtQNZCyc37CLZssnzC"></button><div id="error" class="d-none"></div>')


@respx.mock
def test_jalisco_exito():
    _dos_captcha("TOK")
    respx.get(c.URL_VEHICULAR_JAL).respond(200, text=JAL_HTML)
    post = respx.post(c.URL_VEHICULAR_JAL).respond(200, text=(
        '<div id="error" class="d-none"></div><table><tr><th>Concepto</th><th>Importe</th></tr>'
        "<tr><td>Refrendo 2026</td><td>$ 640.00</td></tr></table>"))
    r = c.GuadalajaraMunClient().consultar_adeudos_vehiculares("jal1234", "abcde12345", "Juan", "m1")
    assert r["consultado"] is True and r["filas"][1] == ["Refrendo 2026", "$ 640.00"]
    assert r["captcha"]["accion"] == "submit"
    cuerpo = post.calls.last.request.content
    assert b"g-recaptcha-response=TOK" in cuerpo and b"numeroSerie=ABCDE12345" in cuerpo


@respx.mock
def test_jalisco_token_rechazado():
    _dos_captcha("a", "b", "c")
    respx.get(c.URL_VEHICULAR_JAL).respond(200, text=JAL_HTML)
    post = respx.post(c.URL_VEHICULAR_JAL).respond(200, text='<div id="error">Error en la validación del captcha</div>')
    with pytest.raises(UpstreamError):
        c.GuadalajaraMunClient().consultar_adeudos_vehiculares("JAL1234", "ABCDE12345")
    assert post.call_count == 3


def test_jalisco_sin_serie_es_handoff():
    assert c.GuadalajaraMunClient().consultar_adeudos_vehiculares("JAL1234")["requiere_humano"] is True


@pytest.mark.live
def test_live_predial_con_solver():
    """Requiere TWOCAPTCHA_API_KEY y GDL_PREDIAL='recaudadora,tipo,cuenta' propios."""
    dato = os.environ.get("GDL_PREDIAL", "")
    if not (os.environ.get("TWOCAPTCHA_API_KEY") and dato.count(",") == 2):
        pytest.skip("requiere TWOCAPTCHA_API_KEY y GDL_PREDIAL")
    rec, tipo, cuenta = dato.split(",")
    r = c.GuadalajaraMunClient().consultar_predial(cuenta, rec, tipo)
    assert r["consultado"] is True and r["status"] is not None


@pytest.mark.live
def test_live_jalisco_con_solver():
    """Requiere TWOCAPTCHA_API_KEY y JAL_VEHICULO='placa,serie,nombre,motor' propios."""
    dato = os.environ.get("JAL_VEHICULO", "")
    if not (os.environ.get("TWOCAPTCHA_API_KEY") and dato.count(",") == 3):
        pytest.skip("requiere TWOCAPTCHA_API_KEY y JAL_VEHICULO")
    r = c.GuadalajaraMunClient().consultar_adeudos_vehiculares(*dato.split(","))
    assert r["consultado"] is True
