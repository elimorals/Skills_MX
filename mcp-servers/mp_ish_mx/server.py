"""mp_ish_mx — MCP."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_ish_mx.client import IshMxClient  # noqa: E402


mcp = FastMCP("ish_mx")
_client = IshMxClient()


class CalcularInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: str = Field(..., min_length=2, max_length=10)
    monto_hospedaje: float = Field(..., ge=0)


class InfoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: str = Field(..., min_length=2, max_length=10)


class ListarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    solo_aplicables: bool = Field(False)


class CompararInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estados: list[str] = Field(..., min_length=1, max_length=32)
    monto_hospedaje: float = Field(..., ge=0)


@mcp.tool(annotations={"title": "Calcular ISH (Impuesto Hospedaje)", "readOnlyHint": True, "idempotentHint": True})
def ish_calcular(args: CalcularInput) -> dict:
    """Calcula ISH dado el estado + monto de hospedaje."""
    return _client.calcular(args.estado, args.monto_hospedaje)


@mcp.tool(annotations={"title": "Info ISH por estado", "readOnlyHint": True, "idempotentHint": True})
def ish_info_estado(args: InfoInput) -> dict:
    return _client.info_estado(args.estado)


@mcp.tool(annotations={"title": "Listar estados con ISH", "readOnlyHint": True, "idempotentHint": True})
def ish_listar_estados(args: ListarInput) -> dict:
    return _client.listar_estados(args.solo_aplicables)


@mcp.tool(annotations={"title": "Comparar ISH entre estados", "readOnlyHint": True, "idempotentHint": True})
def ish_comparar_estados(args: CompararInput) -> dict:
    return _client.comparar_estados(args.estados, args.monto_hospedaje)


if __name__ == "__main__":
    mcp.run()
