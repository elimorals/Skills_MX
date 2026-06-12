"""mp_edomex_municipal — 4 tools mock-first."""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_edomex_municipal.catalogos import (  # noqa: E402
    HOY_NO_CIRCULA_EDOMEX,
    MUNICIPIOS_PREDIAL_DIGITAL,
    PORTALES_EDOMEX,
    STATUS_TENENCIA_EDOMEX,
)
from mp_edomex_municipal.client import EdomexMunicipalClient  # noqa: E402
from shared.errors import McpError  # noqa: E402
from shared.playwright_stub import info_path_real  # noqa: E402


mcp = FastMCP("edomex_municipal_mcp")
_client = EdomexMunicipalClient()


class PredialInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    municipio: str = Field(..., min_length=2, max_length=50)
    cuenta_predial: str = Field(..., min_length=3, max_length=30)


class TenenciaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    placa: str = Field(..., min_length=5, max_length=10)
    ejercicio: int = Field(..., ge=2018, le=2100)


class PlacaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    placa: str = Field(..., min_length=5, max_length=10)


@mcp.tool(annotations={"title": "Consultar predial EdoMex (por municipio)", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def edomex_consultar_predial(args: PredialInput) -> dict:
    """Predial EdoMex — cada municipio tiene su propio portal."""
    try:
        return _client.consultar_predial(args.municipio, args.cuenta_predial)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Consultar tenencia EdoMex", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def edomex_consultar_tenencia(args: TenenciaInput) -> dict:
    """⚠ EdoMex sí cobra tenencia (CDMX subsidia). Verificar antes del 31-mar."""
    try:
        return _client.consultar_tenencia(args.placa, args.ejercicio)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Consultar multas EdoMex", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def edomex_consultar_multas(args: PlacaInput) -> dict:
    """Multas de tránsito EdoMex (carreteras + zona conurbada)."""
    try:
        return _client.consultar_multas(args.placa)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Catálogos EdoMex: municipios, tenencia, hoy no circula", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def edomex_listar_catalogos() -> dict:
    return {
        "portales": PORTALES_EDOMEX,
        "status_tenencia": STATUS_TENENCIA_EDOMEX,
        "municipios_predial_digital": MUNICIPIOS_PREDIAL_DIGITAL,
        "hoy_no_circula": HOY_NO_CIRCULA_EDOMEX,
        "path_real_info": info_path_real(),
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
