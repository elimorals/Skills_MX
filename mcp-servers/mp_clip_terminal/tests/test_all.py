"""Tests mp_clip_terminal contra la referencia de developer.clip.mx."""

from __future__ import annotations

import base64
import json
import os

import pytest
import respx

from mp_clip_terminal.client import GW, PINPAD, REFUNDS, ClipTerminalClient
from mp_clip_terminal.server import FechaInput, clip_get_settlement, clip_listar_catalogos
from shared.errors import AuthError, ConfigError, NotFoundError

TOKEN = "Basic " + base64.b64encode(b"k:s").decode()
_LIVE = {v: os.environ.get(v, "") for v in ("CLIP_API_KEY", "CLIP_SECRET_KEY")}


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("CLIP_API_KEY", "k")
    monkeypatch.setenv("CLIP_SECRET_KEY", "s")


def test_sin_credenciales_simulado() -> None:
    assert ClipTerminalClient().is_mock is True


async def test_mock_marcado() -> None:
    assert (await ClipTerminalClient().list_charges())["simulated"] is True


def test_falta_secret(monkeypatch) -> None:
    monkeypatch.setenv("CLIP_API_KEY", "k")
    with pytest.raises(ConfigError):
        ClipTerminalClient()._token()


@respx.mock
async def test_list_charges(creds) -> None:
    ruta = respx.get(f"{GW}/payments").respond(200, json={"data": [{"receipt_no": "R1"}]})
    r = await ClipTerminalClient().list_charges("2026-10-01", limit=10, status="approved")
    q = ruta.calls.last.request.url.params
    assert q["from"] == "2026-10-01" and q["limit"] == "10" and q["status"] == "approved" and "to" in q
    assert ruta.calls.last.request.headers["Authorization"] == TOKEN
    assert r["simulated"] is False


@respx.mock
async def test_get_charge(creds) -> None:
    respx.get(f"{GW}/payments/receipt-no/R1").respond(200, json={"receipt_no": "R1", "amount": 250.0})
    assert (await ClipTerminalClient().get_charge("R1"))["amount"] == 250.0


@respx.mock
async def test_refund_parcial_body(creds) -> None:
    ruta = respx.post(f"{REFUNDS}/refunds").respond(201, json={"id": "rf1"})
    await ClipTerminalClient().refund_charge("R1", 100.0, reason="Producto dañado")
    assert json.loads(ruta.calls.last.request.content) == {
        "amount": 100.0, "reason": "Producto dañado", "reference": {"type": "receipt", "id": "R1"},
    }


@respx.mock
async def test_refund_total_lee_monto(creds) -> None:
    respx.get(f"{GW}/payments/receipt-no/R1").respond(200, json={"amount": 250.0})
    ruta = respx.post(f"{REFUNDS}/refunds").respond(201, json={"id": "rf1"})
    await ClipTerminalClient().refund_charge("R1")
    assert json.loads(ruta.calls.last.request.content)["amount"] == 250.0


@respx.mock
async def test_terminal_status(creds) -> None:
    respx.get(f"{PINPAD}/f2f/pinpad/v1/devices/status").respond(
        200, json=[{"serial_number": "P8-1", "status": "active"}]
    )
    c = ClipTerminalClient()
    assert (await c.get_terminal_status("P8-1"))["status"] == "active"
    with pytest.raises(NotFoundError):
        await c.get_terminal_status("otro")


@respx.mock
async def test_settlement_usa_x_api_key(creds) -> None:
    ruta = respx.get(f"{GW}/settlements").respond(200, json=[{"settlement_report_id": "S1"}])
    r = await clip_get_settlement(FechaInput(fecha="2026-10-13"))
    assert r["settlements"][0]["settlement_report_id"] == "S1"
    assert ruta.calls.last.request.headers["x-api-key"] == TOKEN


@respx.mock
async def test_credenciales_invalidas(creds) -> None:
    respx.get(f"{GW}/payments/receipt-no/R1").respond(401)
    with pytest.raises(AuthError):
        await ClipTerminalClient().get_charge("R1")


async def test_catalogos() -> None:
    assert "tipos_terminal" in await clip_listar_catalogos()


@pytest.mark.live
async def test_live_list_charges(monkeypatch) -> None:
    if not all(_LIVE.values()):
        pytest.skip("requiere CLIP_API_KEY y CLIP_SECRET_KEY")
    for k, v in _LIVE.items():
        monkeypatch.setenv(k, v)
    assert (await ClipTerminalClient().list_charges())["simulated"] is False
