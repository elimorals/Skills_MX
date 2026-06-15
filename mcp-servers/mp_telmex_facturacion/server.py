"""MCP server mp_telmex_facturacion."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_telmex_facturacion.client import TelmexFactClient  # noqa: E402

mcp = FastMCP("telmex_fact_mcp")
_client = TelmexFactClient()


class FacturaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    telefono: str = Field(..., min_length=10, max_length=15)
    periodo: str = Field("", max_length=7, description="YYYY-MM o vacío para último")


class ConsumoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    telefono: str = Field(..., min_length=10, max_length=15)
    meses: int = Field(6, ge=1, le=24)


class TelefonoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    telefono: str = Field(..., min_length=10, max_length=15)


@mcp.tool(annotations={"title": "Descargar factura Telmex", "readOnlyHint": True, "openWorldHint": True})
def telmex_descargar_factura(args: FacturaInput) -> dict:
    """Descarga factura mensual (PDF + XML CFDI)."""
    return _client.descargar_factura_mes(args.telefono, args.periodo)


@mcp.tool(annotations={"title": "Consumo histórico Telmex", "readOnlyHint": True, "openWorldHint": True})
def telmex_consumo_historico(args: ConsumoInput) -> dict:
    """Consumos mensuales últimos N meses."""
    return _client.consumo_historico(args.telefono, args.meses)


@mcp.tool(annotations={"title": "Listar facturas disponibles", "readOnlyHint": True, "openWorldHint": True})
def telmex_listar_facturas(args: TelefonoInput) -> dict:
    """Periodos con factura disponible."""
    return _client.listar_facturas(args.telefono)


if __name__ == "__main__":
    mcp.run()
