"""MCP server mp_didi_partners."""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_didi_partners.client import DidiPartnersClient  # noqa: E402

mcp = FastMCP("didi_partners_mcp")
_client = DidiPartnersClient()


@mcp.tool()
def didi_partners_listar_viajes(**kwargs) -> dict:
    """listar_viajes (mock-first)."""
    return _client.listar_viajes(**kwargs)

@mcp.tool()
def didi_partners_consultar_viaje(**kwargs) -> dict:
    """consultar_viaje (mock-first)."""
    return _client.consultar_viaje(**kwargs)

@mcp.tool()
def didi_partners_comisiones_mes(**kwargs) -> dict:
    """comisiones_mes (mock-first)."""
    return _client.comisiones_mes(**kwargs)


if __name__ == "__main__":
    mcp.run()
