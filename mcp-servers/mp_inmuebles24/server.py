"""mp_inmuebles24 — MCP para inmuebles24.com."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_inmuebles24.catalogos import (  # noqa: E402
    ESTADOS_TOP_INVENTARIO,
    PLANES_PUBLICACION,
    STATUS_LISTING,
    TIPO_INMUEBLE,
    TIPO_OPERACION,
)
from mp_inmuebles24.client import Inmuebles24Client  # noqa: E402
from shared.errors import McpError  # noqa: E402
from shared.playwright_stub import info_path_real  # noqa: E402


mcp = FastMCP("inmuebles24_mcp")
_client = Inmuebles24Client()


class BuscarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tipo_operacion: Literal["venta", "renta", "renta_temporal", "traspaso"]
    tipo_inmueble: Literal[
        "casa", "departamento", "ph", "loft", "terreno", "oficina",
        "local_comercial", "bodega", "edificio", "hotel", "quinta"
    ]
    ciudad: str = Field(..., min_length=2, max_length=100)
    precio_min: Optional[float] = Field(None, ge=0)
    precio_max: Optional[float] = Field(None, ge=0)
    limit: int = Field(10, ge=1, le=50)


class IdInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id_inmueble: str = Field(..., min_length=3, max_length=80)


class ComparablesInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ubicacion: str = Field(..., min_length=2, max_length=100)
    tipo_inmueble: Literal[
        "casa", "departamento", "ph", "loft", "terreno", "oficina",
        "local_comercial", "bodega", "edificio", "hotel", "quinta"
    ]
    metros_min: int = Field(50, ge=10)
    metros_max: int = Field(500, ge=10)


class PublicarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    titulo: str = Field(..., min_length=10, max_length=80)
    precio_mxn: float = Field(..., gt=0)
    tipo_operacion: Literal["venta", "renta", "renta_temporal", "traspaso"]
    tipo_inmueble: Literal[
        "casa", "departamento", "ph", "loft", "terreno", "oficina",
        "local_comercial", "bodega", "edificio", "hotel", "quinta"
    ]


@mcp.tool(annotations={"title": "Buscar inmuebles en inmuebles24", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def inm24_buscar_inmuebles(args: BuscarInput) -> dict:
    """Búsqueda con filtros. Mock retorna 3 resultados demo."""
    try:
        return _client.buscar_inmuebles(
            args.tipo_operacion, args.tipo_inmueble, args.ciudad,
            args.precio_min, args.precio_max, args.limit,
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Detalle de inmueble por ID", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def inm24_obtener_detalle(args: IdInput) -> dict:
    """Detalle completo: fotos, amenidades, vistas, contactos."""
    try:
        return _client.obtener_detalle(args.id_inmueble)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Comparables de zona (precios y precio/m²)", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def inm24_buscar_comparables_zona(args: ComparablesInput) -> dict:
    """Estadísticas de precio en una zona específica. Útil para pricing."""
    try:
        return _client.buscar_comparables_zona(
            args.ubicacion, args.tipo_inmueble, args.metros_min, args.metros_max,
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Publicar listing nuevo (requiere cuenta vendedor)", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True})
async def inm24_publicar_listing(args: PublicarInput) -> dict:
    """Crea borrador de listing. Activar publicación consume crédito del plan."""
    try:
        return _client.publicar_listing(
            args.titulo, args.precio_mxn, args.tipo_operacion, args.tipo_inmueble,
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Catálogos Inmuebles24: tipos, planes, estados", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def inm24_listar_catalogos() -> dict:
    return {
        "tipo_operacion": TIPO_OPERACION,
        "tipo_inmueble": TIPO_INMUEBLE,
        "estados_top_inventario": ESTADOS_TOP_INVENTARIO,
        "status_listing": STATUS_LISTING,
        "planes_publicacion": PLANES_PUBLICACION,
        "path_real_info": info_path_real(),
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
