"""mp_cabify_business — MCP para Cabify Business (movilidad B2B)."""

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

from mp_cabify_business.catalogos import (  # noqa: E402
    CIUDADES_OPERATIVAS,
    PAYMENT_METHOD,
    RIDE_STATUS,
    TIPO_VEHICULO,
)
from mp_cabify_business.client import CabifyBusinessClient  # noqa: E402
from shared.errors import McpError  # noqa: E402


mcp = FastMCP("cabify_business_mcp")
_client = CabifyBusinessClient()


VehicleType = Literal["lite", "premium", "executive", "group"]


class ScheduleRideInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    passenger_email: str = Field(..., min_length=3, max_length=254)
    pickup_address: str = Field(..., min_length=5, max_length=300)
    destination_address: str = Field(..., min_length=5, max_length=300)
    pickup_datetime: str = Field(..., description="ISO 8601 datetime")
    vehicle_type: VehicleType = "lite"
    cost_center: Optional[str] = Field(None, description="Centro de costos para reporting")


class ListRidesInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fecha_desde: Optional[str] = None
    status: Optional[Literal[
        "scheduled", "searching_driver", "driver_assigned", "driver_arrived",
        "in_progress", "completed", "cancelled_by_user", "cancelled_by_driver", "no_show"
    ]] = None
    limit: int = Field(50, ge=1, le=200)


class RideIdInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ride_id: str = Field(..., min_length=1, max_length=80)


class CancelInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ride_id: str = Field(..., min_length=1, max_length=80)
    reason: Literal[
        "user_request", "driver_late", "wrong_pickup", "emergency", "other"
    ] = "user_request"


class InvoiceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mes: int = Field(..., ge=1, le=12)
    ejercicio: int = Field(..., ge=2018, le=2100)
    rfc_empresa: str = Field(..., min_length=12, max_length=13)


@mcp.tool(annotations={"title": "Agendar viaje Cabify Business", "readOnlyHint": False, "openWorldHint": True})
async def cabify_schedule_ride(args: ScheduleRideInput) -> dict:
    """Agenda viaje para empleado con centro de costos para reporting."""
    try:
        return await _client.schedule_ride(
            args.passenger_email, args.pickup_address,
            args.destination_address, args.pickup_datetime,
            args.vehicle_type, args.cost_center,
        )
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Listar viajes con filtros", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def cabify_list_rides(args: ListRidesInput) -> dict:
    try:
        return await _client.list_rides(args.fecha_desde, args.status, args.limit)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Detalle de viaje", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": True})
async def cabify_get_ride(args: RideIdInput) -> dict:
    try:
        return await _client.get_ride(args.ride_id)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Cancelar viaje agendado", "readOnlyHint": False, "destructiveHint": True, "openWorldHint": True})
async def cabify_cancel_ride(args: CancelInput) -> dict:
    """Cancela viaje. Cancellation fee aplica según reason."""
    try:
        return await _client.cancel_ride(args.ride_id, args.reason)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Generar factura mensual consolidada", "readOnlyHint": False, "openWorldHint": True})
async def cabify_generate_invoice(args: InvoiceInput) -> dict:
    """Genera CFDI consolidado del mes para empresa."""
    try:
        return await _client.generate_invoice(args.mes, args.ejercicio, args.rfc_empresa)
    except McpError as exc:
        return exc.to_dict()


@mcp.tool(annotations={"title": "Catálogos: vehículos, status, ciudades", "readOnlyHint": True, "idempotentHint": True, "openWorldHint": False})
async def cabify_listar_catalogos() -> dict:
    return {
        "tipo_vehiculo": TIPO_VEHICULO,
        "ride_status": RIDE_STATUS,
        "payment_method": PAYMENT_METHOD,
        "ciudades_operativas": CIUDADES_OPERATIVAS,
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
