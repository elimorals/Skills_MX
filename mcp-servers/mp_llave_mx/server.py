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


class AutInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    curp: str = Field(..., min_length=18, max_length=18)
    password: str = Field(..., min_length=6)


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


@mcp.tool(annotations={"title": "Autenticar Llave MX", "readOnlyHint": True, "openWorldHint": True})
def llave_autenticar(args: AutInput) -> dict:
    return _client.autenticar(curp=args.curp, password=args.password)


@mcp.tool(annotations={"title": "Validar token Llave MX", "readOnlyHint": True})
def llave_validar_token(args: TokenInput) -> dict:
    return _client.validar_token(token=args.token)


@mcp.tool(annotations={"title": "Listar trámites disponibles", "readOnlyHint": True, "idempotentHint": True})
def llave_listar_tramites(args: ListarInput) -> dict:
    return _client.listar_tramites(categoria=args.categoria, dependencia=args.dependencia)


@mcp.tool(annotations={"title": "Detalle trámite", "readOnlyHint": True, "idempotentHint": True})
def llave_detalle_tramite(args: ClaveInput) -> dict:
    return _client.detalle_tramite(clave=args.clave)


@mcp.tool(annotations={"title": "Vincular e.firma a Llave MX", "readOnlyHint": True})
def llave_vincular_e_firma(args: CurpOnlyInput) -> dict:
    return _client.vincular_e_firma(curp=args.curp)


if __name__ == "__main__":
    mcp.run()
