"""mp_resico_sat MCP."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_resico_sat.client import RESICOClient  # noqa: E402


mcp = FastMCP("resico_sat")
_client = RESICOClient()


class IngresoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ingreso_mes_mxn: float = Field(..., ge=0)


class EstatusInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rfc: str = Field(..., min_length=12, max_length=13)
    periodos_omitidos: int = Field(..., ge=0, le=12)
    declaracion_anual_presentada: bool = True
    ingresos_anuales_mxn: float = Field(..., ge=0)
    e_firma_vigente: bool = True


class CalendarioInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    anio: int = Field(..., ge=2020, le=2099)
    mes_actual: int = Field(..., ge=1, le=12)


class RetencionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    plataforma: str
    ingreso_bruto_mxn: float = Field(..., ge=0)


class DevolucionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rfc: str = Field(..., min_length=12, max_length=13)
    periodo: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    monto_solicitado_mxn: float = Field(..., gt=0)
    plataforma: str | None = None


@mcp.tool(annotations={"title": "Calcular ISR mensual RESICO", "readOnlyHint": True, "idempotentHint": True})
def resico_calcular_isr(args: IngresoInput) -> dict:
    return _client.calcular_isr_mes(ingreso_mes_mxn=args.ingreso_mes_mxn)


@mcp.tool(annotations={"title": "Evaluar estatus RESICO + riesgo expulsión", "readOnlyHint": True})
def resico_evaluar_estatus(args: EstatusInput) -> dict:
    return _client.evaluar_estatus(
        rfc=args.rfc, periodos_omitidos=args.periodos_omitidos,
        declaracion_anual_presentada=args.declaracion_anual_presentada,
        ingresos_anuales_mxn=args.ingresos_anuales_mxn,
        e_firma_vigente=args.e_firma_vigente,
    )


@mcp.tool(annotations={"title": "Calendario próximas 12 declaraciones", "readOnlyHint": True, "idempotentHint": True})
def resico_calendario(args: CalendarioInput) -> dict:
    return _client.calendario_declaraciones(anio=args.anio, mes_actual=args.mes_actual)


@mcp.tool(annotations={"title": "Calcular retención plataforma digital", "readOnlyHint": True, "idempotentHint": True})
def resico_retencion_plataforma(args: RetencionInput) -> dict:
    return _client.retencion_plataforma(plataforma=args.plataforma,
                                         ingreso_bruto_mxn=args.ingreso_bruto_mxn)


@mcp.tool(annotations={"title": "Solicitar devolución mensual retenciones", "readOnlyHint": True})
def resico_solicitar_devolucion(args: DevolucionInput) -> dict:
    return _client.solicitar_devolucion_mensual(
        rfc=args.rfc, periodo=args.periodo,
        monto_solicitado_mxn=args.monto_solicitado_mxn,
        plataforma=args.plataforma,
    )


@mcp.tool(annotations={"title": "Tasas RESICO 2026", "readOnlyHint": True, "idempotentHint": True})
def resico_listar_tasas() -> dict:
    return _client.listar_tasas()


@mcp.tool(annotations={"title": "Plataformas con retención", "readOnlyHint": True, "idempotentHint": True})
def resico_listar_plataformas() -> dict:
    return _client.listar_plataformas()


if __name__ == "__main__":
    mcp.run()
