"""Tests para mp_repuve."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_MCP_ROOT = _HERE.parent.parent
sys.path.insert(0, str(_MCP_ROOT))


# ============================================================
# Validación de identificadores
# ============================================================

class TestValidarNIV:
    def test_niv_valido(self):
        from shared.repuve import validar_niv
        assert validar_niv("3VWFE21C04M000001") == "3VWFE21C04M000001"

    def test_niv_uppercase_normalize(self):
        from shared.repuve import validar_niv
        assert validar_niv("3vwfe21c04m000001") == "3VWFE21C04M000001"

    def test_niv_strip_spaces_dashes(self):
        from shared.repuve import validar_niv
        assert validar_niv("3VW-FE21C-04M-000001") == "3VWFE21C04M000001"

    def test_niv_corto(self):
        from shared.repuve import validar_niv
        with pytest.raises(ValueError):
            validar_niv("ABC123")

    def test_niv_caracteres_invalidos(self):
        from shared.repuve import validar_niv
        # I, O, Q no se permiten en VIN según ISO 3779
        with pytest.raises(ValueError):
            validar_niv("3VWFE21C04I000001")  # contiene I
        with pytest.raises(ValueError):
            validar_niv("3VWFE21C04O000001")  # contiene O
        with pytest.raises(ValueError):
            validar_niv("3VWFE21C04Q000001")  # contiene Q


class TestValidarPlaca:
    def test_placa_valida(self):
        from shared.repuve import validar_placa
        assert validar_placa("ABC-12-34") == "ABC-12-34"
        assert validar_placa("ABC1234") == "ABC1234"

    def test_placa_normalize_upper(self):
        from shared.repuve import validar_placa
        assert validar_placa("abc-1234") == "ABC-1234"

    def test_placa_vacia(self):
        from shared.repuve import validar_placa
        with pytest.raises(ValueError):
            validar_placa("")

    def test_placa_formato_invalido(self):
        from shared.repuve import validar_placa
        with pytest.raises(ValueError):
            validar_placa("XX")


# ============================================================
# Cliente (mock mode)
# ============================================================

@pytest.fixture(autouse=True)
def _mock_mode(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    monkeypatch.delenv("PLUGINS_MX_REPUVE_LIVE", raising=False)
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))
    yield


class TestRepuveClient:
    def test_consultar_niv_devuelve_vehiculo(self):
        from mp_repuve.client import RepuveClient
        c = RepuveClient()
        r = c.consultar_niv("3VWFE21C04M000002")  # ends in 2 → sin robo
        assert r["encontrado"] is True
        assert r["vehiculo"]["niv"] == "3VWFE21C04M000002"
        assert r["vehiculo"]["tiene_reporte_robo"] is False
        assert r["simulated"] is True

    def test_consultar_niv_terminado_en_1_simula_robo(self):
        from mp_repuve.client import RepuveClient
        c = RepuveClient()
        r = c.consultar_niv("3VWFE21C04M000001")  # ends in 1 → robo
        assert r["vehiculo"]["tiene_reporte_robo"] is True
        assert "ROBO ACTIVO" in r["vehiculo"]["estatus_robo"]

    def test_consultar_placa(self):
        from mp_repuve.client import RepuveClient
        c = RepuveClient()
        r = c.consultar_placa("XYZ1234")
        assert r["encontrado"] is True
        assert r["vehiculo"]["placa"] == "XYZ1234"

    def test_niv_fake_devuelve_no_encontrado(self):
        from mp_repuve.client import RepuveClient
        c = RepuveClient()
        # 17 chars con FAKE en medio
        r = c.consultar_niv("3VWFFAKE0000000001")[:17] if False else c.consultar_niv("FAKEAAA0000000000")
        assert r["encontrado"] is False
        assert r["vehiculo"] is None

    def test_cache_hit_segunda_llamada(self):
        from mp_repuve.client import RepuveClient
        c = RepuveClient()
        c.consultar_niv("3VWFE21C04M000002")
        r2 = c.consultar_niv("3VWFE21C04M000002")
        assert r2["encontrado"] is True


class TestVerificarRobado:
    def test_robo_emite_advertencia_critica(self):
        from mp_repuve.client import RepuveClient
        c = RepuveClient()
        r = c.verificar_robado(niv="3VWFE21C04M000001")  # robado
        assert r["tiene_reporte_robo"] is True
        assert any("ROBO ACTIVO" in adv for adv in r["advertencias"])

    def test_sin_robo_sin_advertencia_critica(self):
        from mp_repuve.client import RepuveClient
        c = RepuveClient()
        r = c.verificar_robado(niv="3VWFE21C04M000002")
        assert r["tiene_reporte_robo"] is False

    def test_no_encontrado_emite_advertencia(self):
        from mp_repuve.client import RepuveClient
        c = RepuveClient()
        r = c.verificar_robado(niv="FAKEAAA0000000000")
        assert r["consultado"] is False
        assert any("NO encontrado" in adv for adv in r["advertencias"])

    def test_sin_niv_ni_placa_lanza(self):
        from mp_repuve.client import RepuveClient
        from shared.errors import ValidationError
        c = RepuveClient()
        with pytest.raises(ValidationError):
            c.verificar_robado()


# ============================================================
# Modo real: handoff humano (reCAPTCHA v3)
# ============================================================


@pytest.fixture
def real_client(tmp_path, monkeypatch):
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))
    from mp_repuve.client import RepuveClient

    return RepuveClient()


def test_real_devuelve_handoff(real_client):
    r = real_client.consultar_niv("3VWFE21C04M000001")
    assert r["requiere_humano"] is True
    assert r["campos_prellenados"] == {"niv": "3VWFE21C04M000001"}
    assert r["simulated"] is False


def test_verificar_robado_real_no_afirma_sin_robo(real_client):
    r = real_client.verificar_robado(placa="ABC1234")
    assert r["tiene_reporte_robo"] is None
    assert r["consultado"] is False
    assert r["detalle"]["requiere_humano"] is True


@pytest.mark.live
def test_live_api_sigue_exigiendo_recaptcha():
    """Sin token, la API responde 401 reCaptcha: el handoff sigue siendo necesario."""
    import httpx

    from shared.repuve import API_URL

    import ssl

    import certifi

    ctx = ssl.create_default_context(cafile=certifi.where())
    ctx.set_ciphers("DEFAULT:@SECLEVEL=1")  # el servidor REPUVE solo negocia cifrados legacy
    r = httpx.post(API_URL, json={}, timeout=30, verify=ctx)
    assert r.status_code == 401
    assert "recaptcha" in r.text.lower()


# ============================================================
# Modo real con solver opt-in (2captcha simulado con respx)
# ============================================================

import base64  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402

import httpx  # noqa: E402
import respx  # noqa: E402

API_2C = "https://api.2captcha.com"


@pytest.fixture
def llaves():
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    priv = rsa.generate_private_key(public_exponent=65537, key_size=1024)
    pem = priv.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode().strip()
    return priv, pem


@pytest.fixture
def solver_on(monkeypatch, real_client, llaves):
    import shared.repuve as rp

    monkeypatch.setenv("PLUGINS_MX_CAPTCHA_SOLVER", "2captcha")
    monkeypatch.setenv("TWOCAPTCHA_API_KEY", "k")
    monkeypatch.setattr("shared.captcha_solver.time.sleep", lambda s: None)
    monkeypatch.setattr(rp, "_CONFIG", {})
    _, pem = llaves
    js_pem = pem.replace("\n", "\\n")
    bundle = (f'const wo_recaptcha_siteKey="6LSITEKEYVIVO000000000000000000000000000";'
              f'this.publicKeyRep="{js_pem}",this.publicKeyPgj="{js_pem}"')
    with respx.mock(assert_all_called=False) as mock:
        mock.get(rp.PORTAL_URL).respond(200, text='<script src="./main.abc123.js"></script>')
        mock.get(rp.PORTAL_URL + "main.abc123.js").respond(200, text=bundle)
        crear = mock.post(f"{API_2C}/createTask").respond(200, json={"errorId": 0, "taskId": 1})
        mock.post(f"{API_2C}/getTaskResult").respond(
            200, json={"errorId": 0, "status": "ready", "solution": {"gRecaptchaResponse": "TOK"}})
        yield mock, crear, real_client


def _descifrar(priv, b64):
    from cryptography.hazmat.primitives.asymmetric import padding

    return priv.decrypt(base64.b64decode(b64), padding.PKCS1v15()).decode()


FILA = {"PLACA": "ABC1234", "MARCA": "VOLKSWAGEN", "MODELO": "JETTA", "ANIO_MODELO": "2018",
        "TIPO": "SEDAN", "VIN": "3VWFE21C04M000001", "ENTIDAD_EMPLACO": "JALISCO", "LINEA": "JETTA", "CLASE": "AUTO"}


def test_solver_consulta_real_cifra_y_parsea(solver_on, llaves):
    import shared.repuve as rp

    mock, crear, client = solver_on
    rep = mock.post(rp.API_URL).respond(200, json={"0": [FILA]})
    mock.post(rp.API_PGJ).respond(200, json={})
    r = client.consultar_placa("ABC1234")
    assert r["encontrado"] is True and r["simulated"] is False and r["modo"] == "real"
    assert r["vehiculo"]["marca"] == "VOLKSWAGEN" and r["vehiculo"]["tiene_reporte_robo"] is False
    body = json.loads(rep.calls.last.request.content)
    priv, _ = llaves
    assert _descifrar(priv, body["criterio"]) == "1" and _descifrar(priv, body["llave"]) == "ABC1234"
    assert body["token"] == "TOK"
    task = json.loads(crear.calls.last.request.content)["task"]
    assert task["websiteKey"] == "6LSITEKEYVIVO000000000000000000000000000" and task["pageAction"] == "login"


def test_solver_robo_activo(solver_on):
    import shared.repuve as rp

    mock, _, client = solver_on
    mock.post(rp.API_URL).respond(200, json={"0": [FILA]})
    mock.post(rp.API_PGJ).respond(200, json={"0": [{"ESTATUS_VHI_ROBO": "ROBADO"}]})
    assert client.verificar_robado(niv="3VWFE21C04M000001")["tiene_reporte_robo"] is True


def test_solver_token_rechazado_reintenta(solver_on):
    import shared.repuve as rp

    mock, crear, client = solver_on
    rechazo = httpx.Response(401, json={"statusCode": 401, "message": "El reCaptcha no fue superado correctamente"})
    mock.post(rp.API_URL).mock(side_effect=[rechazo, httpx.Response(200, json={"0": [FILA]})])
    mock.post(rp.API_PGJ).respond(200, json={})
    assert client.consultar_placa("ABC1234")["encontrado"] is True
    assert crear.call_count == 3  # 2 para /repuve + 1 para /pgj


def test_solver_token_rechazado_siempre_upstream(solver_on):
    import shared.repuve as rp
    from shared.errors import UpstreamError

    mock, crear, client = solver_on
    mock.post(rp.API_URL).respond(401, json={"statusCode": 401, "message": "El reCaptcha no fue superado"})
    with pytest.raises(UpstreamError):
        client.consultar_placa("ABC1234")
    assert crear.call_count == 3


def test_solver_pgj_caido_robo_desconocido(solver_on):
    import shared.repuve as rp

    mock, _, client = solver_on
    mock.post(rp.API_URL).respond(200, json={"0": [FILA]})
    mock.post(rp.API_PGJ).respond(504)
    r = client.verificar_robado(placa="ABC1234")
    assert r["tiene_reporte_robo"] is None and r["advertencias"]


def test_solver_apagado_es_handoff(real_client, monkeypatch):
    monkeypatch.delenv("PLUGINS_MX_CAPTCHA_SOLVER", raising=False)
    monkeypatch.setenv("TWOCAPTCHA_API_KEY", "k")
    assert real_client.consultar_placa("ABC1234")["requiere_humano"] is True


@pytest.mark.live
def test_live_solver_repuve(tmp_path, monkeypatch):
    """Requiere TWOCAPTCHA_API_KEY y REPUVE_LIVE_PLACA (placa propia)."""
    placa = os.environ.get("REPUVE_LIVE_PLACA")
    if not (os.environ.get("TWOCAPTCHA_API_KEY") and placa):
        pytest.skip("requiere TWOCAPTCHA_API_KEY y REPUVE_LIVE_PLACA")
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.setenv("PLUGINS_MX_CAPTCHA_SOLVER", "2captcha")
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "c"))
    from mp_repuve.client import RepuveClient

    r = RepuveClient().consultar_placa(placa)
    assert r["modo"] == "real" and "encontrado" in r
