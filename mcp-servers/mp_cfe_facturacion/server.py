"""MCP server mp_cfe_facturacion — Playwright + human-in-loop CAPTCHA."""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_cfe_facturacion.client import CfeFactClient  # noqa: E402


mcp = FastMCP("cfe_fact")
_client = CfeFactClient()


class DescargarFacturaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rpu: str = Field(..., min_length=6, max_length=16, description="Registro Permanente Único (12 dígitos típicamente).")
    periodo: str = Field("", description="Opcional YYYY-MM. Default: último mes.")


class ConsumoHistoricoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rpu: str = Field(..., min_length=6, max_length=16)
    meses: int = Field(12, ge=1, le=24, description="Cantidad de meses históricos (1-24).")


class ValidarSessionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rpu: str = Field(..., min_length=6, max_length=16)


@mcp.tool(annotations={"title": "Descargar factura CFE del mes", "readOnlyHint": True, "openWorldHint": True})
def cfe_descargar_factura_mes(args: DescargarFacturaInput) -> dict:
    """Descarga el recibo CFE Mi Espacio del periodo solicitado."""
    return _client.descargar_factura_mes(rpu=args.rpu, periodo=args.periodo)


@mcp.tool(annotations={"title": "Histórico de consumo CFE", "readOnlyHint": True, "openWorldHint": True})
def cfe_consumo_historico(args: ConsumoHistoricoInput) -> dict:
    """Histórico mensual de consumo kWh + detección de anomalías."""
    return _client.consumo_historico(rpu=args.rpu, meses=args.meses)


@mcp.tool(annotations={"title": "Validar sesión CFE cacheada", "readOnlyHint": True, "idempotentHint": True})
def cfe_validar_session(args: ValidarSessionInput) -> dict:
    """Verifica si hay sesión cacheada válida para un RPU (evita re-login)."""
    return _client.validar_session(rpu=args.rpu)


if __name__ == "__main__":
    mcp.run()
