"""mp_agua_mx — MCP standalone para consulta unificada de agua MX."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_agua_mx.client import AguaMxClient  # noqa: E402


mcp = FastMCP("agua_mx")
_client = AguaMxClient()


class ConsultarAdeudoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    organismo: str = Field(..., min_length=2, max_length=40,
                            description="Clave del organismo: sacmex, siapa, sadm, cespt, sapal, ceaq, japac, aguakan, etc.")
    cuenta: str = Field(..., min_length=3, max_length=30,
                         description="Identificador del usuario (varía por organismo).")


class ListarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    solo_consultables: bool = Field(False, description="Si True, solo retorna organismos con scraper funcional.")


class BuscarPorEstadoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: str = Field(..., min_length=2, max_length=10, description="Código estado (CDMX, JAL, NL, etc.)")


@mcp.tool(annotations={"title": "Consultar adeudo de agua", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
def agua_consultar_adeudo(args: ConsultarAdeudoInput) -> dict:
    """Consulta adeudo + estatus de una cuenta de agua municipal/estatal."""
    return _client.consultar_adeudo(args.organismo, args.cuenta)


@mcp.tool(annotations={"title": "Listar organismos operadores de agua", "readOnlyHint": True, "idempotentHint": True})
def agua_listar_organismos(args: ListarInput) -> dict:
    """Lista los organismos operadores en el catálogo."""
    return _client.listar_organismos(args.solo_consultables)


@mcp.tool(annotations={"title": "Buscar organismos por estado", "readOnlyHint": True, "idempotentHint": True})
def agua_buscar_por_estado(args: BuscarPorEstadoInput) -> dict:
    """Lista organismos que cubren un estado mexicano."""
    return _client.buscar_por_estado(args.estado)


@mcp.tool(annotations={"title": "Estadísticas del catálogo de agua", "readOnlyHint": True, "idempotentHint": True})
def agua_estadisticas() -> dict:
    """Stats agregadas del catálogo (cobertura, consultables, etc.)."""
    return _client.estadisticas_catalogo()


if __name__ == "__main__":
    mcp.run()
