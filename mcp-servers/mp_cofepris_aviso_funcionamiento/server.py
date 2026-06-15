"""mp_cofepris_aviso_funcionamiento MCP."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_cofepris_aviso_funcionamiento.client import COFEPRISAvisoClient  # noqa: E402


mcp = FastMCP("cofepris_aviso")
_client = COFEPRISAvisoClient()


class ActividadInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    actividad: str = Field(..., min_length=3)


class RequisitosInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    actividad: str = Field(..., min_length=3)
    estado: str = Field(..., min_length=2, max_length=10)


class ConsultarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    identificador: str = Field(..., min_length=8)


@mcp.tool(annotations={"title": "Clasificar giro COFEPRIS", "readOnlyHint": True, "idempotentHint": True})
def cofepris_clasificar_giro(args: ActividadInput) -> dict:
    return _client.clasificar_giro(actividad=args.actividad)


@mcp.tool(annotations={"title": "Requisitos aviso funcionamiento", "readOnlyHint": True})
def cofepris_requisitos_aviso(args: RequisitosInput) -> dict:
    return _client.requisitos_aviso(actividad=args.actividad, estado=args.estado)


@mcp.tool(annotations={"title": "Consultar aviso vigente", "readOnlyHint": True})
def cofepris_consultar_aviso(args: ConsultarInput) -> dict:
    return _client.consultar_aviso(identificador=args.identificador)


@mcp.tool(annotations={"title": "Listar giros catálogo", "readOnlyHint": True, "idempotentHint": True})
def cofepris_listar_giros() -> dict:
    return _client.listar_giros_catalogo()


if __name__ == "__main__":
    mcp.run()
