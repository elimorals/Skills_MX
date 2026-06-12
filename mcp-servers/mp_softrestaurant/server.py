"""mp_softrestaurant — MCP para Soft Restaurant POS (MX).

⚠ Soft Restaurant es POS LOCAL en SQL Server, sin API REST pública.
Este MCP parsea exports CSV desde Soft Restaurant.

8 tools (mock-first):
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_softrestaurant.catalogos import (  # noqa: E402
    CATEGORIAS_MENU,
    ESTATUS_MESA,
    METODOS_EXPORT,
    METODOS_PAGO_SR,
    TIPOS_OPERACION,
)
from mp_softrestaurant.client import SoftRestaurantClient  # noqa: E402
from shared.errors import McpError  # noqa: E402


mcp = FastMCP("softrestaurant_mcp")
_client = SoftRestaurantClient()


class FechaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fecha: str = Field(..., min_length=10, max_length=10, description="YYYY-MM-DD")


class PeriodoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    desde: str = Field(..., min_length=10, max_length=10)
    hasta: str = Field(..., min_length=10, max_length=10)


class PeriodoSimpleInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    periodo: str = Field(..., min_length=4, max_length=20,
                          description="ej. '2026-03' o '2026-Q1'")


class ParsearInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tipo: Literal["corte_z", "ventas_periodo", "platillos_vendidos"]
    contenido_csv: str = Field(..., min_length=1, max_length=10_000_000)


@mcp.tool(annotations={"title": "Corte Z del día (totales por método pago + categoría)", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def softrest_corte_z(args: FechaInput) -> dict:
    """Corte Z: totales del día por método de pago, categoría, propinas, cancelaciones."""
    try:
        return _client.corte_z_del_dia(args.fecha)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Ventas detalladas en periodo", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def softrest_ventas_periodo(args: PeriodoInput) -> dict:
    try:
        return _client.ventas_periodo(args.desde, args.hasta)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Inventario actual con alertas bajo stock", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def softrest_inventario_actual() -> dict:
    try:
        return _client.inventario_actual()
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Platillos más/menos vendidos (ingeniería de menú)", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def softrest_platillos_vendidos(args: PeriodoSimpleInput) -> dict:
    """Top 5 + bottom 5 por cantidad. Útil para ingeniería de menú."""
    try:
        return _client.platillos_vendidos(args.periodo)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Ventas y propinas por mesero", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def softrest_meseros_ventas(args: FechaInput) -> dict:
    try:
        return _client.meseros_ventas(args.fecha)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Estatus en tiempo real de mesas", "readOnlyHint": True, "idempotentHint": False, "openWorldHint": True})
async def softrest_mesas_estatus() -> dict:
    """Mesas libres, ocupadas, con orden, reservadas. Requiere conexión SQL Server (real) o mock."""
    try:
        return _client.mesas_estatus()
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Parsear CSV de export Soft Restaurant (utility local)", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def softrest_parsear_export(args: ParsearInput) -> dict:
    """Parsea contenido CSV inline. Tipos: corte_z, ventas_periodo, platillos_vendidos."""
    try:
        return _client.parsear_export(args.tipo, args.contenido_csv)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Catálogos: tipos operación, mesas, categorías menú, métodos pago", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def softrest_listar_catalogos() -> dict:
    return {
        "tipos_operacion": TIPOS_OPERACION,
        "estatus_mesa": ESTATUS_MESA,
        "categorias_menu": CATEGORIAS_MENU,
        "metodos_pago": METODOS_PAGO_SR,
        "metodos_export": METODOS_EXPORT,
        "nota": "Soft Restaurant no tiene API REST. Configurar SOFT_RESTAURANT_EXPORTS_DIR con CSV exports.",
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
