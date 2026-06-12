"""mp_bancos_mx — MCP para portales bancarios mexicanos.

⚠ Path Playwright real NO implementado. Modo mock por default. Cada banco
requiere 60-100h de desarrollo de scraping + mantenimiento mensual.

4 tools:
- bancos_listar_soportados (discovery, sin red)
- bancos_descargar_estado_cuenta
- bancos_listar_movimientos
- bancos_verificar_pago_por_referencia
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_bancos_mx.catalogos import BANCOS_SOPORTADOS, TIPOS_MOVIMIENTO  # noqa: E402
from mp_bancos_mx.client import BancosMxClient  # noqa: E402
from shared.errors import McpError  # noqa: E402
from shared.playwright_stub import info_path_real  # noqa: E402


mcp = FastMCP("bancos_mx_mcp")
_client = BancosMxClient()


# Códigos bancarios soportados (literales para validación tipo)
BancoCode = Literal[
    "bbva", "banamex", "santander", "banorte", "hsbc",
    "banregio", "inbursa", "azteca", "scotiabank",
]


class EstadoCuentaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    banco: BancoCode
    cuenta: str = Field(..., min_length=4, max_length=30, description="Número de cuenta o CLABE.")
    ejercicio: int = Field(..., ge=2018, le=2100)
    mes: int = Field(..., ge=1, le=12)
    formato: Literal["pdf", "xls", "csv"] = "pdf"


class MovimientosInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    banco: BancoCode
    cuenta: str = Field(..., min_length=4, max_length=30)
    dias: int = Field(30, ge=1, le=365)


class VerificarPagoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    banco: BancoCode
    referencia: str = Field(..., min_length=1, max_length=50)
    monto: float = Field(..., gt=0)


@mcp.tool(
    annotations={
        "title": "Listar bancos soportados + estado del path real",
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def bancos_listar_soportados() -> dict:
    """Discovery: bancos soportados, métodos auth, share PyME, path real."""
    info = _client.listar_bancos_soportados()
    info["path_real_info"] = info_path_real()
    info["movimiento_tipos"] = TIPOS_MOVIMIENTO
    return info


@mcp.tool(
    annotations={
        "title": "Descargar estado de cuenta del periodo",
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def bancos_descargar_estado_cuenta(args: EstadoCuentaInput) -> dict:
    """Descarga estado de cuenta. Mock por default (sin credenciales)."""
    try:
        return _client.descargar_estado_cuenta(
            args.banco, args.cuenta, args.ejercicio, args.mes, args.formato
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Listar movimientos recientes de la cuenta",
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def bancos_listar_movimientos(args: MovimientosInput) -> dict:
    """Lista movimientos de los últimos N días (default 30)."""
    try:
        return _client.listar_movimientos(args.banco, args.cuenta, args.dias)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(
    annotations={
        "title": "Verificar si llegó un pago por referencia numérica",
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def bancos_verificar_pago_por_referencia(args: VerificarPagoInput) -> dict:
    """Busca un pago entrante por referencia + monto. Útil para conciliación."""
    try:
        return _client.verificar_pago_por_referencia(
            args.banco, args.referencia, args.monto
        )
    except McpError as exc:
        return exc.to_dict()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
