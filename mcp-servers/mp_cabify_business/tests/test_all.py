"""Tests mp_cabify_business."""

from __future__ import annotations

import pytest

from mp_cabify_business.client import CabifyBusinessClient
from mp_cabify_business.server import (
    CancelInput,
    InvoiceInput,
    ListRidesInput,
    RideIdInput,
    ScheduleRideInput,
    cabify_cancel_ride,
    cabify_generate_invoice,
    cabify_get_ride,
    cabify_list_rides,
    cabify_listar_catalogos,
    cabify_schedule_ride,
)


@pytest.fixture
def client() -> CabifyBusinessClient:
    return CabifyBusinessClient()


def test_default_mock(client: CabifyBusinessClient) -> None:
    assert client.is_mock is True


@pytest.mark.asyncio
async def test_schedule_ride(client: CabifyBusinessClient) -> None:
    r = await client.schedule_ride(
        passenger_email="demo@example.mx",
        pickup_address="Av. Insurgentes 1234",
        destination_address="Aeropuerto T1",
        pickup_datetime="2026-04-15T08:00:00Z",
        vehicle_type="premium",
        cost_center="MKT-2026",
    )
    assert r["simulated"] is True
    assert r["status"] == "scheduled"
    assert r["vehicle_type"] == "premium"
    # email no en claro
    assert "demo@example.mx" not in str(r)


@pytest.mark.asyncio
async def test_list_rides(client: CabifyBusinessClient) -> None:
    r = await client.list_rides(status="completed", limit=10)
    assert "rides" in r


@pytest.mark.asyncio
async def test_get_ride(client: CabifyBusinessClient) -> None:
    r = await client.get_ride("cabify_ride_xyz")
    assert r["status"] == "completed"
    assert r["price_mxn"] > 0


@pytest.mark.asyncio
async def test_cancel_ride(client: CabifyBusinessClient) -> None:
    r = await client.cancel_ride("cabify_ride_xyz", reason="emergency")
    assert r["status"] == "cancelled_by_user"


@pytest.mark.asyncio
async def test_cancel_driver_late_sin_fee(client: CabifyBusinessClient) -> None:
    r = await client.cancel_ride("cabify_ride_xyz", reason="driver_late")
    assert r["cancellation_fee_mxn"] == 0.0


@pytest.mark.asyncio
async def test_generate_invoice(client: CabifyBusinessClient) -> None:
    r = await client.generate_invoice(mes=3, ejercicio=2026, rfc_empresa="DEMO850101AAA")
    assert r["total_viajes"] > 0
    assert "uuid_cfdi" in r


@pytest.mark.asyncio
async def test_schedule_tool() -> None:
    r = await cabify_schedule_ride(ScheduleRideInput(
        passenger_email="x@y.mx",
        pickup_address="Calle Demo 1",
        destination_address="Calle Demo 2",
        pickup_datetime="2026-04-15T08:00:00Z",
    ))
    assert r["status"] == "scheduled"


@pytest.mark.asyncio
async def test_list_tool() -> None:
    r = await cabify_list_rides(ListRidesInput(limit=5))
    assert "rides" in r


@pytest.mark.asyncio
async def test_get_tool() -> None:
    r = await cabify_get_ride(RideIdInput(ride_id="cabify_xyz"))
    assert "duration_min" in r


@pytest.mark.asyncio
async def test_cancel_tool() -> None:
    r = await cabify_cancel_ride(CancelInput(ride_id="cabify_xyz"))
    assert r["status"] == "cancelled_by_user"


@pytest.mark.asyncio
async def test_invoice_tool() -> None:
    r = await cabify_generate_invoice(
        InvoiceInput(mes=3, ejercicio=2026, rfc_empresa="DEMO850101AAA")
    )
    assert "uuid_cfdi" in r


@pytest.mark.asyncio
async def test_catalogos() -> None:
    r = await cabify_listar_catalogos()
    assert "tipo_vehiculo" in r
    assert "premium" in r["tipo_vehiculo"]
