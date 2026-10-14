import os
from pathlib import Path
from urllib.parse import parse_qs

import httpx
import pytest
import respx

from mp_puebla_municipal.client import URL_PREDIAL, PueblaMunClient, consultar_predial_portal
from shared.captcha_solver import API
from shared.errors import UpstreamError

FORM = (Path(__file__).parent / "fixtures" / "iniciopredial.html").read_text()
URL_IMG = "https://srvappayt.pueblacapital.gob.mx:7016/pabel/simpleImg.jpg"
# Respuestas POST sintéticas: la real no se ha visto (falta llave de 2captcha).
RESULTADO = "<html><table><tr><th>Concepto</th><th>Importe</th></tr><tr><td>Predial 2026</td><td>$1,234.50</td></tr><tr><td>Total a pagar</td><td>$1,234.50</td></tr></table></html>"
CAPTCHA_MAL = FORM.replace("<form", '<div class="alert alert-danger">El código de la imagen es incorrecto</div><form')


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.delenv("PLUGINS_MX_CAPTCHA_SOLVER", raising=False)


def test_predial_handoff_captcha():
    r = PueblaMunClient().consultar_predial("1234567")
    assert r["requiere_humano"] is True and r["motivo"] == "captcha"
    assert r["url"] == URL_PREDIAL and r["simulated"] is False


@pytest.fixture
def solver(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_CAPTCHA_SOLVER", "2captcha")
    monkeypatch.setenv("TWOCAPTCHA_API_KEY", "k")
    monkeypatch.setattr("shared.captcha_solver.time.sleep", lambda s: None)


def _portal(respuestas):
    respx.get(URL_PREDIAL).respond(200, text=FORM)
    respx.get(URL_IMG).respond(200, content=b"\x89PNG", headers={"content-type": "image/png"})
    crear = respx.post(f"{API}/createTask").respond(200, json={"errorId": 0, "taskId": 1})
    respx.post(f"{API}/getTaskResult").respond(200, json={"errorId": 0, "status": "ready", "solution": {"text": "x7K2p"}})
    post = respx.post(URL_PREDIAL).mock(side_effect=[httpx.Response(200, text=t) for t in respuestas])
    return crear, post


@respx.mock
def test_predial_con_solver_exito(solver):
    _, post = _portal([RESULTADO])
    r = PueblaMunClient().consultar_predial("1234567", delegacion="05")
    assert r["consultado"] is True and r["requiere_humano"] is False and r["total_mxn"] == 1234.5
    assert ["Predial 2026", "$1,234.50"] in r["tablas"]
    assert parse_qs(post.calls.last.request.content.decode()) == {
        "tipo": ["PU"], "cuenta": ["1234567"], "delegacion": ["05"], "answer": ["x7K2p"], "_csrf": ["CSRFFIXTURE"]}


@respx.mock
def test_predial_captcha_incorrecto_reintenta(solver):
    crear, post = _portal([CAPTCHA_MAL, RESULTADO])
    assert PueblaMunClient().consultar_predial("1" * 24)["consultado"] is True
    assert post.call_count == 2 and crear.call_count == 2
    assert parse_qs(post.calls.last.request.content.decode())["lc"] == ["1" * 24]


@respx.mock
def test_predial_captcha_incorrecto_tres_veces(solver):
    _portal([CAPTCHA_MAL] * 3)
    with pytest.raises(UpstreamError, match="3 veces"):
        PueblaMunClient().consultar_predial("1234567", delegacion="05")


def test_predial_solver_apagado_es_handoff():
    r = PueblaMunClient().consultar_predial("1234567", delegacion="05")
    assert r["requiere_humano"] is True and r["motivo"] == "captcha"


@pytest.mark.live
@pytest.mark.skipif(
    not (os.environ.get("TWOCAPTCHA_API_KEY") and os.environ.get("PUEBLA_PREDIAL_CUENTA_LIVE")),
    reason="requiere TWOCAPTCHA_API_KEY y PUEBLA_PREDIAL_CUENTA_LIVE (+ PUEBLA_PREDIAL_DELEGACION_LIVE o una LC de 24 dígitos)")
def test_live_predial_con_solver():
    cuenta = os.environ["PUEBLA_PREDIAL_CUENTA_LIVE"]
    if len(cuenta) == 24:
        r = consultar_predial_portal(lc=cuenta)
    else:
        r = consultar_predial_portal(cuenta=cuenta, delegacion=os.environ["PUEBLA_PREDIAL_DELEGACION_LIVE"])
    assert r["consultado"] is True


def test_mock_solo_con_flag(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    assert PueblaMunClient().consultar_predial("1")["simulated"] is True


@pytest.mark.live
def test_live_predial_sigue_con_captcha():
    html = httpx.get(URL_PREDIAL, timeout=30).text
    assert 'name="answer"' in html and "captcha" in html.lower()
