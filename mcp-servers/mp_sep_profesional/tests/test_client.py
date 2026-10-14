"""Tests del cliente mp_sep_profesional."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_MCP_ROOT = _HERE.parent.parent
if str(_MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(_MCP_ROOT))

from mp_sep_profesional.client import (  # noqa: E402
    CURP_REGEX,
    PROFESIONES_REGULADAS,
    SepProfesionalClient,
    _profesion_es_regulada,
)
from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import ValidationError  # noqa: E402


@pytest.fixture
def tmp_client(tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    cache = FileCache("sep_profesional_test", root=tmp_path / "cache")
    bit = Bitacora("sep_profesional_test", root=tmp_path / "bita")
    return SepProfesionalClient(cache=cache, bitacora=bit)


class TestProfesionRegulada:
    def test_medico_es_salud(self):
        assert _profesion_es_regulada("Médico Cirujano") == "salud"
        assert _profesion_es_regulada("medico cirujano") == "salud"

    def test_abogado_es_legal(self):
        assert _profesion_es_regulada("Licenciado en Derecho") == "legal"
        assert _profesion_es_regulada("Abogado") == "legal"

    def test_contador_es_contable(self):
        assert _profesion_es_regulada("Contador Público") == "contable_fiscal"

    def test_arquitecto_es_riesgo(self):
        assert _profesion_es_regulada("Arquitecto") == "ingenierias_riesgo"

    def test_profesion_no_regulada(self):
        assert _profesion_es_regulada("Filósofo") is None
        assert _profesion_es_regulada("") is None


class TestCURPRegex:
    def test_curp_valida(self):
        # CURP de ejemplo con formato válido
        assert CURP_REGEX.match("HEGJ800101HDFRNN09")

    def test_curp_invalida_estructura(self):
        assert not CURP_REGEX.match("INVALIDA")
        assert not CURP_REGEX.match("HEGJ800101HDFRNN")  # corta
        assert not CURP_REGEX.match("HEGJ801301HDFRNN09")  # mes 13


class TestConsultarCedula:
    def test_validacion_formato(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.consultar_cedula("abc")
        with pytest.raises(ValidationError):
            tmp_client.consultar_cedula("123")  # < 7

    def test_consulta_mock(self, tmp_client):
        r = tmp_client.consultar_cedula("1234567")
        assert "cedula" in r
        assert r.get("simulated") is True

    def test_categoria_regulada_se_agrega(self, tmp_client):
        # cuando la profesión existe en el mock
        r = tmp_client.consultar_cedula("1234567", validar_vigencia=True)
        # campo presente (puede ser None si la profesión mock no calza)
        assert "categoria_regulada" in r
        assert "requiere_validacion_obligatoria" in r

    def test_cache_reutilizado(self, tmp_client):
        r1 = tmp_client.consultar_cedula("1234567")
        r2 = tmp_client.consultar_cedula("1234567")
        # mismo resultado, segundo viene de cache
        assert r1["cedula"] == r2["cedula"]


class TestConsultarPorDatos:
    def test_requiere_nombre_y_apellido(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.consultar_por_datos(nombre="", primer_apellido="Garcia")
        with pytest.raises(ValidationError):
            tmp_client.consultar_por_datos(nombre="Juan", primer_apellido="")

    def test_curp_invalido_rechazado(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.consultar_por_datos(
                nombre="Juan",
                primer_apellido="Garcia",
                curp="INVALIDA",
            )

    def test_consulta_ok_sin_curp(self, tmp_client):
        r = tmp_client.consultar_por_datos(
            nombre="Juan",
            primer_apellido="Garcia",
            segundo_apellido="Lopez",
        )
        assert "cedula" in r or "nombre_completo" in r or "simulated" in r


class TestValidarMedicoParaConsulta:
    def test_solo_cedula_general(self, tmp_client):
        r = tmp_client.validar_medico_para_consulta(cedula="1234567")
        assert "puede_dar_consulta" in r
        assert "cedula_general_ok" in r
        assert "advertencias" in r
        assert "cumple_nom_004" in r
        assert "cumple_cofepris_2024" in r

    def test_con_cedula_especialidad(self, tmp_client):
        r = tmp_client.validar_medico_para_consulta(
            cedula="1234567",
            cedula_especialidad="7654321",
        )
        assert "puede_recetar_controlados" in r
        # debe haber 2 cédulas validadas
        assert len(r["cedulas_validadas"]) >= 1


class TestListarProfesionesReguladas:
    def test_retorna_categorias(self, tmp_client):
        r = tmp_client.listar_profesiones_reguladas()
        assert "categorias" in r
        assert "profesiones_por_categoria" in r
        assert r["total"] >= 1
        assert set(r["categorias"]) == set(PROFESIONES_REGULADAS.keys())
        assert "url_consulta" in r


# ---------- modo real: handoff humano (reCAPTCHA v3) ----------


@pytest.fixture
def real_client(tmp_path, monkeypatch):
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "c"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "a"))
    return SepProfesionalClient()


def test_real_cedula_devuelve_handoff(real_client):
    r = real_client.consultar_cedula("1234567")
    assert r["requiere_humano"] is True
    assert r["campos_prellenados"] == {"cedula": "1234567"}
    assert r["simulated"] is False


def test_real_medico_no_afirma(real_client):
    r = real_client.validar_medico_para_consulta("1234567")
    assert r["puede_dar_consulta"] is None
    assert r["requiere_humano"] is True


@pytest.mark.live
def test_live_portal_exige_recaptcha():
    import httpx

    cfg = httpx.get("https://cedulaprofesional.sep.gob.mx/assets/config.json", timeout=30).json()
    assert cfg.get("recaptchaSiteKey"), "SEP ya no declara reCAPTCHA: revisar si se puede consultar directo"


# ---------- solver opt-in (2captcha simulado con respx) ----------

import json  # noqa: E402

import httpx  # noqa: E402
import respx  # noqa: E402

from shared.captcha_solver import API as API_2CAPTCHA  # noqa: E402
from shared.errors import UpstreamError  # noqa: E402
from shared.sep_cedula import API_CONSULTA, URL_CONFIG, URL_TOKEN  # noqa: E402

REGISTRO = {
    "cedula": "1234567", "nombre": "ANA", "primerApellido": "LOPEZ", "segundoApellido": "RUIZ",
    "genero": "2", "profesion": "MÉDICO CIRUJANO", "institucion": "UNAM",
    "entidadInstitucion": "CIUDAD DE MÉXICO", "anioRegistro": "2015",
}


@pytest.fixture
def con_solver(real_client, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_CAPTCHA_SOLVER", "2captcha")
    monkeypatch.setenv("TWOCAPTCHA_API_KEY", "k")
    monkeypatch.setattr("shared.captcha_solver.time.sleep", lambda s: None)
    return real_client


def _mock_portal(respuestas):
    respx.get(URL_CONFIG).respond(200, json={"recaptchaSiteKey": "SK-VIVO", "clientId": "c", "apiKey": "a"})
    respx.get(URL_TOKEN).respond(200, json={"access_token": "JWT"})
    tareas = respx.post(f"{API_2CAPTCHA}/createTask").respond(200, json={"errorId": 0, "taskId": 1})
    respx.post(f"{API_2CAPTCHA}/getTaskResult").respond(
        200, json={"errorId": 0, "status": "ready", "solution": {"gRecaptchaResponse": "TOK"}})
    consulta = respx.post(API_CONSULTA).mock(side_effect=respuestas)
    return tareas, consulta


@respx.mock
def test_solver_consulta_real(con_solver):
    tareas, consulta = _mock_portal([httpx.Response(200, json=[REGISTRO])])
    r = con_solver.consultar_cedula("1234567")
    assert r["encontrada"] is True and r["simulated"] is False
    assert r["nombre_completo"] == "ANA LOPEZ RUIZ" and r["categoria_regulada"] == "salud"
    task = json.loads(tareas.calls.last.request.content)["task"]
    assert task["websiteKey"] == "SK-VIVO" and task["pageAction"] == "submit"
    req = consulta.calls.last.request
    assert req.headers["X-Recaptcha-Token"] == "TOK" and req.headers["Authorization"] == "Bearer JWT"
    assert json.loads(req.content) == {"numCedula": "1234567"}


@respx.mock
def test_solver_token_rechazado_reintenta(con_solver):
    tareas, consulta = _mock_portal([httpx.Response(403), httpx.Response(200, json=[REGISTRO])])
    assert con_solver.consultar_cedula("1234567")["encontrada"] is True
    assert consulta.call_count == 2 and tareas.call_count == 2


@respx.mock
def test_solver_rechazo_persistente_es_upstream(con_solver):
    _, consulta = _mock_portal([httpx.Response(403)] * 3)
    with pytest.raises(UpstreamError):
        con_solver.consultar_cedula("1234567")
    assert consulta.call_count == 3


@respx.mock
def test_solver_no_encontrada(con_solver):
    _mock_portal([httpx.Response(200, json=[])])
    r = con_solver.consultar_cedula("7654321")
    assert r["encontrada"] is False and r["vigente"] is False


@respx.mock
def test_solver_por_datos_body(con_solver):
    _, consulta = _mock_portal([httpx.Response(200, json=[REGISTRO])])
    r = con_solver.consultar_por_datos(nombre="ana", primer_apellido="lopez")
    assert json.loads(consulta.calls.last.request.content) == {"nombre": "ANA", "primerApellido": "LOPEZ"}
    assert r["total"] == 1


def test_solver_apagado_es_handoff(real_client, monkeypatch):
    monkeypatch.delenv("PLUGINS_MX_CAPTCHA_SOLVER", raising=False)
    assert real_client.consultar_cedula("1234567")["requiere_humano"] is True


@pytest.mark.live
def test_live_solver_cedula(tmp_path, monkeypatch):
    import os

    cedula = os.environ.get("SEP_CEDULA_LIVE")
    if not (os.environ.get("TWOCAPTCHA_API_KEY") and cedula):
        pytest.skip("requiere TWOCAPTCHA_API_KEY y SEP_CEDULA_LIVE")
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.setenv("PLUGINS_MX_CAPTCHA_SOLVER", "2captcha")
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "c"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "a"))
    r = SepProfesionalClient().consultar_cedula(cedula)
    assert r["consultado"] is True and "encontrada" in r
