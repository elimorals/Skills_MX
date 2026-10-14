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
def paypal_mx_listar_transacciones(
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
    pagina: int = 1,
    tamano_pagina: int = 100,
) -> dict:
    """Lista transacciones de PayPal (máx. 31 días por consulta; por defecto los últimos 31)."""
    return _client.listar_transacciones(fecha_inicio, fecha_fin, pagina, tamano_pagina)


@mcp.tool()
def paypal_mx_consultar_transaccion(
    transaction_id: str,
    fecha_inicio: str | None = None,
    fecha_fin: str | None = None,
) -> dict:
    """Detalle de una transacción por ID dentro del rango dado (por defecto, últimos 31 días)."""
    return _client.consultar_transaccion(transaction_id, fecha_inicio, fecha_fin)


@mcp.tool()
def paypal_mx_balance(moneda: str | None = None, al_momento: str | None = None) -> dict:
    """Saldos de la cuenta PayPal por moneda (total, disponible y retenido)."""
    return _client.balance(moneda, al_momento)


if __name__ == "__main__":
    mcp.run()
