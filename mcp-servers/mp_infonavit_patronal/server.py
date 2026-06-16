"""mp_infonavit_patronal — MCP para INFONAVIT (SUA / Portal Empresarial).

5 tools (mock-first):
- infonavit_consultar_creditos_trabajadores
- infonavit_descargar_emis (Emisión Mensual)
- infonavit_consultar_descuentos_mensuales (por trabajador)
- infonavit_consultar_avisos_pendientes
- infonavit_listar_catalogos
"""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_infonavit_patronal.catalogos import (  # noqa: E402
    CONCEPTOS_EMIS,
    PRODUCTOS_CREDITO,
    STATUS_CREDITO,
    TIPOS_AVISO_PATRONAL,
    TIPOS_DESCUENTO,
)
from mp_infonavit_patronal.client import InfonavitPatronalClient  # noqa: E402
from shared.errors import McpError  # noqa: E402
from shared.playwright_stub import info_path_real  # noqa: E402


mcp = FastMCP("infonavit_patronal_mcp")
_client = InfonavitPatronalClient()


class RegistroInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    registro_patronal: str = Field(..., min_length=8, max_length=15)


class EmisInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    registro_patronal: str = Field(..., min_length=8, max_length=15)
    mes: int = Field(..., ge=1, le=12)
    ejercicio: int = Field(..., ge=2018, le=2100)


class DescuentoTrabajadorInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    registro_patronal: str = Field(..., min_length=8, max_length=15)
    nss: str = Field(..., min_length=10, max_length=15)
    mes: int = Field(..., ge=1, le=12)
    ejercicio: int = Field(..., ge=2018, le=2100)


@mcp.tool(annotations={"title": "Créditos vigentes de los trabajadores", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def infonavit_consultar_creditos_trabajadores(args: RegistroInput) -> dict:
    """Lista créditos vigentes de los trabajadores del patrón."""
    try:
        return _client.consultar_creditos_trabajadores(args.registro_patronal)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "EMIS — Emisión Mensual Infonavit", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def infonavit_descargar_emis(args: EmisInput) -> dict:
    """EMIS del mes: total a pagar + detalle por trabajador."""
    try:
        return _client.descargar_emis(
            args.registro_patronal, args.mes, args.ejercicio
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Descuento Infonavit de un trabajador específico", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def infonavit_consultar_descuentos_mensuales(args: DescuentoTrabajadorInput) -> dict:
    """Detalle del descuento de un trabajador específico."""
    try:
        return _client.consultar_descuentos_mensuales(
            args.registro_patronal, args.nss, args.mes, args.ejercicio
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Avisos pendientes Infonavit (altas, bajas, requerimientos)", "readOnlyHint": True, "idempotentHint": False, "openWorldHint": True})
async def infonavit_consultar_avisos_pendientes(args: RegistroInput) -> dict:
    """Notificaciones pendientes del portal patronal."""
    try:
        return _client.consultar_avisos_pendientes(args.registro_patronal)
    except McpError as exc:
        return exc.to_dict()


# ---------- Sprint F: profundización ----------


from typing import Any as _Any, Literal as _Literal, Optional as _Optional  # noqa: E402


class DescuentoCalcularInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sbc_diario_mxn: float = Field(..., gt=0, le=100000)
    credito_tipo: _Literal[
        "PESOS_NORMAL", "VSM_NORMAL", "CUOTA_FIJA_PESOS",
        "REESTRUCTURADO_VSM", "OMISIONES_PASIVAS",
    ] = Field(...)
    factor_o_monto: _Optional[float] = Field(None, ge=0, description="Factor (0.05-0.30) o monto fijo MXN según tipo.")
    dias_mes: int = Field(30, ge=28, le=31)


class CreditosSinReporteInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    registro_patronal: str = Field(..., min_length=8, max_length=15)


class EmisHistoricoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    registro_patronal: str = Field(..., min_length=8, max_length=15)
    anios: int = Field(3, ge=1, le=10)


class DescuentoItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nss: str = Field(..., min_length=1, max_length=20)
    monto_mxn: float = Field(..., ge=0)
    periodo: str = Field(..., pattern=r"^\d{4}-\d{2}$")


class ConciliacionNominaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    registro_patronal: str = Field(..., min_length=8, max_length=15)
    descuentos_nomina: list[DescuentoItem] = Field(..., min_length=1, max_length=5000)


@mcp.tool(annotations={"title": "Calcular descuento INFONAVIT por trabajador", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def infonavit_descuento_calcular(args: DescuentoCalcularInput) -> dict:
    """Auto-cálculo descuento mensual INFONAVIT por trabajador.

    Soporta 5 tipos de crédito (Art. 29 LFINFONAVIT). Aplica cap LFT Art. 110 (30% SBC).
    """
    try:
        return _client.descuento_calcular(
            args.sbc_diario_mxn,
            args.credito_tipo,
            args.factor_o_monto,
            args.dias_mes,
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Créditos sin reporte en nómina (riesgo intereses moratorios)", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def infonavit_creditos_sin_reporte(args: CreditosSinReporteInput) -> dict:
    """Detecta créditos INFONAVIT activos NO aplicados en nómina.

    Calcula intereses moratorios estimados (~1.8%/mes). Crítico para liquidaciones.
    """
    try:
        return _client.creditos_sin_reporte(args.registro_patronal)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "EMIS histórico por bimestre y año", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def infonavit_emis_historico(args: EmisHistoricoInput) -> dict:
    """Histórico EMIS bimestral hasta 10 años. Útil para auditorías, juicios."""
    try:
        return _client.emis_historico(args.registro_patronal, args.anios)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Conciliación nómina vs INFONAVIT (cruzada)", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def infonavit_conciliacion_nomina(args: ConciliacionNominaInput) -> dict:
    """Compara descuentos en nómina vs cuotas esperadas por INFONAVIT.

    Devuelve diferencias por trabajador + acción recomendada. Acepta hasta 5000 registros.
    """
    try:
        descuentos = [d.model_dump() for d in args.descuentos_nomina]
        return _client.conciliacion_nomina(args.registro_patronal, descuentos)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Catálogos Infonavit: tipos descuento, status crédito, productos", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def infonavit_listar_catalogos() -> dict:
    """Discovery offline."""
    return {
        "tipos_descuento": TIPOS_DESCUENTO,
        "status_credito": STATUS_CREDITO,
        "conceptos_emis": CONCEPTOS_EMIS,
        "tipos_aviso_patronal": TIPOS_AVISO_PATRONAL,
        "productos_credito": PRODUCTOS_CREDITO,
        "path_real_info": info_path_real(),
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
