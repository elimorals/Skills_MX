"""mp_donatarias_sat — MCP standalone padrón donatarias SAT.

Tools expuestas:
- donatarias_consultar(rfc)
- donatarias_buscar(razon_social, [entidad], [limite])
- donatarias_listar_por_entidad(entidad)
- donatarias_estadisticas()
- donatarias_listar_rubros()

Universo: ~10,000 donatarias autorizadas + cualquier donante que quiera deducir.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_donatarias_sat.client import DonatariasSatClient  # noqa: E402


mcp = FastMCP("donatarias_sat")
_client = DonatariasSatClient()


class ConsultarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rfc: str = Field(..., min_length=12, max_length=13,
                     description="RFC del posible donatario (PM 12 chars o PF 13 chars).")


class BuscarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    razon_social: str = Field(..., min_length=3, max_length=200,
                              description="Nombre o razón social de la donataria (≥3 chars).")
    entidad: Optional[str] = Field(None, min_length=2, max_length=10,
                                    description="Clave estado MX para filtrar (CDMX, JAL, NL, etc).")
    limite: int = Field(20, ge=1, le=100)


class ListarPorEntidadInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entidad: str = Field(..., min_length=2, max_length=10,
                          description="Clave de la entidad federativa (CDMX, JAL, etc).")


@mcp.tool(annotations={
    "title": "Validar donataria autorizada por RFC",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def donatarias_consultar(args: ConsultarInput) -> dict:
    """Verifica si un RFC está autorizado como donataria por SAT.

    Útil ANTES de emitir CFDI con uso D04 (Donativos) o de aceptar un recibo deducible.
    Si NO está autorizada, el donante NO podrá deducir.

    Returns:
        {
          "rfc": "...",
          "autorizada": bool,
          "razon_social": "FUNDACION X AC" | null,
          "entidad": "CDMX" | null,
          "rubro": "asistencia_social" | "educacion" | ...,
          "fecha_autorizacion": "YYYY-MM-DD",
          "vigencia_anexo_14": "2026",
          "puede_emitir_recibo_deducible": bool,
          "advertencias": [...]
        }
    """
    return _client.consultar_donataria(args.rfc)


@mcp.tool(annotations={
    "title": "Buscar donatarias por razón social",
    "readOnlyHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
})
def donatarias_buscar(args: BuscarInput) -> dict:
    """Búsqueda fuzzy por nombre o razón social. Útil cuando no se tiene el RFC."""
    return _client.buscar_donatarias(
        razon_social=args.razon_social,
        entidad=args.entidad,
        limite=args.limite,
    )


@mcp.tool(annotations={
    "title": "Listar donatarias por entidad federativa",
    "readOnlyHint": True,
    "idempotentHint": True,
})
def donatarias_listar_por_entidad(args: ListarPorEntidadInput) -> dict:
    """Devuelve todas las donatarias autorizadas en una entidad federativa."""
    return _client.listar_por_entidad(args.entidad)


@mcp.tool(annotations={
    "title": "Estadísticas del padrón completo",
    "readOnlyHint": True,
    "idempotentHint": True,
})
def donatarias_estadisticas() -> dict:
    """Stats del padrón: total, distribución por entidad y por rubro."""
    return _client.estadisticas_padron()


@mcp.tool(annotations={
    "title": "Catálogo de rubros reconocidos por SAT",
    "readOnlyHint": True,
    "idempotentHint": True,
})
def donatarias_listar_rubros() -> dict:
    """Devuelve los 10 rubros de actividad que SAT reconoce para donatarias."""
    return _client.listar_rubros()


if __name__ == "__main__":
    mcp.run()
