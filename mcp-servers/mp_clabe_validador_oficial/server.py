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
from shared.errors import McpError  # noqa: E402

mcp = FastMCP("clabe_validador_mcp")
_client = ClabeValidadorClient()


@mcp.tool()
def clabe_validador_validar_clabe(clabe: str) -> dict:
    """Valida una CLABE: dígito de control oficial + banco participante SPEI vigente (Banxico)."""
    try:
        return _client.validar_clabe(clabe)
    except McpError as e:
        return e.to_dict()


@mcp.tool()
def clabe_validador_info_banco_clabe(codigo_o_clabe: str) -> dict:
    """Institución SPEI vigente para un código de banco (3 dígitos) o una CLABE (18)."""
    try:
        return _client.info_banco_clabe(codigo_o_clabe)
    except McpError as e:
        return e.to_dict()


if __name__ == "__main__":
    mcp.run()
