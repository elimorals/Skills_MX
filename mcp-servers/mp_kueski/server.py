"""MCP server mp_kueski."""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_kueski.client import KueskiClient  # noqa: E402

mcp = FastMCP("kueski_mcp")
_client = KueskiClient()


@mcp.tool()
def kueski_listar_pagos(**kwargs) -> dict:
    """listar_pagos (mock-first)."""
    return _client.listar_pagos(**kwargs)

@mcp.tool()
def kueski_consultar_pago(**kwargs) -> dict:
    """consultar_pago (mock-first)."""
    return _client.consultar_pago(**kwargs)

@mcp.tool()
def kueski_cancelar_pago(**kwargs) -> dict:
    """cancelar_pago (mock-first)."""
    return _client.cancelar_pago(**kwargs)


if __name__ == "__main__":
    mcp.run()
