"""mp_repep_profeco MCP."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_repep_profeco.client import REPEPClient  # noqa: E402


mcp = FastMCP("repep_profeco")
_client = REPEPClient()


class TelInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    telefono: str = Field(..., min_length=10, max_length=15)


class LoteInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    telefonos: list[str] = Field(..., min_length=1, max_length=5000)


class InscribirInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    telefono: str = Field(..., min_length=10, max_length=15)
    propietario_curp: str | None = None


@mcp.tool(annotations={"title": "Consultar REPEP", "readOnlyHint": True})
def repep_consultar(args: TelInput) -> dict:
    return _client.consultar(telefono=args.telefono)


@mcp.tool(annotations={"title": "Filtrar lote contactables", "readOnlyHint": True})
def repep_filtrar_lote(args: LoteInput) -> dict:
    return _client.filtrar_lote(telefonos=args.telefonos)


@mcp.tool(annotations={"title": "Inscribir teléfono en REPEP", "readOnlyHint": True})
def repep_inscribir(args: InscribirInput) -> dict:
    return _client.inscribir(telefono=args.telefono, propietario_curp=args.propietario_curp)


@mcp.tool(annotations={"title": "Estadísticas REPEP", "readOnlyHint": True, "idempotentHint": True})
def repep_estadisticas() -> dict:
    return _client.estadisticas()


if __name__ == "__main__":
    mcp.run()
