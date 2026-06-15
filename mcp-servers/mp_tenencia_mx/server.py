"""mp_tenencia_mx — MCP standalone."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_tenencia_mx.client import TenenciaMxClient  # noqa: E402


mcp = FastMCP("tenencia_mx")
_client = TenenciaMxClient()


class CalcularInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: str = Field(..., min_length=2, max_length=10, description="Clave estado (edomex, jal, nl, qro, etc.)")
    valor_factura: float = Field(..., ge=0, description="Valor original del vehículo (MXN).")
    anio_modelo: int = Field(..., ge=1970, le=2030, description="Año del modelo.")
    anio_actual: int = Field(2026, ge=2020, le=2030, description="Año del cálculo.")


class InfoEstadoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: str = Field(..., min_length=2, max_length=10)


class ListarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    solo_con_tenencia: bool = Field(False)


class CompararInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estados: list[str] = Field(..., min_length=2, max_length=20)
    valor_factura: float = Field(..., ge=0)
    anio_modelo: int = Field(..., ge=1970, le=2030)


@mcp.tool(annotations={"title": "Calcular tenencia + refrendo vehicular", "readOnlyHint": True, "idempotentHint": True})
def tenencia_calcular(args: CalcularInput) -> dict:
    """Calcula tenencia + refrendo proyectado para un estado mexicano."""
    return _client.calcular(
        estado=args.estado,
        valor_factura=args.valor_factura,
        anio_modelo=args.anio_modelo,
        anio_actual=args.anio_actual,
    )


@mcp.tool(annotations={"title": "Info detallada de tenencia por estado", "readOnlyHint": True, "idempotentHint": True})
def tenencia_info_estado(args: InfoEstadoInput) -> dict:
    """Devuelve configuración completa de un estado."""
    return _client.info_estado(args.estado)


@mcp.tool(annotations={"title": "Listar estados con tenencia/refrendo", "readOnlyHint": True, "idempotentHint": True})
def tenencia_listar_estados(args: ListarInput) -> dict:
    """Lista todos los estados del catálogo (o solo los con tenencia)."""
    return _client.listar_estados(solo_con_tenencia=args.solo_con_tenencia)


@mcp.tool(annotations={"title": "Comparar tenencia entre N estados", "readOnlyHint": True, "idempotentHint": True})
def tenencia_comparar_estados(args: CompararInput) -> dict:
    """Compara costo tenencia + refrendo entre N estados para un mismo vehículo.

    Útil para flotillas decidiendo dónde emplacar — devuelve ranking barato a caro.
    """
    return _client.comparar_estados(
        estados_claves=args.estados,
        valor_factura=args.valor_factura,
        anio_modelo=args.anio_modelo,
    )


if __name__ == "__main__":
    mcp.run()
