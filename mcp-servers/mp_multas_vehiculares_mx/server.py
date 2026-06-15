"""mp_multas_vehiculares_mx — MCP server."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_multas_vehiculares_mx.client import MultasVehicularesMxClient  # noqa: E402


mcp = FastMCP("multas_vehiculares_mx")
_client = MultasVehicularesMxClient()


class ConsultaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: str = Field(..., min_length=2, max_length=10, description="cdmx|edomex|nl|jal")
    placa: str = Field(..., min_length=5, max_length=12)


@mcp.tool(annotations={"title": "Consultar multas por placa", "readOnlyHint": True, "openWorldHint": True})
def multas_consultar_por_placa(args: ConsultaInput) -> dict:
    """Lista multas activas para un vehículo según placa."""
    return _client.consultar_por_placa(args.estado, args.placa)


@mcp.tool(annotations={"title": "Calcular total + descuentos", "readOnlyHint": True})
def multas_calcular_total(args: ConsultaInput) -> dict:
    """Total con descuentos por pago oportuno (50% ≤15d, 25% ≤30d)."""
    return _client.calcular_total(args.estado, args.placa)


@mcp.tool(annotations={"title": "Listar sistemas estatales", "readOnlyHint": True, "idempotentHint": True})
def multas_listar_sistemas() -> dict:
    """Sistemas de multas vehiculares por estado."""
    return _client.listar_sistemas()


if __name__ == "__main__":
    mcp.run()
