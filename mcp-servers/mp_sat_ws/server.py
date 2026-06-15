"""mp_sat_ws — MCP standalone para SAT WS Descarga Masiva CFDI."""
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

from mp_sat_ws.client import SatWsClient  # noqa: E402
from shared.sat_ws import SolicitudDescarga  # noqa: E402


mcp = FastMCP("sat_ws")
_client = SatWsClient()


class SolicitarDescargaInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rfc_emisor: str = Field(..., min_length=12, max_length=13)
    fecha_inicial: str = Field(..., description="ISO YYYY-MM-DDTHH:MM:SS")
    fecha_final: str = Field(..., description="ISO YYYY-MM-DDTHH:MM:SS")
    tipo_solicitud: str = Field("CFDI", pattern="^(CFDI|Metadata)$")
    tipo_comprobante: Optional[str] = Field(None, pattern="^[IETPN]$")
    rfc_receptor: str = Field("", max_length=13)


class VerificarSolicitudInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id_solicitud: str = Field(..., min_length=8)
    rfc_emisor: str = Field(..., min_length=12, max_length=13)


class DescargarPaqueteInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id_paquete: str = Field(..., min_length=8)
    rfc_emisor: str = Field(..., min_length=12, max_length=13)


@mcp.tool(annotations={"title": "Solicitar descarga masiva CFDI al SAT", "readOnlyHint": False, "openWorldHint": True})
def sat_ws_solicitar_descarga(args: SolicitarDescargaInput) -> dict:
    """Inicia solicitud de descarga masiva. Devuelve id_solicitud."""
    sol = SolicitudDescarga(
        rfc_emisor=args.rfc_emisor,
        fecha_inicial=args.fecha_inicial,
        fecha_final=args.fecha_final,
        tipo_solicitud=args.tipo_solicitud,  # type: ignore[arg-type]
        tipo_comprobante=args.tipo_comprobante,  # type: ignore[arg-type]
        rfc_receptor=args.rfc_receptor,
    )
    return _client.solicitar_descarga(sol)


@mcp.tool(annotations={"title": "Verificar estado de solicitud SAT WS", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
def sat_ws_verificar_solicitud(args: VerificarSolicitudInput) -> dict:
    """Polling del estado de la solicitud. cod_estatus_solicitud == 3 = TERMINADA."""
    return _client.verificar_solicitud(args.id_solicitud, args.rfc_emisor)


@mcp.tool(annotations={"title": "Descargar paquete ZIP con CFDIs", "readOnlyHint": True, "openWorldHint": True})
def sat_ws_descargar_paquete(args: DescargarPaqueteInput) -> dict:
    """Descarga un paquete ZIP del SAT (cuando estado=TERMINADA)."""
    return _client.descargar_paquete(args.id_paquete, args.rfc_emisor)


if __name__ == "__main__":
    mcp.run()
