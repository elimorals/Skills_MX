"""mp_monterrey_municipal — 4 tools mock-first."""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_monterrey_municipal.catalogos import (  # noqa: E402
    MUNICIPIOS_AMM,
    PORTALES_NL,
    TIPO_RESTRICCION_NL,
)
from mp_monterrey_municipal.client import MonterreyMunicipalClient  # noqa: E402
from shared.errors import McpError  # noqa: E402
from shared.playwright_stub import info_path_real  # noqa: E402


mcp = FastMCP("monterrey_municipal_mcp")
_client = MonterreyMunicipalClient()


class PredialInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    municipio: str = Field(..., min_length=2, max_length=50,
                          description="Municipio del Área Metropolitana de Monterrey.")
    cuenta_predial: str = Field(..., min_length=3, max_length=30)


class PlacaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    placa: str = Field(..., min_length=5, max_length=10)


class FechaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fecha: str = Field(..., min_length=10, max_length=10)


@mcp.tool(annotations={"title": "Consultar predial Monterrey/NL", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def nl_consultar_predial(args: PredialInput) -> dict:
    """Predial municipal del AMM. Cada municipio tiene portal propio."""
    try:
        return _client.consultar_predial(args.municipio, args.cuenta_predial)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Consultar multas tránsito Nuevo León", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def nl_consultar_multas(args: PlacaInput) -> dict:
    """Multas de tránsito NL."""
    try:
        return _client.consultar_multas(args.placa)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Calidad aire NL + status contingencia Aire Limpio", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def nl_consultar_calidad_aire(args: FechaInput) -> dict:
    """IMECA + fase de contingencia (Aire Limpio) si activa."""
    try:
        return _client.consultar_calidad_aire_nl(args.fecha)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Catálogos NL: municipios, contingencias", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def nl_listar_catalogos() -> dict:
    return {
        "portales_nl": PORTALES_NL,
        "municipios_amm": MUNICIPIOS_AMM,
        "tipo_restriccion_nl": TIPO_RESTRICCION_NL,
        "path_real_info": info_path_real(),
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
