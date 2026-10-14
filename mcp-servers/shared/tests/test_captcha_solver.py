import json
import os

import httpx
import pytest
import respx

from shared.captcha_solver import API, CaptchaSolver, solver_activo
from shared.errors import ConfigError, UpstreamError


@pytest.fixture(autouse=True)
def env(monkeypatch):
    for v in ("PLUGINS_MX_CAPTCHA_SOLVER", "TWOCAPTCHA_API_KEY", "ANTHROPIC_API_KEY"):
        monkeypatch.delenv(v, raising=False)


@pytest.fixture
def activo(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_CAPTCHA_SOLVER", "2captcha")
    monkeypatch.setenv("TWOCAPTCHA_API_KEY", "k")


def _solver():
    return CaptchaSolver(http=httpx.Client(), poll_s=0, timeout_s=5)


def test_apagado_por_defecto():
    assert solver_activo() is False


def test_activo_y_exclusiones(activo):
    assert solver_activo("saf_cdmx") is True
    assert solver_activo("citas_monitor") is False
    assert solver_activo("repep_profeco") is False


@respx.mock
def test_imagen_limpia_texto(activo):
    crear = respx.post(f"{API}/createTask").respond(200, json={"errorId": 0, "taskId": 7})
    respx.post(f"{API}/getTaskResult").mock(side_effect=[
        httpx.Response(200, json={"errorId": 0, "status": "processing"}),
        httpx.Response(200, json={"errorId": 0, "status": "ready", "solution": {"text": " aB-12 "}}),
    ])
    assert _solver().imagen(b"png") == "aB12"
    body = json.loads(crear.calls.last.request.content)
    assert body["clientKey"] == "k" and body["task"]["type"] == "ImageToTextTask"


@respx.mock
def test_recaptcha_v3_task(activo):
    crear = respx.post(f"{API}/createTask").respond(200, json={"errorId": 0, "taskId": 1})
    respx.post(f"{API}/getTaskResult").respond(200, json={"errorId": 0, "status": "ready", "solution": {"gRecaptchaResponse": "TOK"}})
    assert _solver().recaptcha("SK", "https://x.gob.mx", version="v3", accion="consulta") == "TOK"
    task = json.loads(crear.calls.last.request.content)["task"]
    assert task["type"] == "RecaptchaV3TaskProxyless" and task["pageAction"] == "consulta"


@respx.mock
def test_turnstile(activo):
    respx.post(f"{API}/createTask").respond(200, json={"errorId": 0, "taskId": 1})
    respx.post(f"{API}/getTaskResult").respond(200, json={"errorId": 0, "status": "ready", "solution": {"token": "T"}})
    assert _solver().turnstile("SK", "https://x.gob.mx") == "T"


@respx.mock
def test_saldo_cero_es_config_error(activo):
    respx.post(f"{API}/createTask").respond(200, json={"errorId": 10, "errorCode": "ERROR_ZERO_BALANCE"})
    with pytest.raises(ConfigError):
        _solver().recaptcha("SK", "https://x")


@respx.mock
def test_imagen_sin_respaldo_falla_limpio(activo):
    respx.post(f"{API}/createTask").respond(200, json={"errorId": 12, "errorCode": "ERROR_CAPTCHA_UNSOLVABLE"})
    with pytest.raises(UpstreamError):
        _solver().imagen(b"png")


@respx.mock
def test_imagen_respaldo_vision(activo, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "a")
    respx.post(f"{API}/createTask").respond(200, json={"errorId": 12, "errorCode": "ERROR_CAPTCHA_UNSOLVABLE"})
    respx.post("https://api.anthropic.com/v1/messages").respond(200, json={"content": [{"type": "text", "text": "XY7Z"}]})
    assert _solver().imagen(b"png") == "XY7Z"


def test_sin_llave():
    with pytest.raises(ConfigError):
        CaptchaSolver()


@pytest.mark.live
def test_live_saldo():
    if not os.environ.get("TWOCAPTCHA_API_KEY"):
        pytest.skip("requiere TWOCAPTCHA_API_KEY propia")
    r = httpx.post(f"{API}/getBalance", json={"clientKey": os.environ["TWOCAPTCHA_API_KEY"]}, timeout=30).json()
    assert r.get("errorId") == 0
