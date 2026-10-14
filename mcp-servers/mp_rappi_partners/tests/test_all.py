"""Tests mp_rappi_partners contra el contrato del dev-portal de Rappi."""

import json
import os

import pytest
import respx

from mp_rappi_partners.client import RappiPartnersClient
from shared.errors import AuthError, ConfigError, NotFoundError

API, SRV = "https://api.rappi.com.mx", "https://services.mxgrability.rappi.com"
V2 = f"{SRV}/api/v2/restaurants-integrations-public-api"
ORDEN = {"order_detail": {"order_id": "392625", "totals": {"total_order": 23900}}}
_LIVE = {v: os.environ.get(v, "") for v in ("RAPPI_CLIENT_ID", "RAPPI_CLIENT_SECRET", "RAPPI_STORE_ID")}


@pytest.fixture(autouse=True)
def env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    for v in ("RAPPI_CLIENT_ID", "RAPPI_CLIENT_SECRET", "RAPPI_STORE_ID", "RAPPI_ENV", "PLUGINS_MX_MOCK"):
        monkeypatch.delenv(v, raising=False)


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("RAPPI_CLIENT_ID", "cid")
    monkeypatch.setenv("RAPPI_CLIENT_SECRET", "sec")
    monkeypatch.setenv("RAPPI_STORE_ID", "900")


def _token():
    return respx.post(f"{API}/restaurants/auth/v1/token/login/integrations").respond(
        200, json={"access_token": "T", "token_type": "Bearer", "expires_in": 86400}
    )


def test_sin_credenciales_simulado():
    assert RappiPartnersClient().listar_ordenes()["simulated"] is True


@respx.mock
def test_listar_ordenes_real(creds):
    tok = _token()
    ruta = respx.get(f"{V2}/orders").respond(200, json=[ORDEN, ORDEN])
    r = RappiPartnersClient().listar_ordenes(limite=1)
    assert r["simulated"] is False and r["total"] == 1
    assert ruta.calls.last.request.url.params["storeId"] == "900"
    assert ruta.calls.last.request.headers["x-authorization"] == "Bearer T"
    assert json.loads(tok.calls.last.request.content) == {"client_id": "cid", "client_secret": "sec"}


@respx.mock
def test_listar_ordenes_sent(creds):
    _token()
    ruta = respx.get(f"{V2}/orders/status/sent").respond(200, json=[])
    RappiPartnersClient().listar_ordenes(estado="sent")
    assert ruta.called


@respx.mock
def test_consultar_orden(creds):
    _token()
    respx.get(f"{V2}/orders").respond(200, json=[ORDEN])
    c = RappiPartnersClient()
    assert c.consultar_orden("392625")["order_detail"]["totals"]["total_order"] == 23900
    with pytest.raises(NotFoundError):
        c.consultar_orden("1")


@respx.mock
def test_actualizar_disponibilidad_body(creds):
    _token()
    ruta = respx.patch(f"{API}/restaurants/menu/v1/stores/900/products/SKU/stock").respond(200, json={})
    RappiPartnersClient().actualizar_disponibilidad("HAMB-1", False)
    assert json.loads(ruta.calls.last.request.content) == {"available": [], "unavailable": ["HAMB-1"]}


@respx.mock
def test_menu(creds):
    _token()
    respx.get(f"{V2}/menu/rappi/900").respond(200, json={"storeId": "900", "items": []})
    assert RappiPartnersClient().listar_productos_menu()["menu"]["storeId"] == "900"


def test_falta_store_id(creds, monkeypatch):
    monkeypatch.delenv("RAPPI_STORE_ID")
    with respx.mock:
        _token()
        with pytest.raises(ConfigError):
            RappiPartnersClient().listar_productos_menu()


@respx.mock
def test_credenciales_invalidas(creds):
    respx.post(f"{API}/restaurants/auth/v1/token/login/integrations").respond(401, json={})
    with pytest.raises(AuthError):
        RappiPartnersClient().listar_ordenes()


def test_sin_endpoint_es_error_explicito(creds):
    c = RappiPartnersClient()
    for fn in (c.consultar_ranking_zona, c.estimar_comisiones_mes):
        with pytest.raises(ConfigError) as e:
            fn()
        assert e.value.details["motivo"] == "sin_endpoint"


@pytest.mark.live
def test_live_listar_ordenes(monkeypatch):
    if not all(_LIVE.values()):
        pytest.skip("requiere RAPPI_CLIENT_ID, RAPPI_CLIENT_SECRET y RAPPI_STORE_ID")
    for k, v in _LIVE.items():
        monkeypatch.setenv(k, v)
    monkeypatch.setenv("RAPPI_ENV", os.environ.get("RAPPI_ENV", "dev"))
    assert RappiPartnersClient().listar_ordenes()["simulated"] is False
