"""MCP server mp_klap."""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_klap.client import KlapClient  # noqa: E402

mcp = FastMCP("klap_mcp")
_client = KlapClient()


@mcp.tool()
def klap_listar_pagos(**kwargs) -> dict:
    """listar_pagos (mock-first)."""
    return _client.listar_pagos(**kwargs)

@mcp.tool()
def klap_consultar_pago(**kwargs) -> dict:
    """consultar_pago (mock-first)."""
    return _client.consultar_pago(**kwargs)


if __name__ == "__main__":
    mcp.run()
