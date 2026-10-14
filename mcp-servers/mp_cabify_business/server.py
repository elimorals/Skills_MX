"""mp_cabify_business — MCP para Cabify Business (Ride-Hailing API v4)."""

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

from mp_cabify_business.catalogos import ESTADOS_VIAJE  # noqa: E402
from mp_cabify_business.client import CabifyBusinessClient  # noqa: E402
from shared.errors import McpError  # noqa: E402


mcp = FastMCP("cabify_business_mcp")
_client = CabifyBusinessClient()

Lat = Field(..., ge=-90, le=90)
Lon = Field(..., ge=-180, le=180)


class EstimarInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    requester_id: str = Field(..., min_length=1, description="ID del usuario de Cabify Business que pide el viaje")
    origen_lat: float = Lat
    origen_lon: float = Lon
    destino_lat: float = Lat
    destino_lon: float = Lon
    inicio: Optional[str] = Field(None, description="ISO 8601 para reservar; vacío = lo antes posible")


class PedirViajeInput(EstimarInput):
    product_id: str = Field(..., min_length=1, description="product.id devuelto por cabify_estimar")
    pasajero_nombre: str = Field(..., min_length=1, max_length=120)
    pasajero_movil_cc: str = Field("52", pattern=r"^\d{1,4}$")
    pasajero_movil_num: str = Field(..., pattern=r"^\d{6,15}$")
    pasajero_email: Optional[str] = None
    origen_direccion: Optional[str] = Field(None, max_length=300)
    destino_direccion: Optional[str] = Field(None, max_length=300)
    label_slug: Optional[str] = Field(None, description="Etiqueta/centro de costos configurado en Cabify")
    mensaje: Optional[str] = Field(None, max_length=300, description="Mensaje para el conductor")


class ViajeIdInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    journey_id: str = Field(..., min_length=1, max_length=80)


async def _seguro(coro) -> dict:
    try:
        return await coro
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Estimar precio de viaje", "readOnlyHint": True, "openWorldHint": True})
async def cabify_estimar(args: EstimarInput) -> dict:
    """Productos y precios disponibles en el origen. Obligatorio antes de cabify_pedir_viaje."""
    return await _seguro(_client.estimar(
        args.requester_id, (args.origen_lat, args.origen_lon), (args.destino_lat, args.destino_lon), args.inicio
    ))


@mcp.tool(annotations={"title": "Pedir viaje Cabify (genera cargo)", "readOnlyHint": False, "openWorldHint": True})
async def cabify_pedir_viaje(args: PedirViajeInput) -> dict:
    """Crea un viaje real con cargo a la cuenta de empresa. Confirma con el usuario antes de llamarlo."""
    rider = {
        "name": args.pasajero_nombre,
        "mobile": {"mobile_cc": args.pasajero_movil_cc, "mobile_num": args.pasajero_movil_num},
    }
    if args.pasajero_email:
        rider["email"] = args.pasajero_email
    return await _seguro(_client.pedir_viaje(
        args.requester_id, args.product_id,
        (args.origen_lat, args.origen_lon), (args.destino_lat, args.destino_lon), rider,
        inicio=args.inicio, origen_direccion=args.origen_direccion, destino_direccion=args.destino_direccion,
        label_slug=args.label_slug, mensaje=args.mensaje,
    ))


@mcp.tool(annotations={"title": "Detalle de viaje", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def cabify_consultar_viaje(args: ViajeIdInput) -> dict:
    """Paradas, totales, estado final y si terminó."""
    return await _seguro(_client.consultar_viaje(args.journey_id))


@mcp.tool(annotations={"title": "Estado en vivo del viaje", "readOnlyHint": True, "openWorldHint": True})
async def cabify_estado_viaje(args: ViajeIdInput) -> dict:
    """Conductor, vehículo y ruta mientras el viaje está activo."""
    return await _seguro(_client.estado_viaje(args.journey_id))


@mcp.tool(annotations={"title": "Cancelar viaje", "readOnlyHint": False, "destructiveHint": True, "openWorldHint": True})
async def cabify_cancelar_viaje(args: ViajeIdInput) -> dict:
    """Cancela; gratis antes de asignar conductor, después puede cobrar."""
    return await _seguro(_client.cancelar_viaje(args.journey_id))


@mcp.tool(annotations={"title": "Recibos del viaje", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def cabify_ventas_viaje(args: ViajeIdInput) -> dict:
    """Ventas (recibos con impuestos) del viaje; existen cuando el viaje pasa a `terminated`."""
    return await _seguro(_client.ventas_viaje(args.journey_id))


@mcp.tool(annotations={"title": "Catálogo de estados de viaje", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def cabify_listar_catalogos() -> dict:
    return {"estados_viaje": ESTADOS_VIAJE}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
