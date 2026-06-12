"""MCP server Uber Eats Partners."""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_uber_eats_partners.client import UberEatsPartnersClient  # noqa: E402

mcp = FastMCP("uber_eats_partners_mcp")
_client = UberEatsPartnersClient()


@mcp.tool()
def uber_eats_listar_ordenes(estado: str = "all", limite: int = 20) -> dict:
    return _client.listar_ordenes(estado=estado, limite=limite)


@mcp.tool()
def uber_eats_consultar_orden(orden_id: str) -> dict:
    return _client.consultar_orden(orden_id)


@mcp.tool()
def uber_eats_listar_productos_menu() -> dict:
    return _client.listar_productos_menu()


@mcp.tool()
def uber_eats_actualizar_disponibilidad(sku: str, disponible: bool) -> dict:
    return _client.actualizar_disponibilidad(sku=sku, disponible=disponible)


@mcp.tool()
def uber_eats_consultar_ranking_zona() -> dict:
    return _client.consultar_ranking_zona()


@mcp.tool()
def uber_eats_estimar_comisiones_mes(mes: str | None = None) -> dict:
    return _client.estimar_comisiones_mes(mes=mes)


if __name__ == "__main__":
    mcp.run()
