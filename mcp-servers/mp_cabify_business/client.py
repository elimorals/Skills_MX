"""Cliente Cabify Business."""

from __future__ import annotations

import os
import secrets
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import ConfigError, McpError, NotFoundError, handle_httpx_error  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402


NAMESPACE = "cabify_business_mcp"
CABIFY_API_URL = "https://api.cabify.com"
REQUEST_TIMEOUT_S = 20.0


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class CabifyBusinessClient:
    def __init__(
        self,
        api_key: str | None = None,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        explicit = api_key is not None
        if api_key is None:
            api_key = os.environ.get("CABIFY_API_KEY", "").strip() or None

        self._api_key = api_key
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

        if os.environ.get("PLUGINS_MX_MOCK") == "1":
            self._mock = True
        elif explicit or api_key:
            self._mock = False
        else:
            self._mock = is_mock_mode(["CABIFY_API_KEY"])

    @property
    def is_mock(self) -> bool:
        return self._mock

    def _require_key(self) -> None:
        if not self._api_key:
            raise ConfigError("CABIFY_API_KEY no configurado.")

    def _headers(self) -> dict[str, str]:
        self._require_key()
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def _log(self, op: str, params: dict[str, Any]) -> None:
        safe = dict(params)
        if "passenger_email" in safe and safe["passenger_email"]:
            safe["passenger_email_hash"] = Bitacora.hash_sensitive(
                str(safe.pop("passenger_email"))
            )
        self._bitacora.log(op, success=True, params_summary=safe)

    # ---------- tools ----------

    async def schedule_ride(
        self,
        passenger_email: str,
        pickup_address: str,
        destination_address: str,
        pickup_datetime: str,
        vehicle_type: str = "lite",
        cost_center: str | None = None,
    ) -> dict[str, Any]:
        self._log("schedule_ride", {
            "passenger_email": passenger_email,
            "pickup": pickup_address[:30],
            "destination": destination_address[:30],
            "vehicle_type": vehicle_type,
        })

        if self._mock:
            ride_id = f"cabify_ride_{secrets.token_hex(8)}"
            return mark_simulated({
                "ride_id": ride_id,
                "passenger_email_hash": Bitacora.hash_sensitive(passenger_email),
                "pickup_address": pickup_address,
                "destination_address": destination_address,
                "pickup_datetime": pickup_datetime,
                "vehicle_type": vehicle_type,
                "cost_center": cost_center,
                "status": "scheduled",
                "estimated_price_mxn": 285.00,
                "estimated_duration_min": 32,
                "estimated_distance_km": 12.5,
                "currency": "MXN",
                "scheduled_at": _now_iso(),
            })

        self._require_key()
        url = f"{CABIFY_API_URL}/v1/rides"
        body = {
            "passenger": {"email": passenger_email},
            "pickup": {"address": pickup_address},
            "destination": {"address": destination_address},
            "pickup_datetime": pickup_datetime,
            "vehicle_type": vehicle_type,
            "cost_center": cost_center,
        }
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.post(url, headers=self._headers(), json=body)
                resp.raise_for_status()
                return {**resp.json(), "simulated": False}
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

    async def list_rides(
        self, fecha_desde: str | None = None, status: str | None = None, limit: int = 50
    ) -> dict[str, Any]:
        self._log("list_rides", {"fecha_desde": fecha_desde, "status": status, "limit": limit})

        if self._mock:
            return mark_simulated({
                "rides": [
                    {
                        "ride_id": f"cabify_ride_{i:04d}",
                        "passenger_email_hash": "demo_hash",
                        "pickup_datetime": _now_iso(),
                        "vehicle_type": "lite" if i % 2 == 0 else "premium",
                        "status": "completed",
                        "price_mxn": 250.00 * (i + 1),
                    }
                    for i in range(min(limit, 3))
                ],
                "total_count": 47,
            })

        self._require_key()
        params: dict[str, str] = {"limit": str(limit)}
        if fecha_desde:
            params["from"] = fecha_desde
        if status:
            params["status"] = status
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(
                    f"{CABIFY_API_URL}/v1/rides",
                    headers=self._headers(),
                    params=params,
                )
                resp.raise_for_status()
                return {**resp.json(), "simulated": False}
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

    async def get_ride(self, ride_id: str) -> dict[str, Any]:
        cache_key = f"ride_{ride_id}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("get_ride", {"ride_id": ride_id})

        if self._mock:
            r = mark_simulated({
                "ride_id": ride_id,
                "status": "completed",
                "pickup_address": "Av. Demo 123, Polanco",
                "destination_address": "Aeropuerto AICM T1",
                "pickup_datetime": _now_iso(),
                "completion_datetime": (datetime.now(timezone.utc) + timedelta(minutes=32)).isoformat(),
                "vehicle_type": "premium",
                "driver_name": "Carlos R.",
                "driver_rating": 4.9,
                "price_mxn": 385.00,
                "tip_mxn": 30.00,
                "distance_km": 18.2,
                "duration_min": 35,
            })
            self._cache.set(cache_key, r, ttl_minutes=2)
            return r

        self._require_key()
        url = f"{CABIFY_API_URL}/v1/rides/{ride_id}"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(url, headers=self._headers())
                if resp.status_code == 404:
                    raise NotFoundError(f"Ride {ride_id} no encontrado.")
                resp.raise_for_status()
                body = resp.json()
        except McpError:
            raise
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        r = {**body, "simulated": False}
        self._cache.set(cache_key, r, ttl_minutes=2)
        return r

    async def cancel_ride(self, ride_id: str, reason: str = "user_request") -> dict[str, Any]:
        self._log("cancel_ride", {"ride_id": ride_id, "reason": reason})

        if self._mock:
            return mark_simulated({
                "ride_id": ride_id,
                "status": "cancelled_by_user",
                "cancellation_fee_mxn": 30.00 if reason != "driver_late" else 0.00,
                "cancelled_at": _now_iso(),
            })

        self._require_key()
        url = f"{CABIFY_API_URL}/v1/rides/{ride_id}/cancel"
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.post(url, headers=self._headers(), json={"reason": reason})
                resp.raise_for_status()
                return {**resp.json(), "simulated": False}
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

    async def generate_invoice(
        self, mes: int, ejercicio: int, rfc_empresa: str
    ) -> dict[str, Any]:
        """Genera factura mensual consolidada de viajes corporativos."""
        self._log("generate_invoice", {"mes": mes, "ejercicio": ejercicio, "rfc_empresa": rfc_empresa})

        if self._mock:
            return mark_simulated({
                "factura_id": f"cabify_invoice_{ejercicio}{mes:02d}",
                "periodo": f"{ejercicio}-{mes:02d}",
                "rfc_empresa": rfc_empresa,
                "total_viajes": 47,
                "subtotal_mxn": 14_500.00,
                "iva_mxn": 2_320.00,
                "total_mxn": 16_820.00,
                "url_pdf": None,
                "uuid_cfdi": "ABCD-1234-5678-9012-...",
                "fecha_emision": _now_iso(),
            })

        self._require_key()
        url = f"{CABIFY_API_URL}/v1/invoices"
        body = {"month": mes, "year": ejercicio, "rfc": rfc_empresa}
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.post(url, headers=self._headers(), json=body)
                resp.raise_for_status()
                return {**resp.json(), "simulated": False}
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
