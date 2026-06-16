"""mp_citas_monitor MCP — monitor ético de cupos gob.mx."""
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

from mp_citas_monitor.client import CitasMonitorClient  # noqa: E402


mcp = FastMCP("citas_monitor")
_client = CitasMonitorClient()


class ConsentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    titular_curp: str = Field(..., min_length=18, max_length=18)
    titular_rfc: Optional[str] = Field(None, min_length=12, max_length=13)
    portal_clave: Literal["sat_citas", "imss_citas", "sre_mexitel", "ine_modulos"]
    tramite: str = Field(..., min_length=3, max_length=80)
    ttl_dias: int = Field(30, ge=1, le=60)


class AlertaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    consent_token: str = Field(..., min_length=8, max_length=40)
    canal: Literal["whatsapp", "email", "sms", "webhook"]
    destinatario: str = Field(..., min_length=3, max_length=200)
    entidad_preferida: Optional[str] = Field(None, max_length=100)
    fecha_min: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    fecha_max: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")


class RevisarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    portal_clave: Literal["sat_citas", "imss_citas", "sre_mexitel", "ine_modulos"]
    tramite: str = Field(..., min_length=3, max_length=80)


@mcp.tool(annotations={"title": "Listar portales de citas soportados", "readOnlyHint": True, "idempotentHint": True})
def citas_listar_portales() -> dict:
    return _client.listar_portales()


@mcp.tool(annotations={"title": "Generar consent_token del titular (LFPDPPP)", "readOnlyHint": False})
def citas_generar_consent_token(args: ConsentInput) -> dict:
    return _client.generar_consent_token(
        args.titular_curp,
        args.titular_rfc,
        args.portal_clave,
        args.tramite,
        ttl_dias=args.ttl_dias,
    )


@mcp.tool(annotations={"title": "Crear alerta (notifica al titular, NO reserva)", "readOnlyHint": False})
def citas_crear_alerta(args: AlertaInput) -> dict:
    return _client.crear_alerta(
        args.consent_token,
        args.canal,
        args.destinatario,
        entidad_preferida=args.entidad_preferida,
        fecha_min=args.fecha_min,
        fecha_max=args.fecha_max,
    )


@mcp.tool(annotations={"title": "Revisar cupos sin titular (Playwright opt-in)", "readOnlyHint": True})
def citas_revisar_cupos(args: RevisarInput) -> dict:
    return _client.revisar_cupos(args.portal_clave, args.tramite)


@mcp.tool(annotations={"title": "Estadísticas operación ética (auditoría)", "readOnlyHint": True, "idempotentHint": True})
def citas_estadisticas_eticas() -> dict:
    return _client.estadisticas_eticas()


if __name__ == "__main__":
    mcp.run()
