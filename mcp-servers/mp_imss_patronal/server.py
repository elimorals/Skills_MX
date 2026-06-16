"""mp_imss_patronal — MCP para IMSS IDSE (Desde su Empresa).

6 tools (mock-first):
- imss_consultar_avisos_pendientes
- imss_enviar_movimiento_afiliatorio (alta, baja, modificación, reingreso)
- imss_descargar_cedula_autodeterminacion
- imss_consultar_emcr (Emisión Mensual Cédula Reposicionada)
- imss_consultar_sbc (Salario Diario Integrado)
- imss_consultar_padron_trabajadores
- imss_listar_catalogos

⚠ Auth real requiere e.firma o tarjeta NPIE. No implementado todavía.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_imss_patronal.catalogos import (  # noqa: E402
    CAUSA_BAJA,
    CLASE_RIESGO,
    CONCEPTOS_CEDULA,
    LIMITES_SBC,
    STATUS_TRABAJADOR,
    TIPO_SALARIO,
    TIPOS_MOVIMIENTO_AFILIATORIO,
)
from mp_imss_patronal.client import ImssPatronalClient  # noqa: E402
from shared.errors import McpError  # noqa: E402
from shared.playwright_stub import info_path_real  # noqa: E402


mcp = FastMCP("imss_patronal_mcp")
_client = ImssPatronalClient()


class RegistroInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    registro_patronal: str = Field(..., min_length=8, max_length=15,
                                    description="Registro patronal IMSS (11 chars típicamente).")


class MovimientoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    registro_patronal: str = Field(..., min_length=8, max_length=15)
    nss: str = Field(..., min_length=10, max_length=15,
                     description="Número de Seguridad Social (11 dígitos).")
    tipo_movimiento: Literal["08", "02", "07", "11", "09", "01"] = Field(
        ..., description="08=Alta, 02=Baja, 07=Modificación, 11=Cambio, 09=Incapacidad, 01=Reingreso"
    )
    salario_diario: Optional[float] = Field(None, gt=0, description="Requerido para alta (08).")
    causa_baja: Optional[Literal[
        "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13"
    ]] = Field(None, description="Requerido para baja (02).")


class CedulaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    registro_patronal: str = Field(..., min_length=8, max_length=15)
    bimestre: int = Field(..., ge=1, le=6)
    ejercicio: int = Field(..., ge=2018, le=2100)


class EmcrInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    registro_patronal: str = Field(..., min_length=8, max_length=15)
    mes: int = Field(..., ge=1, le=12)
    ejercicio: int = Field(..., ge=2018, le=2100)


class SbcInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    registro_patronal: str = Field(..., min_length=8, max_length=15)
    nss: str = Field(..., min_length=10, max_length=15)


@mcp.tool(annotations={"title": "Avisos pendientes IMSS", "readOnlyHint": True, "idempotentHint": False, "openWorldHint": True})
async def imss_consultar_avisos_pendientes(args: RegistroInput) -> dict:
    """Notificaciones pendientes del IMSS para el registro patronal."""
    try:
        return _client.consultar_avisos_pendientes(args.registro_patronal)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Enviar movimiento afiliatorio (alta/baja/modif)", "readOnlyHint": False, "destructiveHint": True, "openWorldHint": True})
async def imss_enviar_movimiento_afiliatorio(args: MovimientoInput) -> dict:
    """Procesa alta, baja, modificación de SBC o reingreso de trabajador.

    Operación crítica: cambia padrón del trabajador en IMSS.
    """
    try:
        return _client.enviar_movimiento_afiliatorio(
            args.registro_patronal,
            args.nss,
            args.tipo_movimiento,
            salario_diario=args.salario_diario,
            causa_baja=args.causa_baja,
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Cédula autodeterminación bimestral", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def imss_descargar_cedula_autodeterminacion(args: CedulaInput) -> dict:
    """Cédula bimestral con cuotas obrero-patronales + INFONAVIT + retiro."""
    try:
        return _client.descargar_cedula_autodeterminacion(
            args.registro_patronal, args.bimestre, args.ejercicio
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "EMCR (Emisión Mensual Cédula Reposicionada)", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def imss_consultar_emcr(args: EmcrInput) -> dict:
    """EMCR mensual."""
    try:
        return _client.consultar_emcr(args.registro_patronal, args.mes, args.ejercicio)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Salario Diario Integrado de un trabajador", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def imss_consultar_sbc(args: SbcInput) -> dict:
    """Consulta SBC del trabajador (salario + factor integración)."""
    try:
        return _client.consultar_salario_diario_integrado(
            args.registro_patronal, args.nss
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Padrón trabajadores del registro patronal", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def imss_consultar_padron_trabajadores(args: RegistroInput) -> dict:
    """Lista trabajadores activos con SBC y status."""
    try:
        return _client.consultar_padron_trabajadores(args.registro_patronal)
    except McpError as exc:
        return exc.to_dict()


# ---------- Sprint F: profundización ----------


class SbcCalcularInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    salario_diario_base: float = Field(..., gt=0, le=100000, description="Salario diario base MXN.")
    bono_anual_mxn: float = Field(0.0, ge=0)
    dias_aguinaldo: int = Field(15, ge=15, le=60)
    dias_prima_vacacional: int = Field(6, ge=0, le=100, description="% prima vacacional (default 25%).")
    otras_percepciones_anuales_mxn: float = Field(0.0, ge=0)


class EmaEbaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    registro_patronal: str = Field(..., min_length=8, max_length=15)
    periodo: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="YYYY-MM")


class CalendarioObligacionesInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    giro: str = Field("comercio", min_length=1, max_length=50)
    clase_riesgo: Literal["I", "II", "III", "IV", "V"] = Field("I")


class SimuladorCostoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    salario_diario_base: float = Field(..., gt=0, le=100000)
    bono_anual_mxn: float = Field(0.0, ge=0)
    clase_riesgo: Literal["I", "II", "III", "IV", "V"] = Field("I")


class PrimaRiesgoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prima_actual: float = Field(..., gt=0, lt=0.20, description="Prima vigente como decimal (ej 0.025 = 2.5%).")
    s_dias_subsidiados: int = Field(0, ge=0)
    n_total_trabajadores: int = Field(..., gt=0)
    v_casos_invalidez: int = Field(0, ge=0)
    i_casos_incapacidad_permanente_parcial: float = Field(0.0, ge=0)
    d_casos_defuncion: int = Field(0, ge=0)


@mcp.tool(annotations={"title": "Calcular SBC con factor integración + tope UMAs 2026", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def imss_sbc_calcular(args: SbcCalcularInput) -> dict:
    """Auto-cálculo SBC (Art. 27 LSS) con UMA 2026 ($113.07).

    Tope: 25 UMAs diarias = $2,826.75. Local, sin red.
    """
    try:
        return _client.sbc_calcular(
            args.salario_diario_base,
            bono_anual_mxn=args.bono_anual_mxn,
            dias_aguinaldo=args.dias_aguinaldo,
            dias_prima_vacacional=args.dias_prima_vacacional,
            otras_percepciones_anuales_mxn=args.otras_percepciones_anuales_mxn,
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Diferencias EMA (Empresa) vs EBA (Banco)", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def imss_ema_vs_eba_diferencias(args: EmaEbaInput) -> dict:
    """Compara cédula EMA vs comprobante bancario EBA (Art. 39-A LSS).

    Detecta diferencias cuotas, movimientos no aplicados, intereses por mora.
    """
    try:
        return _client.ema_vs_eba_diferencias(args.registro_patronal, args.periodo)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Calendario obligaciones IMSS por giro y clase de riesgo", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def imss_calendario_obligaciones(args: CalendarioObligacionesInput) -> dict:
    """Calendario anual: mensuales (cuotas), bimestrales (INFONAVIT+RCV), anual (RT).

    Local. Fechas día 17 del mes/bimestre siguiente.
    """
    try:
        return _client.calendario_obligaciones(args.giro, args.clase_riesgo)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Simulador costo patronal mensual + anual por colaborador", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def imss_simulador_costo_patronal(args: SimuladorCostoInput) -> dict:
    """Costo total patronal: salario + IMSS + INFONAVIT + provisiones LFT.

    Devuelve factor_costo_sobre_salario — utilidad para presupuestos.
    """
    try:
        return _client.simulador_costo_patronal(
            args.salario_diario_base,
            bono_anual_mxn=args.bono_anual_mxn,
            clase_riesgo=args.clase_riesgo,
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Proyección prima Riesgo de Trabajo siguiente año (Art. 72 LSS)", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def imss_riesgo_trabajo_prima_cambio(args: PrimaRiesgoInput) -> dict:
    """Calcula prima RT siguiente año con fórmula oficial IMSS.

    Aplica tope ±1% (Art. 74 LSS). Fecha límite: 28 feb año siguiente.
    """
    try:
        return _client.riesgo_trabajo_prima_cambio(
            args.prima_actual,
            s_dias_subsidiados=args.s_dias_subsidiados,
            n_total_trabajadores=args.n_total_trabajadores,
            v_casos_invalidez=args.v_casos_invalidez,
            i_casos_incapacidad_permanente_parcial=args.i_casos_incapacidad_permanente_parcial,
            d_casos_defuncion=args.d_casos_defuncion,
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Catálogos IMSS: tipos movimiento, causas baja, riesgo", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def imss_listar_catalogos() -> dict:
    """Discovery: catálogos completos IMSS."""
    return {
        "tipos_movimiento_afiliatorio": TIPOS_MOVIMIENTO_AFILIATORIO,
        "causa_baja": CAUSA_BAJA,
        "conceptos_cedula": CONCEPTOS_CEDULA,
        "status_trabajador": STATUS_TRABAJADOR,
        "tipo_salario": TIPO_SALARIO,
        "limites_sbc": LIMITES_SBC,
        "clase_riesgo": CLASE_RIESGO,
        "path_real_info": info_path_real(),
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
