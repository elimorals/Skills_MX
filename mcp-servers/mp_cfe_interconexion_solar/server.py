"""mp_cfe_interconexion_solar MCP."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_cfe_interconexion_solar.client import CFEInterconexionClient  # noqa: E402


mcp = FastMCP("cfe_interconexion_solar")
_client = CFEInterconexionClient()


class SolicitarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rpu: str = Field(..., min_length=6, max_length=16)
    kw_instalados: float = Field(..., gt=0, le=500)
    tarifa_actual: str
    tipo_sistema: str = "fotovoltaico"
    tension: str = "baja"


class FolioInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    folio: str


class SimularInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tarifa_actual: str
    kwh_consumo_promedio_mensual: float = Field(..., ge=0)
    kwh_generacion_solar_estimada: float = Field(..., ge=0)


@mcp.tool(annotations={"title": "Solicitar interconexión solar CFE", "readOnlyHint": True})
def cfe_solar_solicitar(args: SolicitarInput) -> dict:
    return _client.solicitar_interconexion(
        rpu=args.rpu, kw_instalados=args.kw_instalados,
        tarifa_actual=args.tarifa_actual, tipo_sistema=args.tipo_sistema,
        tension=args.tension,
    )


@mcp.tool(annotations={"title": "Consultar estatus solicitud interconexión", "readOnlyHint": True})
def cfe_solar_estatus(args: FolioInput) -> dict:
    return _client.consultar_estatus_solicitud(folio=args.folio)


@mcp.tool(annotations={"title": "Simular ahorro prosumidor", "readOnlyHint": True, "idempotentHint": True})
def cfe_solar_simular_ahorro(args: SimularInput) -> dict:
    return _client.simular_ahorro_prosumidor(
        tarifa_actual=args.tarifa_actual,
        kwh_consumo_promedio_mensual=args.kwh_consumo_promedio_mensual,
        kwh_generacion_solar_estimada=args.kwh_generacion_solar_estimada,
    )


@mcp.tool(annotations={"title": "Listar tarifas CFE prosumidor", "readOnlyHint": True, "idempotentHint": True})
def cfe_solar_listar_tarifas() -> dict:
    return _client.listar_tarifas()


if __name__ == "__main__":
    mcp.run()
