"""MCP server mp_queretaro_municipal."""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_queretaro_municipal.client import QueretaroMunClient  # noqa: E402

mcp = FastMCP("queretaro_mun_mcp")
_client = QueretaroMunClient()


@mcp.tool()
def queretaro_mun_consultar_multas(**kwargs) -> dict:
    """consultar_multas (mock-first)."""
    return _client.consultar_multas(**kwargs)

@mcp.tool()
def queretaro_mun_consultar_predial(**kwargs) -> dict:
    """consultar_predial (mock-first)."""
    return _client.consultar_predial(**kwargs)


if __name__ == "__main__":
    mcp.run()
