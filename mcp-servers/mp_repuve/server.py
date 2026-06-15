"""mp_repuve — MCP standalone para REPUVE (vehículos robados)."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_repuve.client import RepuveClient  # noqa: E402


mcp = FastMCP("repuve")
_client = RepuveClient()


class ConsultarNivInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    niv: str = Field(..., min_length=17, max_length=17, description="NIV/VIN 17 caracteres (sin I/O/Q).")


class ConsultarPlacaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    placa: str = Field(..., min_length=5, max_length=12, description="Placa mexicana.")


class VerificarRobadoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    niv: str = Field("", max_length=17)
    placa: str = Field("", max_length=12)


@mcp.tool(annotations={"title": "Consultar REPUVE por NIV", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
def repuve_consultar_niv(args: ConsultarNivInput) -> dict:
    """Consulta REPUVE por número de serie (NIV/VIN). Devuelve marca, modelo, estatus de robo, etc."""
    return _client.consultar_niv(args.niv)


@mcp.tool(annotations={"title": "Consultar REPUVE por placa", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
def repuve_consultar_placa(args: ConsultarPlacaInput) -> dict:
    """Consulta REPUVE por placa mexicana."""
    return _client.consultar_placa(args.placa)


@mcp.tool(annotations={"title": "Verificar reporte de robo (binario)", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
def repuve_verificar_robado(args: VerificarRobadoInput) -> dict:
    """Decisión binaria para aseguradoras / movilidad / marketplaces.

    Returns tiene_reporte_robo: bool + advertencias contextuales.
    """
    return _client.verificar_robado(niv=args.niv, placa=args.placa)


if __name__ == "__main__":
    mcp.run()
