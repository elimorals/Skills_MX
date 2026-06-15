"""mp_concilianet_profeco MCP."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_concilianet_profeco.client import ConcilianetClient  # noqa: E402


mcp = FastMCP("concilianet")
_client = ConcilianetClient()


class ProveedorInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    razon_social: str = Field(..., min_length=3)


class FolioInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    folio: str = Field(..., min_length=6)


class QuejaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    consumidor_curp_hash: str | None = None
    proveedor: str = Field(..., min_length=3)
    descripcion: str = Field(..., min_length=20)
    monto_reclamado_mxn: float | None = None


@mcp.tool(annotations={"title": "Consultar proveedor convenio", "readOnlyHint": True})
def concilianet_consultar_proveedor(args: ProveedorInput) -> dict:
    return _client.consultar_proveedor(razon_social=args.razon_social)


@mcp.tool(annotations={"title": "Estatus caso conciliación", "readOnlyHint": True})
def concilianet_estatus_caso(args: FolioInput) -> dict:
    return _client.estatus_caso(folio=args.folio)


@mcp.tool(annotations={"title": "Listar proveedores convenio", "readOnlyHint": True, "idempotentHint": True})
def concilianet_listar_proveedores() -> dict:
    return _client.listar_proveedores_convenio()


@mcp.tool(annotations={"title": "Registrar queja PROFECO", "readOnlyHint": True})
def concilianet_registrar_queja(args: QuejaInput) -> dict:
    return _client.registrar_queja(
        consumidor_curp_hash=args.consumidor_curp_hash, proveedor=args.proveedor,
        descripcion=args.descripcion, monto_reclamado_mxn=args.monto_reclamado_mxn,
    )


if __name__ == "__main__":
    mcp.run()
