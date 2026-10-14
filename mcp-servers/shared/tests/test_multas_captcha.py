"""Solver opt-in en multas EdoMex (Turnstile) y San Pedro (reCAPTCHA v2), con respx."""
import json
import os

import httpx
import pytest
import respx

from mp_multas_mx.client import MultasMxClient
from mp_multas_vehiculares_mx.client import MultasVehicularesMxClient
from shared import portal_handoff as ph
from shared.captcha_solver import API
from shared.errors import UpstreamError
from shared.multas_captcha import EDOMEX_SITEKEY, SANPEDRO_SITEKEY

_LLAVE = os.environ.get("TWOCAPTCHA_API_KEY", "")  # se lee antes de que el fixture limpie el env
SP_POST = "https://aplicativos.sanpedro.gob.mx/esanpedro/multas/e_cuenta_sp.asp"
EDOMEX_FORM = (
    f'<form method="post"><select name="doctype"></select><input name="Doc">'
    f'<div class="cf-turnstile" data-sitekey="{EDOMEX_SITEKEY}"></div>'
    '<input name="__RequestVerificationToken" type="hidden" value="CSRF1" /></form>'
    '<script src="https://challenges.cloudflare.com/turnstile/v0/api.js"></script>'
)
EDOMEX_OK = (
    "<table><tr><th>Folio</th><th>Fecha</th><th>Motivo</th><th>Importe Total</th></tr>"
    "<tr><td>F123</td><td>2026-01-02</td><td>Velocidad</td><td>$1,234.50</td></tr></table>"
)
SP_FORM = (
    f'<form action="e_cuenta_sp.asp"><input name="placa"><input type="hidden" name="token" value="{{ABC}}">'
    f'<div class="g-recaptcha" data-sitekey="{SANPEDRO_SITEKEY}"></div></form>'
)
SP_OK = (
    "<table><tr><td><table>"
    "<tr><td>Mun.</td><td>Boleta</td><td>Fecha</td><td>Infracci&oacute;n</td><td>Crucero</td><td>Valor</td>"
    "<td>Bonif. Desc.</td><td>Total</td><td>Fecha Pago</td><td>Recibo</td><td>Pagado</td><td>Saldo</td></tr>"
    "<tr><td>SPGG</td><td>111</td><td>20260101</td><td>VEL</td><td>X</td><td> 900.00 </td><td> 0.00 </td>"
    "<td> 900.00 </td><td></td><td></td><td> 0.00 </td><td> 900.00 </td></tr>"
    "<tr><td>SPGG</td><td>222</td><td>20250101</td><td>EST</td><td>Y</td><td> 500.00 </td><td> 0.00 </td>"
    "<td> 500.00 </td><td>20250201</td><td>R1</td><td> 500.00 </td><td> 0.00 </td></tr>"
    "<tr><td colspan='5'>Total</td><td>1,400.00</td><td>0.00</td><td>1,400.00</td><td></td><td></td>"
    "<td>500.00</td><td>900.00</td></tr></table></td></tr></table>"
)


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "c"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "a"))
    for v in ("PLUGINS_MX_MOCK", "PLUGINS_MX_CAPTCHA_SOLVER", "TWOCAPTCHA_API_KEY"):
        monkeypatch.delenv(v, raising=False)
    monkeypatch.setattr("shared.captcha_solver.time.sleep", lambda s: None)


@pytest.fixture
def activo(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_CAPTCHA_SOLVER", "2captcha")
    monkeypatch.setenv("TWOCAPTCHA_API_KEY", "k")


def _2captcha(solucion):
    crear = respx.post(f"{API}/createTask").respond(200, json={"errorId": 0, "taskId": 1})
    respx.post(f"{API}/getTaskResult").respond(200, json={"errorId": 0, "status": "ready", "solution": solucion})
    return crear


@respx.mock
def test_edomex_turnstile_ok(activo):
    crear = _2captcha({"token": "TT"})
    respx.get(ph.EDOMEX_INFRACCIONES.url).respond(200, text=EDOMEX_FORM)
    post = respx.post(ph.EDOMEX_INFRACCIONES.url).respond(200, text=EDOMEX_OK)
    r = MultasMxClient().consultar_multas("edomex", "ABC-12-34")
    assert r["consultado"] and not r["requiere_humano"] and r["simulated"] is False
    assert r["multas"][0]["monto_mxn"] == 1234.5 and r["adeudo_total_mxn"] == 1234.5
    task = json.loads(crear.calls.last.request.content)["task"]
    assert task["type"] == "TurnstileTaskProxyless" and task["websiteKey"] == EDOMEX_SITEKEY
    body = post.calls.last.request.content.decode()
    assert "cf-turnstile-response=TT" in body and "Doc=ABC1234" in body
    assert "__RequestVerificationToken=CSRF1" in body and "doctype=1" in body


@respx.mock
def test_edomex_rechazo_reintenta_y_falla(activo):
    _2captcha({"token": "TT"})
    respx.get(ph.EDOMEX_INFRACCIONES.url).respond(200, text=EDOMEX_FORM)
    post = respx.post(ph.EDOMEX_INFRACCIONES.url).respond(200, text=EDOMEX_FORM)
    with pytest.raises(UpstreamError):
        MultasMxClient().consultar_multas("edomex", "ABC1234")
    assert post.call_count == 3


@respx.mock
def test_edomex_formato_desconocido_no_inventa(activo):
    _2captcha({"token": "TT"})
    respx.get(ph.EDOMEX_INFRACCIONES.url).respond(200, text=EDOMEX_FORM)
    respx.post(ph.EDOMEX_INFRACCIONES.url).respond(200, text="<p>algo nuevo</p>")
    with pytest.raises(UpstreamError):
        MultasMxClient().consultar_multas("edomex", "ABC1234")


@respx.mock
def test_sanpedro_recaptcha_ok_con_reintento(activo):
    crear = _2captcha({"gRecaptchaResponse": "GR"})
    respx.get(ph.SAN_PEDRO_MULTAS.url).respond(200, text=SP_FORM)
    post = respx.post(SP_POST).mock(side_effect=[
        httpx.Response(200, text="<script>alert('verifica que no eres un robot')</script>"),
        httpx.Response(200, text=SP_OK),
    ])
    c = MultasVehicularesMxClient()
    r = c.consultar_por_placa("nl_sanpedro", "ABC1234")
    assert post.call_count == 2 and crear.call_count == 2
    assert r["multas_total"] == 1 and r["multas"][0]["folio"] == "111"
    assert r["adeudo_total_mxn"] == 900.0 and len(r["historial"]) == 2
    body = post.calls.last.request.content.decode()
    assert "g-recaptcha-response=GR" in body and "placa=ABC1234" in body and "token=%7BABC%7D" in body
    task = json.loads(crear.calls.last.request.content)["task"]
    assert task["type"] == "RecaptchaV2TaskProxyless" and task["websiteKey"] == SANPEDRO_SITEKEY


@respx.mock
def test_calcular_total_real_sin_monto_no_suma_cero(activo):
    _2captcha({"token": "TT"})
    respx.get(ph.EDOMEX_INFRACCIONES.url).respond(200, text=EDOMEX_FORM)
    respx.post(ph.EDOMEX_INFRACCIONES.url).respond(
        200, text="<table><tr><th>Folio</th><th>Motivo</th></tr><tr><td>F1</td><td>X</td></tr></table>")
    r = MultasVehicularesMxClient().calcular_total("edomex", "ABC1234")
    assert r["monto_bruto_mxn"] is None


@respx.mock
@pytest.mark.parametrize("estado,portal", [("edomex", ph.EDOMEX_INFRACCIONES), ("nl_sanpedro", ph.SAN_PEDRO_MULTAS)])
def test_solver_apagado_es_handoff(estado, portal):
    respx.get(portal.url).respond(200, text=EDOMEX_FORM if estado == "edomex" else SP_FORM)
    r = MultasMxClient().consultar_multas(estado, "ABC1234")
    assert r["requiere_humano"] is True and r["consultado"] is False
    assert not any(c.request.url.host == "api.2captcha.com" for c in respx.calls)


@pytest.mark.live
@pytest.mark.parametrize("estado,var", [("edomex", "MULTAS_EDOMEX_PLACA"), ("nl_sanpedro", "MULTAS_SANPEDRO_PLACA")])
def test_live_solver(monkeypatch, estado, var):
    if not (_LLAVE and os.environ.get(var)):
        pytest.skip(f"requiere TWOCAPTCHA_API_KEY y {var}")
    monkeypatch.setenv("PLUGINS_MX_CAPTCHA_SOLVER", "2captcha")
    monkeypatch.setenv("TWOCAPTCHA_API_KEY", _LLAVE)
    monkeypatch.setattr("shared.captcha_solver.time.sleep", __import__("time").sleep)
    r = MultasMxClient().consultar_multas(estado, os.environ[var])
    assert r["consultado"] is True and isinstance(r["multas"], list)
