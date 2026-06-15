"""mp_gas_natural_mx — MCP."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_gas_natural_mx.client import GasNaturalMxClient  # noqa: E402


mcp = FastMCP("gas_natural_mx")
_client = GasNaturalMxClient()


class ConsultarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    distribuidor: str = Field(..., min_length=3, max_length=20)
    contrato: str = Field(..., min_length=4, max_length=30)


@mcp.tool(annotations={"title": "Consultar recibo gas natural", "readOnlyHint": True, "openWorldHint": True})
def gas_consultar_recibo(args: ConsultarInput) -> dict:
    """Consulta recibo + consumo m³ + monto."""
    return _client.consultar_recibo(args.distribuidor, args.contrato)


@mcp.tool(annotations={"title": "Listar distribuidores gas", "readOnlyHint": True, "idempotentHint": True})
def gas_listar_distribuidores() -> dict:
    return _client.listar_distribuidores()


if __name__ == "__main__":
    mcp.run()
