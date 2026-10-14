"""mp_llave_mx MCP."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_llave_mx.client import LlaveMXClient  # noqa: E402


mcp = FastMCP("llave_mx")
_client = LlaveMXClient()


class OAuthInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    redirect_url: str = Field(..., description="URL https registrada con la ATDT")
    state: str | None = None


class AdopcionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entidad: str | None = Field(None, description="Nombre o cve_ent; vacío = nacional")


class TokenInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: str


class ListarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    categoria: str | None = None
    dependencia: str | None = None


class ClaveInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    clave: str


class CurpOnlyInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    curp: str = Field(..., min_length=18, max_length=18)


@mcp.tool(annotations={"title": "URL de autorización OAuth Llave MX", "readOnlyHint": True})
def llave_iniciar_oauth(args: OAuthInput) -> dict:
    return _client.iniciar_oauth(redirect_url=args.redirect_url, state=args.state)


@mcp.tool(annotations={"title": "Estado de llave.gob.mx", "readOnlyHint": True, "openWorldHint": True})
def llave_estado_endpoints() -> dict:
    return _client.estado_endpoints()


@mcp.tool(annotations={"title": "Altas de usuarios Llave MX (datos abiertos)", "readOnlyHint": True,
                       "openWorldHint": True})
def llave_estadisticas_adopcion(args: AdopcionInput) -> dict:
    return _client.estadisticas_adopcion(entidad=args.entidad)


@mcp.tool(annotations={"title": "Validar token Llave MX", "readOnlyHint": True})
def llave_validar_token(args: TokenInput) -> dict:
    return _client.validar_token(token=args.token)


@mcp.tool(annotations={"title": "Listar trámites disponibles", "readOnlyHint": True, "idempotentHint": True})
def llave_listar_tramites(args: ListarInput) -> dict:
    return _client.listar_tramites(categoria=args.categoria, dependencia=args.dependencia)


@mcp.tool(annotations={"title": "Detalle trámite", "readOnlyHint": True, "idempotentHint": True})
def llave_detalle_tramite(args: ClaveInput) -> dict:
    return _client.detalle_tramite(clave=args.clave)


@mcp.tool(annotations={"title": "Vincular e.firma (handoff)", "readOnlyHint": True})
def llave_vincular_e_firma(args: CurpOnlyInput) -> dict:
    return _client.vincular_e_firma(curp=args.curp)


if __name__ == "__main__":
    mcp.run()
