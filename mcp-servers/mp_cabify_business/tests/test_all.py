"""Tests mp_cabify_business contra el contrato de la Ride-Hailing API v4."""

from __future__ import annotations

import json
import os

import pytest
import respx

from mp_cabify_business.client import CabifyBusinessClient
from mp_cabify_business.server import ViajeIdInput, cabify_consultar_viaje, cabify_listar_catalogos
from shared.errors import AuthError, ConfigError, McpError

H = "https://cabify.com"
_LIVE = {v: os.environ.get(v, "") for v in ("CABIFY_CLIENT_ID", "CABIFY_CLIENT_SECRET")}


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("CABIFY_CLIENT_ID", "uuid")
    monkeypatch.setenv("CABIFY_CLIENT_SECRET", "sec")


def _token():
    return respx.post(f"{H}/auth/api/authorization").respond(200, json={"access_token": "T", "expires_in": 2591999})


def test_sin_credenciales_es_simulado() -> None:
    c = CabifyBusinessClient()
    assert c.is_mock is True


async def test_mock_marcado() -> None:
    r = await CabifyBusinessClient().consultar_viaje("j1")
    assert r["simulated"] is True


def test_env_invalido(monkeypatch) -> None:
    monkeypatch.setenv("CABIFY_ENV", "staging")
    with pytest.raises(ConfigError):
        CabifyBusinessClient()


@respx.mock
async def test_estimar_body_y_token(creds) -> None:
    tok = _token()
    ruta = respx.post(f"{H}/api/v4/estimates").respond(200, json=[{"product": {"id": "p1", "name": "Lite"}}])
    r = await CabifyBusinessClient().estimar("u1", (19.43, -99.13), (19.36, -99.18))
    assert r["simulated"] is False and r["estimaciones"][0]["product"]["id"] == "p1"
    body = json.loads(ruta.calls.last.request.content)
    assert body == {"requester_id": "u1", "start_type": "asap", "stops": [{"loc": [19.43, -99.13]}, {"loc": [19.36, -99.18]}]}
    assert ruta.calls.last.request.headers["Authorization"] == "Bearer T"
    assert b"grant_type=client_credentials" in tok.calls.last.request.content


@respx.mock
async def test_estimar_reservado(creds) -> None:
    _token()
    ruta = respx.post(f"{H}/api/v4/estimates").respond(200, json=[])
    await CabifyBusinessClient().estimar("u1", (1, 2), (3, 4), inicio="2026-10-20T08:00:00Z")
    body = json.loads(ruta.calls.last.request.content)
    assert body["start_type"] == "reserved" and body["start_at"] == "2026-10-20T08:00:00Z"


@respx.mock
async def test_pedir_viaje_body(creds) -> None:
    _token()
    ruta = respx.post(f"{H}/api/v4/journey").respond(200, json={"id": "j1"})
    rider = {"name": "Ana", "mobile": {"mobile_cc": "52", "mobile_num": "5512345678"}}
    r = await CabifyBusinessClient().pedir_viaje("u1", "p1", (1, 2), (3, 4), rider, origen_direccion="Reforma 1", label_slug="ventas")
    assert r["id"] == "j1"
    body = json.loads(ruta.calls.last.request.content)
    assert body["product_id"] == "p1" and body["label_slug"] == "ventas"
    assert body["stops"][0] == {"loc": [1, 2], "addr": "Reforma 1"}


@respx.mock
async def test_cancelar_conflicto_409(creds) -> None:
    _token()
    respx.post(f"{H}/api/v4/journey/j1/state").respond(409, json={"message": "can't cancel journey at current state"})
    with pytest.raises(McpError) as e:
        await CabifyBusinessClient().cancelar_viaje("j1")
    assert e.value.details["status_code"] == 409


@respx.mock
async def test_ventas_y_token_reutilizado(creds) -> None:
    tok = _token()
    respx.get(f"{H}/api/v4/journey/j1/sales").respond(200, json=[{"code": "S1", "currency": "MXN"}])
    respx.get(f"{H}/api/v4/journey/j1").respond(200, json={"id": "j1", "finished": True})
    c = CabifyBusinessClient()
    assert (await c.ventas_viaje("j1"))["ventas"][0]["code"] == "S1"
    assert (await c.consultar_viaje("j1"))["finished"] is True
    assert tok.call_count == 1


@respx.mock
async def test_credenciales_invalidas(creds) -> None:
    respx.post(f"{H}/auth/api/authorization").respond(401, json={"error": "invalid_client"})
    with pytest.raises(AuthError):
        await CabifyBusinessClient().estado_viaje("j1")


@respx.mock
async def test_sandbox(creds, monkeypatch) -> None:
    monkeypatch.setenv("CABIFY_ENV", "sandbox")
    respx.post("https://cabify-sandbox.com/auth/api/authorization").respond(200, json={"access_token": "T", "expires_in": 10})
    respx.get("https://cabify-sandbox.com/api/v4/journey/j1/state").respond(200, json={"name": "hired"})
    assert (await CabifyBusinessClient().estado_viaje("j1"))["name"] == "hired"


async def test_tool_devuelve_error_como_dict(creds) -> None:
    with respx.mock:
        respx.post(f"{H}/auth/api/authorization").respond(500)
        r = await cabify_consultar_viaje(ViajeIdInput(journey_id="j1"))
    assert "error" in json.dumps(r).lower()


async def test_catalogo() -> None:
    assert "terminated" in (await cabify_listar_catalogos())["estados_viaje"]


@pytest.mark.live
async def test_live_token_sandbox(monkeypatch) -> None:
    if not all(_LIVE.values()):
        pytest.skip("requiere CABIFY_CLIENT_ID y CABIFY_CLIENT_SECRET de sandbox")
    for k, v in _LIVE.items():
        monkeypatch.setenv(k, v)
    monkeypatch.setenv("CABIFY_ENV", os.environ.get("CABIFY_ENV", "sandbox"))
    assert len(await CabifyBusinessClient()._auth()) > 10
