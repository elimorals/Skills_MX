"""mp_vivanuncios — MCP para vivanuncios.com.mx (multi-categoría)."""

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

from mp_vivanuncios.catalogos import (  # noqa: E402
    CATEGORIAS_VIVANUNCIOS,
    DIFERENCIAS_VS_INMUEBLES24,
    STATUS_ANUNCIO,
    TIPO_PUBLICACION,
)
from mp_vivanuncios.client import VivanunciosClient  # noqa: E402
from shared.errors import McpError  # noqa: E402
from shared.playwright_stub import info_path_real  # noqa: E402


mcp = FastMCP("vivanuncios_mcp")
_client = VivanunciosClient()


Categoria = Literal[
    "inmuebles", "vehiculos", "empleos", "servicios", "electronica",
    "hogar", "moda_belleza", "deportes", "negocios_industriales", "mascotas",
]


class BuscarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    categoria: Categoria
    query: str = Field(..., min_length=2, max_length=100)
    ciudad: str = Field(..., min_length=2, max_length=100)
    limit: int = Field(10, ge=1, le=50)


class IdInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id_anuncio: str = Field(..., min_length=3, max_length=80)


class PublicarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    titulo: str = Field(..., min_length=10, max_length=80)
    categoria: Categoria
    precio_mxn: float = Field(..., gt=0)


@mcp.tool(annotations={"title": "Buscar anuncios Vivanuncios", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def viv_buscar_anuncios(args: BuscarInput) -> dict:
    """Búsqueda multi-categoría (autos, inmuebles, empleos, etc.)."""
    try:
        return _client.buscar_anuncios(
            args.categoria, args.query, args.ciudad, args.limit
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Detalle de anuncio por ID", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def viv_obtener_detalle(args: IdInput) -> dict:
    """Detalle completo: vendedor, fotos, métricas."""
    try:
        return _client.obtener_detalle(args.id_anuncio)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Publicar anuncio nuevo (requiere cuenta)", "readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True})
async def viv_publicar_anuncio(args: PublicarInput) -> dict:
    """Crea anuncio. Va a moderación 1-4 hrs antes de visible."""
    try:
        return _client.publicar_anuncio(args.titulo, args.categoria, args.precio_mxn)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Catálogos Vivanuncios: categorías, tipos pub, diferencias vs Inmuebles24", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def viv_listar_catalogos() -> dict:
    return {
        "categorias": CATEGORIAS_VIVANUNCIOS,
        "tipo_publicacion": TIPO_PUBLICACION,
        "status_anuncio": STATUS_ANUNCIO,
        "diferencias_vs_inmuebles24": DIFERENCIAS_VS_INMUEBLES24,
        "path_real_info": info_path_real(),
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
