"""MCP server mp_clabe_validador_oficial."""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_clabe_validador_oficial.client import ClabeValidadorClient  # noqa: E402

mcp = FastMCP("clabe_validador_mcp")
_client = ClabeValidadorClient()


@mcp.tool()
def clabe_validador_validar_clabe(**kwargs) -> dict:
    """validar_clabe (mock-first)."""
    return _client.validar_clabe(**kwargs)

@mcp.tool()
def clabe_validador_info_banco_clabe(**kwargs) -> dict:
    """info_banco_clabe (mock-first)."""
    return _client.info_banco_clabe(**kwargs)


if __name__ == "__main__":
    mcp.run()
