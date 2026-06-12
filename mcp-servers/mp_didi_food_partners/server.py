"""MCP server DiDi Food Partners."""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_didi_food_partners.client import DidiFoodPartnersClient  # noqa: E402

mcp = FastMCP("didi_food_partners_mcp")
_client = DidiFoodPartnersClient()


@mcp.tool()
def didi_food_listar_ordenes(estado: str = "all", limite: int = 20) -> dict:
    return _client.listar_ordenes(estado=estado, limite=limite)


@mcp.tool()
def didi_food_consultar_orden(orden_id: str) -> dict:
    return _client.consultar_orden(orden_id)


@mcp.tool()
def didi_food_listar_productos_menu() -> dict:
    return _client.listar_productos_menu()


@mcp.tool()
def didi_food_actualizar_disponibilidad(sku: str, disponible: bool) -> dict:
    return _client.actualizar_disponibilidad(sku=sku, disponible=disponible)


@mcp.tool()
def didi_food_consultar_ranking_zona() -> dict:
    return _client.consultar_ranking_zona()


@mcp.tool()
def didi_food_estimar_comisiones_mes(mes: str | None = None) -> dict:
    return _client.estimar_comisiones_mes(mes=mes)


if __name__ == "__main__":
    mcp.run()
