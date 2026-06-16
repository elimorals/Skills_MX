"""mp_imss_continuidad MCP — adapter Continuidad Operativa IMSS."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_imss_continuidad.client import ImssContinuidadClient  # noqa: E402


mcp = FastMCP("imss_continuidad")
_client = ImssContinuidadClient()


class ClaveSistemaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    clave: str = Field(..., min_length=2, max_length=40)


class PeriodoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    periodo: str = Field(..., pattern=r"^\d{4}-\d{2}$")


@mcp.tool(annotations={"title": "Listar 8 sistemas sustantivos IMSS", "readOnlyHint": True, "idempotentHint": True})
def imss_continuidad_listar_sistemas() -> dict:
    return _client.listar_sistemas_sustantivos()


@mcp.tool(annotations={"title": "Health-check de sistema sustantivo", "readOnlyHint": True})
def imss_continuidad_health_check(args: ClaveSistemaInput) -> dict:
    return _client.health_check_sistema(args.clave)


@mcp.tool(annotations={"title": "Plan continuidad DR/BCP por sistema", "readOnlyHint": True})
def imss_continuidad_plan(args: ClaveSistemaInput) -> dict:
    return _client.plan_continuidad(args.clave)


@mcp.tool(annotations={"title": "Reporte ejecutivo mensual (formato licitación)", "readOnlyHint": True})
def imss_continuidad_reporte_ejecutivo(args: PeriodoInput) -> dict:
    return _client.reporte_ejecutivo(args.periodo)


if __name__ == "__main__":
    mcp.run()
