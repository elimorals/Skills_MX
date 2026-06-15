"""mp_cre_hidrocarburos MCP."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_cre_hidrocarburos.client import CREClient  # noqa: E402


mcp = FastMCP("cre_hidrocarburos")
_client = CREClient()


class IdInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    identificador: str = Field(..., min_length=4)


class CalendInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    anio: int = Field(..., ge=2020, le=2099)
    mes_actual: int = Field(..., ge=1, le=12)


class Anexo30Input(BaseModel):
    model_config = ConfigDict(extra="forbid")
    litros_mes_max: float = Field(..., ge=0)
    tiene_permiso_cre: bool = False


class ZerosInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    num_permiso: str
    periodo: str = Field(..., pattern=r"^\d{4}-\d{2}$")


@mcp.tool(annotations={"title": "Consultar permiso CRE", "readOnlyHint": True})
def cre_consultar_permiso(args: IdInput) -> dict:
    return _client.consultar_permiso(identificador=args.identificador)


@mcp.tool(annotations={"title": "Calendar reporte mensual CRE", "readOnlyHint": True, "idempotentHint": True})
def cre_calendar_reporte(args: CalendInput) -> dict:
    return _client.calendar_reporte_mensual(anio=args.anio, mes_actual=args.mes_actual)


@mcp.tool(annotations={"title": "Evaluar aplicación Anexo 30 SAT", "readOnlyHint": True, "idempotentHint": True})
def cre_evaluar_anexo30(args: Anexo30Input) -> dict:
    return _client.evaluar_anexo30(litros_mes_max=args.litros_mes_max,
                                     tiene_permiso_cre=args.tiene_permiso_cre)


@mcp.tool(annotations={"title": "Reportar ceros (sin actividad)", "readOnlyHint": True})
def cre_reportar_zeros(args: ZerosInput) -> dict:
    return _client.reportar_zeros(num_permiso=args.num_permiso, periodo=args.periodo)


@mcp.tool(annotations={"title": "Listar tipos de permiso", "readOnlyHint": True, "idempotentHint": True})
def cre_listar_tipos_permiso() -> dict:
    return _client.listar_tipos_permiso()


if __name__ == "__main__":
    mcp.run()
