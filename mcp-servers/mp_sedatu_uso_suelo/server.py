"""mp_sedatu_uso_suelo MCP."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_sedatu_uso_suelo.client import SEDATUUsoSueloClient  # noqa: E402


mcp = FastMCP("sedatu_uso_suelo")
_client = SEDATUUsoSueloClient()


class BuscarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: str = Field(..., min_length=2)
    municipio: str = Field(..., min_length=2)
    clave_tramite: str


class UsoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: str = Field(..., min_length=2)
    municipio: str = Field(..., min_length=2)
    giro_propuesto: str = Field(..., min_length=3)


class EstimarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: str = Field(..., min_length=2)
    municipio: str = Field(..., min_length=2)
    m2_construir: float = Field(..., gt=0)
    uso: str = "habitacional"


@mcp.tool(annotations={"title": "Buscar trámite municipal RETyS", "readOnlyHint": True})
def sedatu_buscar_tramite(args: BuscarInput) -> dict:
    return _client.buscar_tramite(estado=args.estado, municipio=args.municipio,
                                    clave_tramite=args.clave_tramite)


@mcp.tool(annotations={"title": "Consultar uso suelo permitido", "readOnlyHint": True})
def sedatu_consultar_uso_suelo(args: UsoInput) -> dict:
    return _client.consultar_uso_suelo_permitido(
        estado=args.estado, municipio=args.municipio, giro_propuesto=args.giro_propuesto,
    )


@mcp.tool(annotations={"title": "Estimar construcción", "readOnlyHint": True, "idempotentHint": True})
def sedatu_estimar_construccion(args: EstimarInput) -> dict:
    return _client.estimar_construccion(estado=args.estado, municipio=args.municipio,
                                          m2_construir=args.m2_construir, uso=args.uso)


@mcp.tool(annotations={"title": "Listar trámites", "readOnlyHint": True, "idempotentHint": True})
def sedatu_listar_tramites() -> dict:
    return _client.listar_tramites()


if __name__ == "__main__":
    mcp.run()
