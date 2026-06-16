"""mp_llave_mx_tracker MCP — adopción Llave MX por dependencia (federal+estatal)."""
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

from mp_llave_mx_tracker.client import LlaveMxTrackerClient  # noqa: E402


mcp = FastMCP("llave_mx_tracker")
_client = LlaveMxTrackerClient()


class NivelInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nivel: Optional[Literal["federal", "federal_autonomo", "estatal"]] = None


class ClaveInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    clave: str = Field(..., min_length=2, max_length=30)


@mcp.tool(annotations={"title": "Listar dependencias monitoreadas", "readOnlyHint": True})
def llave_mx_listar_dependencias(args: NivelInput) -> dict:
    return _client.listar_dependencias(nivel=args.nivel)


@mcp.tool(annotations={"title": "Estatus de una dependencia", "readOnlyHint": True})
def llave_mx_estatus_dependencia(args: ClaveInput) -> dict:
    return _client.estatus_dependencia(args.clave)


@mcp.tool(annotations={"title": "Estadísticas nacionales adopción", "readOnlyHint": True, "idempotentHint": True})
def llave_mx_estadisticas_nacionales() -> dict:
    return _client.estadisticas_nacionales()


@mcp.tool(annotations={"title": "Verificar adopción en vivo (Playwright opt-in)", "readOnlyHint": True})
def llave_mx_verificar_en_vivo(args: ClaveInput) -> dict:
    return _client.verificar_en_vivo(args.clave)


if __name__ == "__main__":
    mcp.run()
