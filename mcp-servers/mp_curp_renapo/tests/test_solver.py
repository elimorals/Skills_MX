"""RENAPO con solver opt-in (2captcha y portal simulados con respx).

Las respuestas del portal son SINTÉTICAS: no corresponden a ninguna persona real.
"""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path

import httpx
import pytest
import respx

import mp_curp_renapo.renapo as rn
from mp_curp_renapo.renapo import RenapoClient
from mp_curp_renapo.tests.conftest import make_valid_curp
from shared.errors import UpstreamError

API_2C = "https://api.2captcha.com"
CURP = make_valid_curp("XAXX010101HNEXXXA")
PAGINA_OK = (
    '<script src="https://www.google.com/recaptcha/enterprise.js?render='
    '6LSITEKEYVIVO000000000000000000000000000"></script>'
)
PAGINA_AKAMAI = '<html><title>Challenge Validation</title><iframe id="sec-cpt-if"></iframe></html>'
REGISTRO = {
    "curp": CURP, "nombres": "PRUEBA", "primerApellido": "SINTETICA", "segundoApellido": "FICTICIA",
    "sexo": "HOMBRE", "fechaNacimiento": "01/01/2001", "nacionalidad": "MEX", "entidad": "NACIDO EN EL EXTRANJERO",
    "statusCurp": "AN", "docProbatorio": 1,
    "datosDocProbatorio": {"anioReg": "2001", "numActa": "00000", "entidadRegistro": "NE"},
}
OK = {"codigo": "01", "mensaje": "Consulta exitosa", "registros": [REGISTRO]}


@pytest.fixture
def solver_on(monkeypatch):
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.setenv("PLUGINS_MX_CAPTCHA_SOLVER", "2captcha")
    monkeypatch.setenv("TWOCAPTCHA_API_KEY", "k")
    monkeypatch.setattr("shared.captcha_solver.time.sleep", lambda s: None)
    with respx.mock(assert_all_called=False) as mock:
        mock.get(rn.PORTAL_URL).respond(200, text=PAGINA_OK)
        crear = mock.post(f"{API_2C}/createTask").respond(200, json={"errorId": 0, "taskId": 1})
        mock.post(f"{API_2C}/getTaskResult").respond(
            200, json={"errorId": 0, "status": "ready", "solution": {"gRecaptchaResponse": "TOK"}})
        yield mock, crear


def _sin_cache(tmp_path: Path) -> None:
    cache = tmp_path / "cache"
    assert not cache.exists() or not any(p.is_file() for p in cache.rglob("*"))


@pytest.mark.asyncio
async def test_exito_por_curp(solver_on, tmp_path):
    mock, crear = solver_on
    api = mock.post(rn.API_CONSULTA).respond(200, json=OK)
    r = await RenapoClient().consultar(CURP)
    assert r["encontrada"] is True and r["consultado"] is True and r["simulated"] is False
    assert r["curp"] == CURP and r["nombre_completo"] == "PRUEBA SINTETICA FICTICIA"
    assert r["fecha_nacimiento"] == "01/01/2001" and r["estatus_curp"] == "AN"
    assert r["documento_probatorio"]["tipo"] == 1 and r["documento_probatorio"]["anioReg"] == "2001"
    assert "LFPDPPP" in r["aviso_privacidad"]
    body = json.loads(api.calls.last.request.content)
    assert body == {"curp": CURP, "tipoBusqueda": "curp", "ip": "127.0.0.1", "token": "TOK"}
    task = json.loads(crear.calls.last.request.content)["task"]
    assert task["websiteKey"] == "6LSITEKEYVIVO000000000000000000000000000"
    assert task["pageAction"] == "CONSULTA" and task["isEnterprise"] is True
    _sin_cache(tmp_path)


@pytest.mark.asyncio
async def test_exito_por_datos(solver_on, tmp_path):
    mock, _ = solver_on
    api = mock.post(rn.API_CONSULTA).respond(200, json=OK)
    r = await RenapoClient().consultar_por_datos("Prueba", "Sintética", "Ficticia", date(2001, 1, 1), "h", "ne")
    assert r["encontrada"] is True and r["tipo_busqueda"] == "datos" and r["curp"] == CURP
    body = json.loads(api.calls.last.request.content)
    assert body["primerApellido"] == "SINTETICA" and body["fechaNacimiento"] == "01/01/2001"
    assert body["diaNacimiento"] == "01" and body["selectedYear"] == "2001"
    assert body["sexo"] == "H" and body["claveEntidad"] == "NE" and body["tipoBusqueda"] == "datos"
    _sin_cache(tmp_path)


@pytest.mark.asyncio
async def test_no_encontrada(solver_on):
    mock, _ = solver_on
    mock.post(rn.API_CONSULTA).respond(200, json={"codigo": "02", "mensaje": "No se encontró registro"})
    r = await RenapoClient().consultar(CURP)
    assert r["encontrada"] is False and r["codigo"] == "02"


@pytest.mark.asyncio
async def test_token_rechazado_reintenta(solver_on):
    mock, crear = solver_on
    rechazo = httpx.Response(200, json={"codigo": "13", "mensaje": "Token de reCAPTCHA inválido"})
    mock.post(rn.API_CONSULTA).mock(side_effect=[rechazo, httpx.Response(200, json=OK)])
    assert (await RenapoClient().consultar(CURP))["encontrada"] is True
    assert crear.call_count == 2


@pytest.mark.asyncio
async def test_token_rechazado_siempre_upstream(solver_on):
    mock, crear = solver_on
    mock.post(rn.API_CONSULTA).respond(403, json={"mensaje": "captcha"})
    with pytest.raises(UpstreamError):
        await RenapoClient().consultar(CURP)
    assert crear.call_count == 3


@pytest.mark.asyncio
async def test_akamai_da_handoff_sin_gastar_captcha(solver_on):
    mock, crear = solver_on
    mock.get(rn.PORTAL_URL).respond(200, text=PAGINA_AKAMAI)
    r = await RenapoClient().consultar(CURP)
    assert r["requiere_humano"] is True and r["bloqueo_antibot"] == "akamai"
    assert r["campos_prellenados"] == {"curp": CURP}
    assert crear.call_count == 0


@pytest.mark.asyncio
async def test_solver_apagado_es_handoff_actual(monkeypatch):
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.delenv("PLUGINS_MX_CAPTCHA_SOLVER", raising=False)
    monkeypatch.setenv("TWOCAPTCHA_API_KEY", "k")
    with respx.mock() as mock:  # cualquier petición de red haría fallar el test
        r = await RenapoClient().consultar(CURP)
        assert not mock.calls
    esperado = {**rn.handoff_renapo(CURP), "validacion_local": r["validacion_local"]}
    esperado.pop("generado_en", None)
    r.pop("generado_en", None)
    assert r == esperado and "bloqueo_antibot" not in r


@pytest.mark.asyncio
async def test_bitacora_solo_hashes(solver_on, tmp_path):
    mock, _ = solver_on
    mock.post(rn.API_CONSULTA).respond(200, json=OK)
    await RenapoClient().consultar_por_datos("Prueba", "Sintetica", "", date(2001, 1, 1), "H", "NE")
    texto = "".join(p.read_text() for p in (tmp_path / "audit").rglob("*") if p.is_file())
    assert texto and "SINTETICA" not in texto and "PRUEBA" not in texto


@pytest.mark.live
@pytest.mark.asyncio
async def test_live_solver_renapo(tmp_path, monkeypatch):
    """Requiere TWOCAPTCHA_API_KEY y CURP_LIVE (la CURP propia del usuario)."""
    curp = os.environ.get("CURP_LIVE")
    if not (os.environ.get("TWOCAPTCHA_API_KEY") and curp):
        pytest.skip("requiere TWOCAPTCHA_API_KEY y CURP_LIVE")
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.setenv("PLUGINS_MX_CAPTCHA_SOLVER", "2captcha")
    r = await RenapoClient().consultar(curp)
    # Mientras Akamai siga delante de www.gob.mx esto es un handoff; si desaparece, consulta real.
    assert r.get("bloqueo_antibot") == "akamai" or (r["consultado"] and r["curp"] == curp.upper())
