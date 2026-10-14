"""SAF CDMX con solver de captcha opt-in (2captcha simulado con respx)."""
import json
import os
from pathlib import Path
from urllib.parse import parse_qs

import httpx
import pytest
import respx

from shared.captcha_solver import API
from shared.errors import UpstreamError
from shared.saf_cdmx import (
    URL_SAF_CDMX_CONSULTA,
    URL_SAF_CDMX_OBTEN_ADEUDOS,
    adeudos_o_handoff,
    consultar_adeudos,
)

FORM = (Path(__file__).parent / "fixtures" / "saf_cdmx_consultaciudadana.html").read_text()
URL_IMG = "https://data.finanzas.cdmx.gob.mx/captcha/flat?FIXTURE"
OK = {
    "status": "valido", "tenencia_code": "sin_adeudos", "fotocivicas_verifica": True, "sin_derecho": False,
    "html": "<div>Tenencia sin adeudos</div><script>$total_infracciones = '0';</script>",
}
CAPTCHA_MAL = {"message": "x", "errors": {"captcha_code": ["El captcha es incorrecto."]}}


@pytest.fixture(autouse=True)
def env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    monkeypatch.setenv("PLUGINS_MX_CAPTCHA_SOLVER", "2captcha")
    monkeypatch.setenv("TWOCAPTCHA_API_KEY", "k")
    monkeypatch.setattr("shared.captcha_solver.time.sleep", lambda s: None)


def _portal(post_side_effect):
    respx.get(URL_SAF_CDMX_CONSULTA).respond(200, text=FORM)
    respx.get(URL_IMG).respond(200, content=b"\x89PNG", headers={"content-type": "image/png"})
    crear = respx.post(f"{API}/createTask").respond(200, json={"errorId": 0, "taskId": 1})
    respx.post(f"{API}/getTaskResult").respond(
        200, json={"errorId": 0, "status": "ready", "solution": {"text": "aB3dE"}})
    post = respx.post(URL_SAF_CDMX_OBTEN_ADEUDOS).mock(side_effect=post_side_effect)
    return crear, post


@respx.mock
def test_exito():
    crear, post = _portal([httpx.Response(200, json=OK)])
    r = adeudos_o_handoff("abc-123-d", seccion="Tenencia")
    assert r["consultado"] is True and r["requiere_humano"] is False and r["simulated"] is False
    assert r["puede_verificar"] is True and r["seccion"] == "Tenencia"
    assert r["resumen"] == {"total_infracciones": "0"} and "sin adeudos" in r["detalle_texto"]
    req = post.calls.last.request
    assert req.headers["X-CSRF-TOKEN"] == "TOKENFIXTURE"
    assert parse_qs(req.content.decode()) == {"placa": ["ABC123D"], "captcha_code": ["aB3dE"]}
    assert json.loads(crear.calls.last.request.content)["task"]["type"] == "ImageToTextTask"


@respx.mock
def test_captcha_incorrecto_reintenta():
    crear, post = _portal([httpx.Response(422, json=CAPTCHA_MAL), httpx.Response(200, json=OK)])
    assert consultar_adeudos("ABC123D")["consultado"] is True
    assert post.call_count == 2 and crear.call_count == 2


@respx.mock
def test_captcha_incorrecto_tres_veces_falla():
    _, post = _portal([httpx.Response(422, json=CAPTCHA_MAL)] * 3)
    with pytest.raises(UpstreamError, match="3 veces"):
        consultar_adeudos("ABC123D")
    assert post.call_count == 3


@respx.mock
def test_solver_apagado_es_handoff(monkeypatch):
    monkeypatch.delenv("PLUGINS_MX_CAPTCHA_SOLVER")
    respx.get(URL_SAF_CDMX_CONSULTA).respond(200, text=FORM)
    crear = respx.post(f"{API}/createTask")
    r = adeudos_o_handoff("ABC-123-D", seccion="Tenencia")
    assert r["requiere_humano"] is True and r["captcha_tipo"] == "imagen" and r["placa"] == "ABC123D"
    assert not crear.called


def _cdmx():
    from mp_cdmx_municipal.client import CdmxMunicipalClient
    return CdmxMunicipalClient().consultar_multas("ABC123D")


def _verificacion():
    from mp_verificacion_vehicular_mx.client import VerificacionVehicularClient
    return VerificacionVehicularClient().consultar_estatus("ABC123D", "cdmx")


def _multas():
    from mp_multas_mx.client import MultasMxClient
    return MultasMxClient().consultar_multas("cdmx", "ABC123D")


def _multas_vehiculares():
    from mp_multas_vehiculares_mx.client import MultasVehicularesMxClient
    return MultasVehicularesMxClient().consultar_por_placa("cdmx", "ABC123D")


@pytest.mark.parametrize("llamada", [_cdmx, _verificacion, _multas, _multas_vehiculares])
def test_usuarios_de_saf_usan_el_solver(monkeypatch, tmp_path, llamada):
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path))
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.setattr("shared.saf_cdmx.consultar_adeudos", lambda placa: {"consultado": True, "placa": placa})
    r = llamada()
    assert r["consultado"] is True and r["placa"] == "ABC123D"


@pytest.mark.live
@pytest.mark.skipif(not (os.environ.get("TWOCAPTCHA_API_KEY") and os.environ.get("SAF_CDMX_PLACA_LIVE")),
                    reason="requiere TWOCAPTCHA_API_KEY y SAF_CDMX_PLACA_LIVE")
def test_live_saf_con_solver():
    r = consultar_adeudos(os.environ["SAF_CDMX_PLACA_LIVE"])
    assert r["consultado"] is True and r["tenencia_code"]
