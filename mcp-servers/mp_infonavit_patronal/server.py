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
