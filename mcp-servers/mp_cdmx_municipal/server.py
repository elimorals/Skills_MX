"""mp_cdmx_municipal — MCP para portales CDMX (finanzas + semovi).

5 tools (mock-first):
- cdmx_consultar_predial
- cdmx_consultar_tenencia
- cdmx_consultar_multas
- cdmx_consultar_hoy_no_circula
- cdmx_listar_catalogos
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_cdmx_municipal.catalogos import (  # noqa: E402
    HOLOGRAMAS,
    HOY_NO_CIRCULA,
    PORTALES_CDMX,
    STATUS_PREDIAL,
    STATUS_TENENCIA,
    TIPO_MULTA,
)
from mp_cdmx_municipal.client import CdmxMunicipalClient  # noqa: E402
from shared.errors import McpError  # noqa: E402
from shared.playwright_stub import info_path_real  # noqa: E402


mcp = FastMCP("cdmx_municipal_mcp")
_client = CdmxMunicipalClient()


class PredialInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cuenta_predial: str = Field(..., min_length=5, max_length=30,
                                description="Cuenta predial CDMX (10 dígitos típicamente).")


class PlacaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    placa: str = Field(..., min_length=5, max_length=10,
                       description="Placa vehicular CDMX (ej. ABC-123-D).")


class FechaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fecha: str = Field(..., description="Fecha ISO YYYY-MM-DD.", min_length=10, max_length=10)


@mcp.tool(annotations={"title": "Consultar predial CDMX", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def cdmx_consultar_predial(args: PredialInput) -> dict:
    """Status del impuesto predial por cuenta. Mock por default."""
    try:
        return _client.consultar_predial(args.cuenta_predial)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Consultar tenencia vehicular CDMX", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def cdmx_consultar_tenencia(args: PlacaInput) -> dict:
    """Status tenencia por placa. CDMX subsidia 100% para vehículos < umbral."""
    try:
        return _client.consultar_tenencia(args.placa)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Consultar multas vehiculares CDMX (foto-infracciones + manuales)", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def cdmx_consultar_multas(args: PlacaInput) -> dict:
    """Lista todas las multas pendientes por placa."""
    try:
        return _client.consultar_multas(args.placa)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Calendario Hoy No Circula CDMX", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def cdmx_consultar_hoy_no_circula(args: FechaInput) -> dict:
    """Reglas del programa Hoy No Circula para una fecha + contingencias."""
    try:
        return _client.consultar_calendario_hoy_no_circula(args.fecha)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Catálogos CDMX: status, tipos multa, hologramas", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def cdmx_listar_catalogos() -> dict:
    """Discovery offline."""
    return {
        "portales_cdmx": PORTALES_CDMX,
        "status_predial": STATUS_PREDIAL,
        "status_tenencia": STATUS_TENENCIA,
        "tipo_multa": TIPO_MULTA,
        "hoy_no_circula": HOY_NO_CIRCULA,
        "hologramas": HOLOGRAMAS,
        "path_real_info": info_path_real(),
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
