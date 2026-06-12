"""MCP server mp_telmex_facturacion."""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_telmex_facturacion.client import TelmexFactClient  # noqa: E402

mcp = FastMCP("telmex_fact_mcp")
_client = TelmexFactClient()


@mcp.tool()
def telmex_fact_descargar_factura_mes(**kwargs) -> dict:
    """descargar_factura_mes (mock-first)."""
    return _client.descargar_factura_mes(**kwargs)

@mcp.tool()
def telmex_fact_listar_facturas(**kwargs) -> dict:
    """listar_facturas (mock-first)."""
    return _client.listar_facturas(**kwargs)


if __name__ == "__main__":
    mcp.run()
