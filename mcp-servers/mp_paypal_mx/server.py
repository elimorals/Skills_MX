"""MCP server mp_paypal_mx."""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_paypal_mx.client import PaypalMxClient  # noqa: E402

mcp = FastMCP("paypal_mx_mcp")
_client = PaypalMxClient()


@mcp.tool()
def paypal_mx_listar_transacciones(**kwargs) -> dict:
    """listar_transacciones (mock-first)."""
    return _client.listar_transacciones(**kwargs)

@mcp.tool()
def paypal_mx_consultar_transaccion(**kwargs) -> dict:
    """consultar_transaccion (mock-first)."""
    return _client.consultar_transaccion(**kwargs)

@mcp.tool()
def paypal_mx_balance(**kwargs) -> dict:
    """balance (mock-first)."""
    return _client.balance(**kwargs)


if __name__ == "__main__":
    mcp.run()
