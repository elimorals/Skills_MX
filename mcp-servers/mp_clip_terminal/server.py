"""mp_clip_terminal — MCP para Clip (POS MX)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_clip_terminal.catalogos import (  # noqa: E402
    CHARGE_STATUS,
    COMISIONES_TIPICAS,
    SETTLEMENT_FRECUENCIA,
    TIPOS_TERMINAL,
)
from mp_clip_terminal.client import ClipTerminalClient  # noqa: E402
from shared.errors import McpError  # noqa: E402


mcp = FastMCP("clip_terminal_mcp")
_client = ClipTerminalClient()


class ListChargesInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fecha_desde: Optional[str] = Field(None, description="ISO date YYYY-MM-DD")
    limit: int = Field(50, ge=1, le=200)
    status: Optional[Literal[
        "pending", "approved", "declined", "refunded", "voided", "chargeback"
    ]] = None


class ChargeIdInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    charge_id: str = Field(..., min_length=1, max_length=80)


class RefundInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    charge_id: str = Field(..., min_length=1, max_length=80)
    amount_mxn: Optional[float] = Field(None, ge=0)


class TerminalIdInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    terminal_id: str = Field(..., min_length=1, max_length=50)


class FechaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fecha: str = Field(..., min_length=10, max_length=10)


@mcp.tool(annotations={"title": "Listar charges Clip", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def clip_list_charges(args: ListChargesInput) -> dict:
    try:
        return await _client.list_charges(args.fecha_desde, args.limit, args.status)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Detalle charge Clip", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def clip_get_charge(args: ChargeIdInput) -> dict:
    try:
        return await _client.get_charge(args.charge_id)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Refund charge Clip", "readOnlyHint": False, "destructiveHint": True, "openWorldHint": True})
async def clip_refund_charge(args: RefundInput) -> dict:
    try:
        return await _client.refund_charge(args.charge_id, args.amount_mxn)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Status terminal Clip (batería, señal, transacciones)", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def clip_terminal_status(args: TerminalIdInput) -> dict:
    try:
        return await _client.get_terminal_status(args.terminal_id)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Liquidación Clip del día (depósito a tu banco)", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def clip_get_settlement(args: FechaInput) -> dict:
    """Reporte de liquidación T+1: brutos, comisiones, retenciones, neto depositado."""
    try:
        return await _client.get_settlement(args.fecha)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Catálogos Clip: terminales, comisiones, status", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def clip_listar_catalogos() -> dict:
    return {
        "tipos_terminal": TIPOS_TERMINAL,
        "comisiones_tipicas": COMISIONES_TIPICAS,
        "charge_status": CHARGE_STATUS,
        "settlement_frecuencia": SETTLEMENT_FRECUENCIA,
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
