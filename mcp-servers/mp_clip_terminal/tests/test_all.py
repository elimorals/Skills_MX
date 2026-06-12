"""Tests mp_clip_terminal."""

from __future__ import annotations

import pytest

from mp_clip_terminal.client import ClipTerminalClient
from mp_clip_terminal.server import (
    ChargeIdInput,
    FechaInput,
    ListChargesInput,
    RefundInput,
    TerminalIdInput,
    clip_get_charge,
    clip_get_settlement,
    clip_list_charges,
    clip_listar_catalogos,
    clip_refund_charge,
    clip_terminal_status,
)


@pytest.fixture
def client() -> ClipTerminalClient:
    return ClipTerminalClient()


def test_default_mock(client: ClipTerminalClient) -> None:
    assert client.is_mock is True


def test_con_api_key_no_mock(monkeypatch) -> None:
    monkeypatch.setenv("CLIP_API_KEY", "demo_key")
    c = ClipTerminalClient()
    assert c.is_mock is False


@pytest.mark.asyncio
async def test_list_charges(client: ClipTerminalClient) -> None:
    r = await client.list_charges(limit=10)
    assert "charges" in r
    assert r["simulated"] is True


@pytest.mark.asyncio
async def test_get_charge(client: ClipTerminalClient) -> None:
    r = await client.get_charge("clip_charge_001234")
    assert r["status"] == "approved"
    assert "comision_porcentaje" in r


@pytest.mark.asyncio
async def test_refund(client: ClipTerminalClient) -> None:
    r = await client.refund_charge("clip_charge_001", amount_mxn=200.0)
    assert r["status"] == "approved"


@pytest.mark.asyncio
async def test_terminal_status(client: ClipTerminalClient) -> None:
    r = await client.get_terminal_status("TERM-001")
    assert r["status"] == "active"


@pytest.mark.asyncio
async def test_settlement(client: ClipTerminalClient) -> None:
    r = await client.get_settlement("2026-03-15")
    assert "total_neto_depositado_mxn" in r


@pytest.mark.asyncio
async def test_list_tool() -> None:
    r = await clip_list_charges(ListChargesInput(limit=5))
    assert "charges" in r


@pytest.mark.asyncio
async def test_get_tool() -> None:
    r = await clip_get_charge(ChargeIdInput(charge_id="clip_x"))
    assert "comision_porcentaje" in r


@pytest.mark.asyncio
async def test_refund_tool() -> None:
    r = await clip_refund_charge(RefundInput(charge_id="clip_x"))
    assert r["status"] == "approved"


@pytest.mark.asyncio
async def test_terminal_tool() -> None:
    r = await clip_terminal_status(TerminalIdInput(terminal_id="TERM-001"))
    assert "bateria_porcentaje" in r


@pytest.mark.asyncio
async def test_settlement_tool() -> None:
    r = await clip_get_settlement(FechaInput(fecha="2026-03-15"))
    assert r["fecha_liquidacion"] == "2026-03-15"


@pytest.mark.asyncio
async def test_catalogos() -> None:
    r = await clip_listar_catalogos()
    assert "tipos_terminal" in r
    assert "clip_pro" in r["tipos_terminal"]
