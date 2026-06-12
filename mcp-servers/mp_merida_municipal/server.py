"""MCP server mp_merida_municipal."""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_merida_municipal.client import MeridaMunClient  # noqa: E402

mcp = FastMCP("merida_mun_mcp")
_client = MeridaMunClient()


@mcp.tool()
def merida_mun_consultar_multas(**kwargs) -> dict:
    """consultar_multas (mock-first)."""
    return _client.consultar_multas(**kwargs)

@mcp.tool()
def merida_mun_consultar_predial(**kwargs) -> dict:
    """consultar_predial (mock-first)."""
    return _client.consultar_predial(**kwargs)


if __name__ == "__main__":
    mcp.run()
