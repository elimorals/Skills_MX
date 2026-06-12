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
