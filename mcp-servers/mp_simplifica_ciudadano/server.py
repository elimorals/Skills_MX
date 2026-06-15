"""mp_simplifica_ciudadano MCP."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_simplifica_ciudadano.client import SimplificaCiudadanoClient  # noqa: E402


mcp = FastMCP("simplifica_ciudadano")
_client = SimplificaCiudadanoClient()


class EstadoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado_clave: str = Field(..., min_length=2, max_length=10)


class CompararInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estados_claves: list[str] = Field(..., min_length=1, max_length=32)


@mcp.tool(annotations={"title": "Estado simplificación por entidad", "readOnlyHint": True})
def simplifica_estado(args: EstadoInput) -> dict:
    return _client.estado(estado_clave=args.estado_clave)


@mcp.tool(annotations={"title": "Tracker nacional", "readOnlyHint": True, "idempotentHint": True})
def simplifica_tracker_nacional() -> dict:
    return _client.tracker_nacional()


@mcp.tool(annotations={"title": "Comparar estados", "readOnlyHint": True})
def simplifica_comparar_estados(args: CompararInput) -> dict:
    return _client.comparar_estados(estados_claves=args.estados_claves)


if __name__ == "__main__":
    mcp.run()
