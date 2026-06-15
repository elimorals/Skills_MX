"""mp_verificacion_vehicular_mx — MCP."""
from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_verificacion_vehicular_mx.client import VerificacionVehicularClient  # noqa: E402


mcp = FastMCP("verificacion_vehicular_mx")
_client = VerificacionVehicularClient()


class ConsultarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    placa: str = Field(..., min_length=5, max_length=12)
    estado: str = Field(..., min_length=2, max_length=10)


class ProximoPeriodoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    placa: str = Field(..., min_length=5, max_length=12)
    estado: str = Field("cdmx", min_length=2, max_length=10)


@mcp.tool(annotations={"title": "Consultar verificación vehicular", "readOnlyHint": True, "openWorldHint": True})
def verificacion_consultar_estatus(args: ConsultarInput) -> dict:
    """Consulta estatus del holograma + vigencia."""
    return _client.consultar_estatus(args.placa, args.estado)


@mcp.tool(annotations={"title": "Próximo periodo de verificación", "readOnlyHint": True, "idempotentHint": True})
def verificacion_proximo_periodo(args: ProximoPeriodoInput) -> dict:
    """Calcula color de engomado + próximo mes de verificación obligatoria."""
    return _client.proximo_periodo(args.placa, args.estado)


@mcp.tool(annotations={"title": "Listar programas estatales", "readOnlyHint": True, "idempotentHint": True})
def verificacion_listar_programas() -> dict:
    """Lista programas de verificación por estado."""
    return _client.listar_programas()


if __name__ == "__main__":
    mcp.run()
