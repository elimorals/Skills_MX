"""mp_portales_monitor MCP — monitor uptime portales gob.mx."""
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

from mp_portales_monitor.client import PortalesMonitorClient  # noqa: E402


mcp = FastMCP("portales_monitor")
_client = PortalesMonitorClient()


class CategoriaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    categoria: Optional[str] = Field(None, max_length=40)


class ClaveInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    clave: str = Field(..., min_length=2, max_length=40)


class FormRenderInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    clave: str = Field(..., min_length=2, max_length=40)
    selector: str = Field(..., min_length=1, max_length=200)


class AlertaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    clave: str = Field(..., min_length=2, max_length=40)
    canal: Literal["whatsapp", "email", "slack", "webhook_pagerduty"]
    destinatario: str = Field(..., min_length=3, max_length=200)
    umbral_latencia_ms: Optional[int] = Field(None, ge=100, le=60000)


@mcp.tool(annotations={"title": "Listar portales monitoreados", "readOnlyHint": True, "idempotentHint": True})
def portales_listar(args: CategoriaInput) -> dict:
    return _client.listar_portales(categoria=args.categoria)


@mcp.tool(annotations={"title": "Check HTTP de un portal", "readOnlyHint": True})
def portales_check_http(args: ClaveInput) -> dict:
    return _client.check_http(args.clave)


@mcp.tool(annotations={"title": "Verificar renderizado de selector (Playwright opt-in)", "readOnlyHint": True})
def portales_check_form_render(args: FormRenderInput) -> dict:
    return _client.check_form_render(args.clave, args.selector)


@mcp.tool(annotations={"title": "Dashboard health agregado", "readOnlyHint": True, "idempotentHint": True})
def portales_health_dashboard() -> dict:
    return _client.health_dashboard()


@mcp.tool(annotations={"title": "Configurar alerta para un portal", "readOnlyHint": False})
def portales_configurar_alerta(args: AlertaInput) -> dict:
    return _client.configurar_alerta(
        args.clave, args.canal, args.destinatario, args.umbral_latencia_ms
    )


if __name__ == "__main__":
    mcp.run()
