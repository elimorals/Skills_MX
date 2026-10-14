"""Cliente Rappi Partners — API de integración para restaurantes.

Doc oficial: https://dev-portal.rappi.com/en/api-reference/content/
Acceso: Rappi entrega client_id/client_secret tras aprobar la integración (contacto comercial).
Dos familias de dominios para México:
- API nueva (`/restaurants/{auth,menu,orders}/v1`): https://api.rappi.com.mx
- API v2 (`/api/v2/restaurants-integrations-public-api`): https://services.mxgrability.rappi.com
Auth: header `x-authorization: Bearer <token>` (token de /restaurants/auth/v1/token/login/integrations, 24 h).
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
from shared.errors import ConfigError, NotFoundError, handle_httpx_error  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

NAMESPACE = "rappi_partners"
CRED_VARS = ["RAPPI_CLIENT_ID", "RAPPI_CLIENT_SECRET"]
DOMINIOS = {
    "mx": ("https://api.rappi.com.mx", "https://services.mxgrability.rappi.com"),
    "dev": ("https://api.dev.rappi.com", "https://microservices.dev.rappi.com"),
}
V2 = "/api/v2/restaurants-integrations-public-api"
SIN_ENDPOINT = (
    "La API de Rappi no expone {que}. Consulta el Portal Partners de Rappi o el estado de cuenta mensual."
)


class RappiPartnersClient:
    def __init__(self, bitacora: Bitacora | None = None, http: httpx.Client | None = None) -> None:
        self.bitacora = bitacora or Bitacora(NAMESPACE)
        env = os.environ.get("RAPPI_ENV", "mx").strip().lower()
        if env not in DOMINIOS:
            raise ConfigError(f"RAPPI_ENV debe ser mx o dev, no {env!r}")
        self.api, self.services = DOMINIOS[env]
        self._store_id = os.environ.get("RAPPI_STORE_ID", "").strip()
        self._http = http or httpx.Client(timeout=20)
        self._token: str | None = None
        self._token_exp = 0.0

    def _is_mock(self) -> bool:
        return is_mock_mode(CRED_VARS)

    def _log(self, op: str, *, success: bool, params: dict[str, Any] | None = None) -> None:
        self.bitacora.log(op, success=success, params_summary={k: str(v)[:30] for k, v in (params or {}).items()})

    def _store(self) -> str:
        if not self._store_id:
            raise ConfigError("Falta RAPPI_STORE_ID (ID de la tienda en Rappi).")
        return self._store_id

    def _auth(self) -> str:
        if self._token and time.time() < self._token_exp - 300:
            return self._token
        cid, secret = (os.environ.get(v, "").strip() for v in CRED_VARS)
        try:
            r = self._http.post(
                f"{self.api}/restaurants/auth/v1/token/login/integrations",
                json={"client_id": cid, "client_secret": secret},
            )
            r.raise_for_status()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
        body = r.json()
        self._token = body["access_token"]
        self._token_exp = time.time() + float(body.get("expires_in", 0))
        return self._token

    def _call(self, method: str, url: str, **kw: Any) -> Any:
        token = self._auth()
        try:
            r = self._http.request(method, url, headers={"x-authorization": f"Bearer {token}"}, **kw)
            r.raise_for_status()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
        return r.json() if r.content else {}

    def listar_ordenes(self, estado: str = "all", limite: int = 20) -> dict[str, Any]:
        """Órdenes nuevas de la tienda. estado: "all" (GET orders) o "sent" (GET orders/status/sent)."""
        self._log("listar_ordenes", success=True, params={"estado": estado})
        if self._is_mock():
            return mark_simulated({"total": 0, "ordenes": []})
        ruta = f"{V2}/orders/status/sent" if estado == "sent" else f"{V2}/orders"
        ordenes = self._call("GET", f"{self.services}{ruta}", params={"storeId": self._store()})
        ordenes = ordenes[:limite] if isinstance(ordenes, list) else ordenes
        return {"total": len(ordenes) if isinstance(ordenes, list) else None, "ordenes": ordenes, "simulated": False}

    def consultar_orden(self, orden_id: str) -> dict[str, Any]:
        """Busca la orden entre las órdenes nuevas (la API no tiene GET por ID)."""
        self._log("consultar_orden", success=True, params={"orden_id": orden_id})
        if self._is_mock():
            return mark_simulated({"orden_id": orden_id})
        for o in self.listar_ordenes(limite=10_000)["ordenes"] or []:
            if str((o.get("order_detail") or {}).get("order_id")) == str(orden_id):
                return {**o, "simulated": False}
        raise NotFoundError(f"Orden {orden_id} no está entre las órdenes nuevas de la tienda")

    def listar_productos_menu(self) -> dict[str, Any]:
        """Último menú creado para la tienda (GET menu/rappi/{storeId})."""
        self._log("listar_productos_menu", success=True)
        if self._is_mock():
            return mark_simulated({"menu": None})
        return {"menu": self._call("GET", f"{self.services}{V2}/menu/rappi/{self._store()}"), "simulated": False}

    def actualizar_disponibilidad(self, sku: str, disponible: bool) -> dict[str, Any]:
        """Activa/desactiva un producto por SKU (PATCH .../products/SKU/stock, asíncrono)."""
        self._log("actualizar_disponibilidad", success=True, params={"sku": sku, "disponible": disponible})
        if self._is_mock():
            return mark_simulated({"sku": sku, "disponible": disponible})
        body = {"available": [sku], "unavailable": []} if disponible else {"available": [], "unavailable": [sku]}
        r = self._call("PATCH", f"{self.api}/restaurants/menu/v1/stores/{self._store()}/products/SKU/stock", json=body)
        return {"sku": sku, "disponible": disponible, "respuesta": r, "simulated": False}

    def consultar_ranking_zona(self) -> dict[str, Any]:
        if self._is_mock():
            return mark_simulated({"ranking": None})
        raise ConfigError(SIN_ENDPOINT.format(que="ranking por zona"), {"motivo": "sin_endpoint"})

    def estimar_comisiones_mes(self, mes: str | None = None) -> dict[str, Any]:
        if self._is_mock():
            return mark_simulated({"mes": mes, "comision_rappi_mxn": None})
        raise ConfigError(SIN_ENDPOINT.format(que="histórico ni comisiones mensuales"), {"motivo": "sin_endpoint"})
