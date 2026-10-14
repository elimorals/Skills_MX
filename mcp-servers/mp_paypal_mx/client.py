"""Cliente mp_paypal_mx — PayPal Transaction Search API v1 (solo lectura).

Doc oficial: https://developer.paypal.com/api/transaction-search/v1/
Requiere activar "Transaction Search" en la app REST del Dashboard de PayPal.
Las transacciones tardan hasta 3 h en aparecer; el rango máximo por consulta es 31 días.
"""

from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import ConfigError, NotFoundError, ValidationError, handle_httpx_error  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

NAMESPACE = "paypal_mx"
CRED_VARS = ["PAYPAL_CLIENT_ID", "PAYPAL_CLIENT_SECRET"]
BASE_URLS = {
    "live": "https://api-m.paypal.com",
    "sandbox": "https://api-m.sandbox.paypal.com",
}
MAX_DIAS = 31


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rango(fecha_inicio: str | None, fecha_fin: str | None) -> tuple[str, str]:
    """Normaliza el rango (YYYY-MM-DD o ISO) y valida el máximo de 31 días."""
    fin = datetime.fromisoformat(fecha_fin) if fecha_fin else datetime.now(timezone.utc)
    ini = datetime.fromisoformat(fecha_inicio) if fecha_inicio else fin - timedelta(days=MAX_DIAS)
    fin = fin if fin.tzinfo else fin.replace(tzinfo=timezone.utc)
    ini = ini if ini.tzinfo else ini.replace(tzinfo=timezone.utc)
    if fin <= ini:
        raise ValidationError("fecha_fin debe ser posterior a fecha_inicio")
    if fin - ini > timedelta(days=MAX_DIAS):
        raise ValidationError(f"PayPal permite máximo {MAX_DIAS} días por consulta")
    return _iso(ini), _iso(fin)


class PaypalMxClient:
    def __init__(self, bitacora: Bitacora | None = None, http: httpx.Client | None = None) -> None:
        self.bitacora = bitacora or Bitacora(NAMESPACE)
        env = os.environ.get("PAYPAL_ENV", "live").strip().lower()
        if env not in BASE_URLS:
            raise ConfigError(f"PAYPAL_ENV debe ser live o sandbox, no {env!r}")
        self.base_url = BASE_URLS[env]
        self._http = http or httpx.Client(timeout=30)
        self._token: str | None = None
        self._token_exp = 0.0

    def _is_mock(self) -> bool:
        return is_mock_mode(CRED_VARS)

    def _auth(self) -> str:
        if self._token and time.time() < self._token_exp - 60:
            return self._token
        cid, secret = (os.environ.get(v, "") for v in CRED_VARS)
        if not (cid and secret):
            raise ConfigError("Faltan PAYPAL_CLIENT_ID / PAYPAL_CLIENT_SECRET")
        try:
            r = self._http.post(
                f"{self.base_url}/v1/oauth2/token",
                auth=(cid, secret),
                data={"grant_type": "client_credentials"},
            )
            r.raise_for_status()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
        body = r.json()
        self._token = body["access_token"]
        self._token_exp = time.time() + float(body.get("expires_in", 0))
        return self._token

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        token = self._auth()
        try:
            r = self._http.get(
                f"{self.base_url}{path}",
                params={k: v for k, v in params.items() if v is not None},
                headers={"Authorization": f"Bearer {token}"},
            )
            r.raise_for_status()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc
        return r.json()

    def listar_transacciones(
        self,
        fecha_inicio: str | None = None,
        fecha_fin: str | None = None,
        pagina: int = 1,
        tamano_pagina: int = 100,
    ) -> dict[str, Any]:
        self.bitacora.log("listar_transacciones", success=True, params_summary={"pagina": pagina})
        if self._is_mock():
            return mark_simulated({"transaction_details": [], "total_items": 0, "total_pages": 0})
        ini, fin = _rango(fecha_inicio, fecha_fin)
        body = self._get(
            "/v1/reporting/transactions",
            {
                "start_date": ini,
                "end_date": fin,
                "fields": "transaction_info,payer_info",
                "page": pagina,
                "page_size": max(1, min(tamano_pagina, 500)),
            },
        )
        return {**body, "simulated": False}

    def consultar_transaccion(
        self,
        transaction_id: str,
        fecha_inicio: str | None = None,
        fecha_fin: str | None = None,
    ) -> dict[str, Any]:
        """Busca una transacción por ID dentro del rango (por defecto, los últimos 31 días)."""
        self.bitacora.log("consultar_transaccion", success=True, params_summary={"id": transaction_id[:6]})
        if not transaction_id or len(transaction_id) > 19:
            raise ValidationError("transaction_id de PayPal tiene hasta 19 caracteres")
        if self._is_mock():
            return mark_simulated({"transaction_id": transaction_id, "transaction_details": []})
        ini, fin = _rango(fecha_inicio, fecha_fin)
        body = self._get(
            "/v1/reporting/transactions",
            {"transaction_id": transaction_id, "start_date": ini, "end_date": fin, "fields": "all"},
        )
        detalles = body.get("transaction_details") or []
        if not detalles:
            raise NotFoundError(f"Transacción {transaction_id} no encontrada entre {ini} y {fin}")
        return {**detalles[0], "simulated": False}

    def balance(self, moneda: str | None = None, al_momento: str | None = None) -> dict[str, Any]:
        self.bitacora.log("balance", success=True, params_summary={"moneda": moneda or ""})
        if self._is_mock():
            return mark_simulated({"balances": [], "as_of_time": None})
        body = self._get(
            "/v1/reporting/balances",
            {"currency_code": moneda.upper() if moneda else None, "as_of_time": al_momento},
        )
        return {**body, "simulated": False}
