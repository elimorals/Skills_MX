"""Tests mp_ine_verificacion — formatos, regla de vigencia y handoff (reCAPTCHA)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import httpx
import pytest
import respx

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))

from mp_ine_verificacion.client import (  # noqa: E402
    RECAPTCHA_SITEKEY, URL_LISTA_NOMINAL, URL_RESULTADO, INEVerificacionClient,
)
from shared.captcha_solver import API  # noqa: E402
from shared.errors import UpstreamError, ValidationError  # noqa: E402

AUT = "autorizacion-firmada-" + "0001"  # referencia de prueba, no es credencial


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))
    monkeypatch.delenv("PLUGINS_MX_CAPTCHA_SOLVER", raising=False)


def test_verificar_modelo_g_es_handoff():
    r = INEVerificacionClient().verificar_datos("G", AUT, cic="012345678", id_ciudadano="000123456")
    assert r["requiere_humano"] is True
    assert r["en_lista_nominal"] is None
    assert r["campos_a_capturar"] == ["cic", "id_ciudadano"]


def test_cic_de_13_digitos_rechazado():
    with pytest.raises(ValidationError):
        INEVerificacionClient().verificar_datos("E", AUT, cic="1234567890123", id_ciudadano="000123456")


def test_modelo_c_pide_clave_elector():
    c = INEVerificacionClient()
    r = c.verificar_datos("C", AUT, clave_elector="GOMZJN80010109H400", numero_emision="03",
                          ocr="1234567890123")
    assert r["campos_a_capturar"] == ["clave_elector", "numero_emision", "ocr"]
    with pytest.raises(ValidationError):
        c.verificar_datos("C", AUT, cic="012345678")


def test_sin_autorizacion_falla():
    with pytest.raises(ValidationError):
        INEVerificacionClient().verificar_datos("G", "", cic="012345678", id_ciudadano="000123456")


def test_vigencia_regla_10_anios():
    c = INEVerificacionClient()
    assert c.consultar_vigencia("G", 2020)["vigente_por_regla"] is True
    viejo = c.consultar_vigencia("E", 2014)
    assert viejo["vence_fin_de_anio"] == 2024
    assert viejo["vigente_por_regla"] is False
    assert c.consultar_vigencia("D", 2025)["vigente_por_regla"] is False  # modelo no vigente


def test_qr_no_se_afirma():
    r = INEVerificacionClient().verificar_qr("INE.MX.QR." + "x" * 40)
    assert r["autentica"] is None


def test_modelos_publicados():
    r = INEVerificacionClient().listar_modelos_credencial()
    vigentes = [m["clave"] for m in r["modelos"] if m["vigente_segun_ine"]]
    assert vigentes == ["E", "F", "G", "H", "I", "J"]


def test_autorizacion_template():
    r = INEVerificacionClient().generar_autorizacion("GOMJ800101HDFRNN09", "Alta de cliente en fintech")
    assert "AUTORIZO" in r["texto_autorizacion"]
    assert "simulated" not in r


def test_mock_solo_con_flag(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    r = INEVerificacionClient().verificar_datos("G", AUT, cic="012345678", id_ciudadano="000123456")
    assert r["simulated"] is True


# ---------- solver opt-in (fixtures sintéticas, sin datos reales) ----------

FORM_HTML = (f'<form id="formEFGH" action="resultado.html" method="post">'
             f'<div class="g-recaptcha" data-sitekey="{RECAPTCHA_SITEKEY}"></div></form>')
VIGENTE_HTML = ("<html><header>INE</header><main><h3>Resultado</h3><p>Tu Credencial para Votar es "
                "vigente y estás en la Lista Nominal.</p><p>Fecha de consulta: 14/10/2026</p></main></html>")
NO_VIGENTE_HTML = "<main><p>Tu Credencial para Votar no es vigente.</p></main>"
G = {"cic": "012345678", "id_ciudadano": "000123456"}  # sintéticos


@pytest.fixture
def solver_on(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_CAPTCHA_SOLVER", "2captcha")
    monkeypatch.setenv("TWOCAPTCHA_API_KEY", "k")
    monkeypatch.setattr("shared.captcha_solver.time.sleep", lambda s: None)


def _mock_2captcha():
    crear = respx.post(f"{API}/createTask").respond(200, json={"errorId": 0, "taskId": 1})
    respx.post(f"{API}/getTaskResult").respond(
        200, json={"errorId": 0, "status": "ready", "solution": {"gRecaptchaResponse": "tok"}})
    return crear


@respx.mock
def test_solver_vigente(solver_on):
    crear = _mock_2captcha()
    respx.get(URL_LISTA_NOMINAL).respond(200, text=FORM_HTML)
    post = respx.post(URL_RESULTADO).respond(200, text=VIGENTE_HTML)
    r = INEVerificacionClient().verificar_datos("G", AUT, **G)
    assert r["consultado"] is True and r["estado"] == "vigente" and r["vigente"] is True
    assert r["en_lista_nominal"] is True and r["fecha_portal"] == "14/10/2026"
    assert "vigente" in r["mensaje_oficial"] and "LFPDPPP" in r["aviso_privacidad"]
    task = json.loads(crear.calls[0].request.content)["task"]
    assert task["type"] == "RecaptchaV2TaskProxyless" and task["websiteKey"] == RECAPTCHA_SITEKEY
    body = post.calls[0].request.content.decode()
    assert "modelo=e" in body and "idCiudadano=000123456" in body and "g-recaptcha-response=tok" in body


@respx.mock
def test_solver_no_vigente_modelo_d(solver_on):
    _mock_2captcha()
    respx.get(URL_LISTA_NOMINAL).respond(200, text=FORM_HTML)
    post = respx.post(URL_RESULTADO).respond(200, text=NO_VIGENTE_HTML)
    r = INEVerificacionClient().verificar_datos("D", AUT, cic="012345678", ocr="1234567890123")
    assert r["estado"] == "no_vigente" and r["vigente"] is False
    assert "modelo=d" in post.calls[0].request.content.decode()


@respx.mock
def test_solver_no_encontrada(solver_on):
    _mock_2captcha()
    respx.get(URL_LISTA_NOMINAL).respond(200, text=FORM_HTML)
    respx.post(URL_RESULTADO).respond(200, text="<main><p>No se encontró ningún registro con los datos.</p></main>")
    r = INEVerificacionClient().verificar_datos("G", AUT, **G)
    assert r["estado"] == "no_encontrada" and r["en_lista_nominal"] is False


@respx.mock
def test_token_rechazado_reintenta_y_luego_upstream(solver_on):
    crear = _mock_2captcha()
    respx.get(URL_LISTA_NOMINAL).respond(200, text=FORM_HTML)
    respx.post(URL_RESULTADO).mock(side_effect=[
        httpx.Response(200, text=FORM_HTML), httpx.Response(200, text=VIGENTE_HTML)])
    r = INEVerificacionClient().verificar_datos("G", AUT, **G)
    assert r["estado"] == "vigente" and crear.call_count == 2

    respx.post(URL_RESULTADO).respond(200, text=FORM_HTML)
    with pytest.raises(UpstreamError):
        INEVerificacionClient().verificar_datos("G", AUT, **G)


@respx.mock
def test_cloudflare_challenge_es_handoff(solver_on):
    crear = _mock_2captcha()
    respx.get(URL_LISTA_NOMINAL).respond(403, headers={"cf-mitigated": "challenge"},
                                         text="<title>Just a moment...</title>")
    r = INEVerificacionClient().verificar_datos("G", AUT, **G)
    assert r["requiere_humano"] is True and r["motivo"] == "bot_manager"
    assert crear.call_count == 0  # no se gasta captcha si Cloudflare bloquea


@respx.mock
def test_solver_apagado_es_handoff_actual():
    ruta = respx.get(URL_LISTA_NOMINAL)
    r = INEVerificacionClient().verificar_datos("G", AUT, **G)
    assert r["motivo"] == "captcha" and r["en_lista_nominal"] is None
    assert "aviso_privacidad" not in r and ruta.call_count == 0


@respx.mock
def test_sin_cache_y_bitacora_solo_hashes(solver_on):
    _mock_2captcha()
    respx.get(URL_LISTA_NOMINAL).respond(200, text=FORM_HTML)
    post = respx.post(URL_RESULTADO).respond(200, text=VIGENTE_HTML)
    c = INEVerificacionClient()
    for _ in range(2):
        c.verificar_datos("G", AUT, **G)
    assert post.call_count == 2
    log = json.dumps(c._bitacora.tail(5))
    assert "012345678" not in log and "000123456" not in log and "cic_hash" in log


@pytest.mark.live
def test_live_credencial_propia(monkeypatch):
    """Credencial propia: INE_TEST_MODELO + INE_TEST_CIC / _ID_CIUDADANO / _OCR / _CLAVE_ELECTOR / _NUMERO_EMISION."""
    if not os.environ.get("TWOCAPTCHA_API_KEY") or not os.environ.get("INE_TEST_MODELO"):
        pytest.skip("requiere TWOCAPTCHA_API_KEY e INE_TEST_* de la credencial propia")
    monkeypatch.setenv("PLUGINS_MX_CAPTCHA_SOLVER", "2captcha")
    campos = {k: os.environ.get(f"INE_TEST_{k.upper()}")
              for k in ("cic", "id_ciudadano", "ocr", "clave_elector", "numero_emision")}
    r = INEVerificacionClient().verificar_datos(os.environ["INE_TEST_MODELO"], AUT, **campos)
    assert r.get("estado") in {"vigente", "no_vigente", "no_encontrada"} or r["motivo"] == "bot_manager"
