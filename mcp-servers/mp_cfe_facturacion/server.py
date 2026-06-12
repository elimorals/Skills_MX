"""MCP server mp_cfe_facturacion."""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_cfe_facturacion.client import CfeFactClient  # noqa: E402

mcp = FastMCP("cfe_fact_mcp")
_client = CfeFactClient()


@mcp.tool()
def cfe_fact_descargar_factura_mes(**kwargs) -> dict:
    """descargar_factura_mes (mock-first)."""
    return _client.descargar_factura_mes(**kwargs)

@mcp.tool()
def cfe_fact_consumo_historico(**kwargs) -> dict:
    """consumo_historico (mock-first)."""
    return _client.consumo_historico(**kwargs)


if __name__ == "__main__":
    mcp.run()
