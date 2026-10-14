"""mp_monterrey_municipal — predial AMM (real: Monterrey)."""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_monterrey_municipal.catalogos import MUNICIPIOS_AMM, PREDIAL_REAL  # noqa: E402
from mp_monterrey_municipal.client import MonterreyMunicipalClient  # noqa: E402
from shared.errors import McpError  # noqa: E402


mcp = FastMCP("monterrey_municipal_mcp")
_client = MonterreyMunicipalClient()


class PredialInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    municipio: str = Field(..., min_length=2, max_length=50,
                           description="Municipio del Área Metropolitana de Monterrey.")
    cuenta_predial: str = Field(..., min_length=3, max_length=30,
                                description="Expediente catastral (Monterrey: 8 dígitos).")


@mcp.tool(annotations={"title": "Consultar predial Monterrey/NL", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def nl_consultar_predial(args: PredialInput) -> dict:
    """Adeudo de predial. Real para Monterrey; otros municipios del AMM devuelven error explícito."""
    try:
        return _client.consultar_predial(args.municipio, args.cuenta_predial)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Catálogos NL: municipios AMM", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def nl_listar_catalogos() -> dict:
    return {"municipios_amm": MUNICIPIOS_AMM, "predial_real": PREDIAL_REAL}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
