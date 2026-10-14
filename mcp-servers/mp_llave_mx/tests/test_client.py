"""Tests mp_llave_mx — OAuth sin contraseñas, datos abiertos ATDT y handoffs."""
from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
import respx

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))

from mp_llave_mx.client import URL_CSV_ADOPCION, LlaveMXClient  # noqa: E402
from shared.errors import ConfigError, ValidationError  # noqa: E402

CSV = (_HERE / "fixtures" / "nuevos_usuarios.csv").read_bytes()


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
    monkeypatch.delenv("LLAVE_MX_CLIENT_ID", raising=False)
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))


def test_iniciar_oauth_arma_url_con_redirect_url(monkeypatch):
    monkeypatch.setenv("LLAVE_MX_CLIENT_ID", "123456")
    r = LlaveMXClient().iniciar_oauth("https://app.ejemplo.mx/callback", state="abc")
    u = urlparse(r["authorization_url"])
    assert u.netloc == "www.llave.gob.mx" and u.path == "/oauthV2.xhtml"
    q = parse_qs(u.query)
    assert q == {"client_id": ["123456"], "redirect_url": ["https://app.ejemplo.mx/callback"], "state": ["abc"]}


def test_iniciar_oauth_sin_client_id_es_config_error():
    with pytest.raises(ConfigError):
        LlaveMXClient().iniciar_oauth("https://app.ejemplo.mx/callback")


def test_redirect_no_https_rechazado(monkeypatch):
    monkeypatch.setenv("LLAVE_MX_CLIENT_ID", "123456")
    with pytest.raises(ValidationError):
        LlaveMXClient().iniciar_oauth("http://app.ejemplo.mx/callback")


def test_autenticar_con_password_retirado():
    with pytest.raises(ValidationError):
        LlaveMXClient().autenticar("GOMJ800101HDFRNN09", "secreta123")


def test_validar_token_sin_endpoint_publico():
    with pytest.raises(ConfigError):
        LlaveMXClient().validar_token("x" * 48)


@respx.mock
def test_adopcion_csv_real():
    respx.get(URL_CSV_ADOPCION).mock(return_value=httpx.Response(200, content=CSV))
    c = LlaveMXClient()
    nac = c.estadisticas_adopcion()
    assert nac["total_nuevos_usuarios"] == 8_439_610
    assert nac["periodo"] == "2024-10-01 a 2025-05-01"
    assert c.estadisticas_adopcion("Aguascalientes")["total_nuevos_usuarios"] == 85_439


def test_listar_tramites_marcado_no_verificado():
    r = LlaveMXClient().listar_tramites(categoria="fiscal")
    assert r["verificado"] is False
    assert r["total"] >= 1


def test_detalle_inexistente():
    with pytest.raises(ValidationError):
        LlaveMXClient().detalle_tramite("xxx")


def test_vincular_e_firma_handoff():
    r = LlaveMXClient().vincular_e_firma("GOMJ800101HDFRNN09")
    assert r["requiere_humano"] is True
    assert r["e_firma_vinculada"] is None


@pytest.mark.live
def test_live_endpoints_y_adopcion():
    c = LlaveMXClient()
    e = c.estado_endpoints()
    assert e["http_status"] == 200 and e["redirige_a_oauthV2"] is True
    assert c.estadisticas_adopcion()["total_nuevos_usuarios"] > 0
