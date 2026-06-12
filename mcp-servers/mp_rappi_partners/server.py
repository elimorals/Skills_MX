"""MCP server para Rappi Partners."""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_rappi_partners.client import RappiPartnersClient  # noqa: E402

mcp = FastMCP("rappi_partners_mcp")
_client = RappiPartnersClient()


@mcp.tool()
def rappi_listar_ordenes(estado: str = "all", limite: int = 20) -> dict:
    """Lista órdenes recientes del comercio."""
    return _client.listar_ordenes(estado=estado, limite=limite)


@mcp.tool()
def rappi_consultar_orden(orden_id: str) -> dict:
    """Detalle de una orden específica."""
    return _client.consultar_orden(orden_id)


@mcp.tool()
def rappi_listar_productos_menu() -> dict:
    """Lista productos del menú del comercio."""
    return _client.listar_productos_menu()


@mcp.tool()
def rappi_actualizar_disponibilidad(sku: str, disponible: bool) -> dict:
    """Marca/desmarca un producto como disponible."""
    return _client.actualizar_disponibilidad(sku=sku, disponible=disponible)


@mcp.tool()
def rappi_consultar_ranking_zona() -> dict:
    """Posición del comercio en su zona vs competencia."""
    return _client.consultar_ranking_zona()


@mcp.tool()
def rappi_estimar_comisiones_mes(mes: str | None = None) -> dict:
    """Estimación de comisiones del mes (gross, comisión Rappi 30%, neto)."""
    return _client.estimar_comisiones_mes(mes=mes)


if __name__ == "__main__":
    mcp.run()
