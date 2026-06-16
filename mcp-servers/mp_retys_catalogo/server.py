"""mp_retys_catalogo MCP — Catálogo Nacional CONAMER + exportador DCAT datos.gob.mx."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_retys_catalogo.client import RetysCatalogoClient  # noqa: E402


mcp = FastMCP("retys_catalogo")
_client = RetysCatalogoClient()


class BuscarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    q: str = Field(..., min_length=2, max_length=200)
    sector: Optional[str] = Field(None, max_length=50)


class HomoclaveInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    homoclave: str = Field(..., min_length=3, max_length=50)


class QueryInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    q: str = Field(..., min_length=2, max_length=200)


@mcp.tool(annotations={"title": "Listar sectores CONAMER", "readOnlyHint": True, "idempotentHint": True})
def retys_listar_sectores() -> dict:
    return _client.listar_sectores()


@mcp.tool(annotations={"title": "Buscar trámite por texto + sector", "readOnlyHint": True})
def retys_buscar_tramite(args: BuscarInput) -> dict:
    return _client.buscar_tramite(args.q, sector=args.sector)


@mcp.tool(annotations={"title": "Detalle trámite por homoclave", "readOnlyHint": True})
def retys_detalle_tramite(args: HomoclaveInput) -> dict:
    return _client.detalle_tramite(args.homoclave)


@mcp.tool(annotations={"title": "Exportar catálogo en DCAT (datos.gob.mx)", "readOnlyHint": True, "idempotentHint": True})
def retys_exportar_dcat() -> dict:
    return _client.exportar_dcat()


@mcp.tool(annotations={"title": "Buscar en vivo CONAMER (Playwright opt-in)", "readOnlyHint": True})
def retys_buscar_en_vivo(args: QueryInput) -> dict:
    return _client.buscar_en_vivo(args.q)


if __name__ == "__main__":
    mcp.run()
