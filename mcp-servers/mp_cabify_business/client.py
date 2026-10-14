"""Cliente Cabify Business — Ride-Hailing API v4.

Doc oficial: https://developers.cabify.com/docs/ride-hailing (índice: https://cabify-api.readme.io/llms.txt)
Auth: OAuth2 client_credentials con el "OAuth UUID" y "Secret" de la integración
creada en el panel de Cabify Business → Integración. Token válido ~30 días.
Las paradas van por coordenadas `loc: [lat, lon]`; antes de pedir un viaje hay que
llamar a /estimates y usar el `product.id` devuelto.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any

import httpx

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import ConfigError, handle_httpx_error  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402


NAMESPACE = "cabify_business_mcp"
HOSTS = {"production": "https://cabify.com", "sandbox": "https://cabify-sandbox.com"}
CRED_VARS = ["CABIFY_CLIENT_ID", "CABIFY_CLIENT_SECRET"]
REQUEST_TIMEOUT_S = 20.0


def _parada(lat: float, lon: float, **extra: Any) -> dict[str, Any]:
    return {"loc": [lat, lon], **{k: v for k, v in extra.items() if v}}


class CabifyBusinessClient:
    def __init__(self, bitacora: Bitacora | None = None, transport: httpx.AsyncBaseTransport | None = None) -> None:
        env = os.environ.get("CABIFY_ENV", "production").strip().lower()
        if env not in HOSTS:
            raise ConfigError(f"CABIFY_ENV debe ser production o sandbox, no {env!r}")
        self.host = HOSTS[env]
        self._bitacora = bitacora or Bitacora(NAMESPACE)
        self._transport = transport
        self._token: str | None = None
        self._token_exp = 0.0

    @property
    def is_mock(self) -> bool:
        return is_mock_mode(CRED_VARS)

    def _http(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S, transport=self._transport)

    async def _auth(self) -> str:
        if self._token and time.time() < self._token_exp - 3600:
            return self._token
        cid, secret = (os.environ.get(v, "").strip() for v in CRED_VARS)
        if not (cid and secret):
            raise ConfigError("Faltan CABIFY_CLIENT_ID / CABIFY_CLIENT_SECRET (OAuth UUID y Secret).")
        try:
            async with self._http() as c:
                r = await c.post(
                    f"{self.host}/auth/api/authorization",
                    data={"grant_type": "client_credentials", "client_id": cid, "client_secret": secret},
                )
                r.raise_for_status()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
        body = r.json()
        self._token = body["access_token"]
        self._token_exp = time.time() + float(body.get("expires_in", 0))
        return self._token

    async def _call(self, method: str, path: str, json: Any = None) -> Any:
        token = await self._auth()
        try:
            async with self._http() as c:
                r = await c.request(
                    method,
                    f"{self.host}/api/v4{path}",
                    json=json,
                    headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                )
                r.raise_for_status()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
        return r.json() if r.content else {}

    def _log(self, op: str, **params: Any) -> None:
        self._bitacora.log(op, success=True, params_summary={k: str(v)[:40] for k, v in params.items()})

    async def estimar(
        self,
        requester_id: str,
        origen: tuple[float, float],
        destino: tuple[float, float],
        inicio: str | None = None,
    ) -> dict[str, Any]:
        """Precios y productos disponibles (POST /api/v4/estimates)."""
        self._log("estimar", requester_id=requester_id)
        if self.is_mock:
            return mark_simulated({"estimaciones": [{"product": {"id": "mock-lite", "name": "Lite"}, "total": {"amount": 28500, "currency": "MXN"}}]})
        body = {
            "requester_id": requester_id,
            "start_type": "reserved" if inicio else "asap",
            "stops": [_parada(*origen), _parada(*destino)],
        }
        if inicio:
            body["start_at"] = inicio
        return {"estimaciones": await self._call("POST", "/estimates", body), "simulated": False}

    async def pedir_viaje(
        self,
        requester_id: str,
        product_id: str,
        origen: tuple[float, float],
        destino: tuple[float, float],
        rider: dict[str, Any],
        inicio: str | None = None,
        origen_direccion: str | None = None,
        destino_direccion: str | None = None,
        label_slug: str | None = None,
        mensaje: str | None = None,
    ) -> dict[str, Any]:
        """Crea un viaje real (POST /api/v4/journey). Genera cargo a la empresa."""
        self._log("pedir_viaje", requester_id=requester_id, product_id=product_id)
        if self.is_mock:
            return mark_simulated({"id": "mock-journey"})
        body: dict[str, Any] = {
            "requester_id": requester_id,
            "product_id": product_id,
            "rider": rider,
            "stops": [_parada(*origen, addr=origen_direccion), _parada(*destino, addr=destino_direccion)],
        }
        for k, v in (("start_at", inicio), ("label_slug", label_slug), ("message", mensaje)):
            if v:
                body[k] = v
        return {**await self._call("POST", "/journey", body), "simulated": False}

    async def consultar_viaje(self, journey_id: str) -> dict[str, Any]:
        """Detalle, estado final y totales (GET /api/v4/journey/{id})."""
        self._log("consultar_viaje", journey_id=journey_id)
        if self.is_mock:
            return mark_simulated({"id": journey_id, "finished": True, "end_state": "drop off"})
        return {**await self._call("GET", f"/journey/{journey_id}"), "simulated": False}

    async def estado_viaje(self, journey_id: str) -> dict[str, Any]:
        """Estado operativo en vivo: conductor, vehículo, ruta (GET /api/v4/journey/{id}/state)."""
        self._log("estado_viaje", journey_id=journey_id)
        if self.is_mock:
            return mark_simulated({"id": journey_id, "name": "hired"})
        return {**await self._call("GET", f"/journey/{journey_id}/state"), "simulated": False}

    async def cancelar_viaje(self, journey_id: str) -> dict[str, Any]:
        """Cancela (POST /api/v4/journey/{id}/state). Con conductor asignado puede cobrar; 409 si ya no se puede."""
        self._log("cancelar_viaje", journey_id=journey_id)
        if self.is_mock:
            return mark_simulated({"id": journey_id})
        return {**await self._call("POST", f"/journey/{journey_id}/state"), "simulated": False}

    async def ventas_viaje(self, journey_id: str) -> dict[str, Any]:
        """Recibos (sales) del viaje, disponibles cuando pasa a `terminated` (GET /api/v4/journey/{id}/sales)."""
        self._log("ventas_viaje", journey_id=journey_id)
        if self.is_mock:
            return mark_simulated({"ventas": []})
        return {"ventas": await self._call("GET", f"/journey/{journey_id}/sales"), "simulated": False}
