"""mp_lnetb_auditor MCP — auditor LNETB ranking estatal."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_lnetb_auditor.client import LnetbAuditorClient  # noqa: E402


mcp = FastMCP("lnetb_auditor")
_client = LnetbAuditorClient()


class EstadoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado_clave: str = Field(..., min_length=2, max_length=10)


class RankingInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    top: int = Field(32, ge=1, le=32)


class CompararInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estados_claves: list[str] = Field(..., min_length=1, max_length=10)


@mcp.tool(annotations={"title": "Listar 10 indicadores LNETB", "readOnlyHint": True, "idempotentHint": True})
def lnetb_listar_indicadores() -> dict:
    return _client.listar_indicadores()


@mcp.tool(annotations={"title": "Evaluar estado con score compuesto", "readOnlyHint": True})
def lnetb_evaluar_estado(args: EstadoInput) -> dict:
    return _client.evaluar_estado(args.estado_clave)


@mcp.tool(annotations={"title": "Ranking nacional 32 estados", "readOnlyHint": True, "idempotentHint": True})
def lnetb_ranking_nacional(args: RankingInput) -> dict:
    return _client.ranking_nacional(top=args.top)


@mcp.tool(annotations={"title": "Comparar 2-10 estados side-by-side", "readOnlyHint": True})
def lnetb_comparar_estados(args: CompararInput) -> dict:
    return _client.comparar_estados(args.estados_claves)


if __name__ == "__main__":
    mcp.run()
