"""Async client for the Banxico SIE REST API.

Endpoint pattern (single date):
    GET https://www.banxico.org.mx/SieAPIRest/service/v1/series/{ID}/datos/{date}/{date}

Endpoint pattern (range):
    GET .../series/{ID}/datos/{from}/{to}

Endpoint pattern (latest available):
    GET .../series/{ID}/datos/oportuno

Auth: header `Bmx-Token: <token>`.

The token is free, lifetime, and obtained at:
    https://www.banxico.org.mx/SieAPIRest/service/v1/token

This client handles:
- Real mode via httpx when BANXICO_TOKEN is set
- Mock mode with plausible values otherwise
- Cache hits via shared.cache.FileCache
- Typed errors via shared.errors.handle_httpx_error
"""

from __future__ import annotations

import asyncio
import random
import sys
from datetime import date
from pathlib import Path
from typing import Any

import httpx

# Ensure the repo root is importable so `shared.*` resolves regardless of cwd.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import (  # noqa: E402
    ConfigError,
    McpError,
    UpstreamError,
    ValidationError,
    handle_httpx_error,
)
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

BANXICO_BASE_URL = "https://www.banxico.org.mx/SieAPIRest/service/v1"
NAMESPACE = "banxico_mcp"
REQUEST_TIMEOUT_S = 15.0


# Plausible reference values for mock mode — anchored to recent ranges so
# downstream skills get something realistic for tests/demos.
_MOCK_REFERENCE_RATES: dict[str, float] = {
    "USD/MXN": 18.50,
    "EUR/MXN": 20.10,
    "GBP/MXN": 23.40,
    "CAD/MXN": 13.50,
    "JPY/MXN": 0.123,
}

_MOCK_UMA_DIARIA = 108.57  # 2024 reference value
_MOCK_INPC = 134.5  # rough mid-2026 reference
_MOCK_TIIE_28 = 10.25  # rough mid-2026 reference


class BanxicoClient:
    """Async client over Banxico SIE API with cache + mock fallback."""

    def __init__(
        self,
        token: str | None = None,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        # Resolve token from env if not passed explicitly. An explicit
        # constructor arg always wins (useful for tests/programmatic config).
        import os

        explicitly_set = token is not None
        if token is None:
            token = os.environ.get("BANXICO_TOKEN") or None
        self._token = token
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)
        # PLUGINS_MX_MOCK=1 always wins (used to force mock in dev with real creds).
        if os.environ.get("PLUGINS_MX_MOCK") == "1":
            self._mock_mode = True
        elif explicitly_set or self._token:
            self._mock_mode = False
        else:
            self._mock_mode = is_mock_mode(["BANXICO_TOKEN"])

    @property
    def is_mock(self) -> bool:
        return self._mock_mode

    # ---------- public API ----------

    async def get_serie_value(
        self,
        serie_code: str,
        fecha: date,
        *,
        cache_ttl_hours: float = 24.0,
        cache_key_hint: str | None = None,
    ) -> dict[str, Any]:
        """Fetch a single observation for a series on a given date.

        Returns a dict shaped:
            { "fecha": "YYYY-MM-DD", "valor": float, "serie": str,
              "simulated": bool, "advertencias": [...] }

        Raises McpError subclasses on failure.
        """
        if not _looks_like_serie_code(serie_code):
            raise ValidationError(
                f"Invalid Banxico series code: {serie_code!r}. Expected like 'SF63528'.",
                {"serie_code": serie_code},
            )

        cache_key = cache_key_hint or f"{serie_code}_{fecha.isoformat()}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)  # don't mutate stored value

        # In mock mode, fabricate a plausible response and cache it like the real call.
        if self._mock_mode:
            payload = self._mock_response_for(serie_code, fecha)
            self._cache.set(cache_key, payload, ttl_hours=cache_ttl_hours)
            self._bitacora.log(
                "get_serie_value",
                success=True,
                params_summary={"serie": serie_code, "fecha": fecha.isoformat(), "mode": "mock"},
                result_summary={"value": payload.get("valor")},
            )
            return payload

        # Real mode
        if not self._token:
            raise ConfigError(
                "BANXICO_TOKEN is not set. Get one free at "
                "https://www.banxico.org.mx/SieAPIRest/service/v1/token",
            )

        url = f"{BANXICO_BASE_URL}/series/{serie_code}/datos/{fecha.isoformat()}/{fecha.isoformat()}"
        start = _now_ms()
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(
                    url,
                    headers={"Bmx-Token": self._token, "Accept": "application/json"},
                )
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            err = handle_httpx_error(exc)
            self._bitacora.log(
                "get_serie_value",
                success=False,
                duration_ms=_now_ms() - start,
                params_summary={"serie": serie_code, "fecha": fecha.isoformat()},
                error={"code": err.code, "message": err.message},
            )
            raise err from exc

        payload = self._parse_banxico_response(body, serie_code, fecha)
        self._cache.set(cache_key, payload, ttl_hours=cache_ttl_hours)
        self._bitacora.log(
            "get_serie_value",
            success=True,
            duration_ms=_now_ms() - start,
            params_summary={"serie": serie_code, "fecha": fecha.isoformat()},
            result_summary={"value": payload.get("valor")},
        )
        return payload

    async def get_serie_latest(
        self,
        serie_code: str,
        *,
        cache_ttl_hours: float = 6.0,
    ) -> dict[str, Any]:
        """Fetch the most recent observation for a series.

        Uses Banxico's `/datos/oportuno` endpoint. Cache shorter than dated
        queries because "latest" moves throughout the day.
        """
        if not _looks_like_serie_code(serie_code):
            raise ValidationError(
                f"Invalid Banxico series code: {serie_code!r}.",
                {"serie_code": serie_code},
            )

        cache_key = f"{serie_code}_oportuno"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        if self._mock_mode:
            # Use today as the synthetic "latest" date
            from datetime import datetime, timezone

            today = datetime.now(timezone.utc).date()
            payload = self._mock_response_for(serie_code, today)
            self._cache.set(cache_key, payload, ttl_hours=cache_ttl_hours)
            self._bitacora.log(
                "get_serie_latest",
                success=True,
                params_summary={"serie": serie_code, "mode": "mock"},
                result_summary={"value": payload.get("valor")},
            )
            return payload

        if not self._token:
            raise ConfigError(
                "BANXICO_TOKEN is not set. Get one free at "
                "https://www.banxico.org.mx/SieAPIRest/service/v1/token",
            )

        url = f"{BANXICO_BASE_URL}/series/{serie_code}/datos/oportuno"
        start = _now_ms()
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
                resp = await client.get(
                    url,
                    headers={"Bmx-Token": self._token, "Accept": "application/json"},
                )
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:
            err = handle_httpx_error(exc)
            self._bitacora.log(
                "get_serie_latest",
                success=False,
                duration_ms=_now_ms() - start,
                params_summary={"serie": serie_code},
                error={"code": err.code, "message": err.message},
            )
            raise err from exc

        # For latest, the date comes from the response itself
        payload = self._parse_banxico_response(body, serie_code, fecha=None)
        self._cache.set(cache_key, payload, ttl_hours=cache_ttl_hours)
        self._bitacora.log(
            "get_serie_latest",
            success=True,
            duration_ms=_now_ms() - start,
            params_summary={"serie": serie_code},
            result_summary={"value": payload.get("valor")},
        )
        return payload

    # ---------- internal helpers ----------

    @staticmethod
    def _parse_banxico_response(
        body: dict[str, Any],
        serie_code: str,
        fecha: date | None,
    ) -> dict[str, Any]:
        """Extract the (fecha, valor) tuple from a Banxico SIE JSON response.

        Banxico format:
            { "bmx": { "series": [ { "datos": [ { "fecha": "DD/MM/YYYY", "dato": "18.5432" } ] } ] } }
        """
        try:
            datos = body["bmx"]["series"][0]["datos"]
            if not datos:
                raise UpstreamError(
                    f"Banxico returned no observations for {serie_code} on "
                    f"{fecha.isoformat() if fecha else 'oportuno'}.",
                    {"serie": serie_code},
                )
            obs = datos[0]
            raw_date = obs["fecha"]
            raw_value = obs["dato"]
        except (KeyError, IndexError, TypeError) as exc:
            raise UpstreamError(
                "Unexpected Banxico response shape — schema may have changed.",
                {"raw_body": str(body)[:300]},
            ) from exc

        # Banxico delivers DD/MM/YYYY; normalize to ISO
        fecha_iso = _parse_banxico_date(raw_date)

        # Some series come back with "N/E" (no data) — propagate as upstream error
        if raw_value in ("N/E", "ND", ""):
            raise UpstreamError(
                f"Banxico has no value for {serie_code} on {fecha_iso} (N/E).",
                {"serie": serie_code, "fecha": fecha_iso},
            )

        try:
            valor = float(raw_value)
        except (TypeError, ValueError) as exc:
            raise UpstreamError(
                f"Banxico value for {serie_code} is not numeric: {raw_value!r}.",
                {"serie": serie_code, "raw_value": raw_value},
            ) from exc

        return {
            "fecha": fecha_iso,
            "valor": valor,
            "serie": serie_code,
            "fuente": "Banxico",
            "simulated": False,
            "advertencias": [],
        }

    @staticmethod
    def _mock_response_for(serie_code: str, fecha: date) -> dict[str, Any]:
        """Produce a plausible synthetic observation for mock mode.

        Uses deterministic jitter seeded by (serie, fecha) so the same lookup
        always returns the same value in mock mode — important for tests.
        """
        rng = random.Random(f"{serie_code}_{fecha.isoformat()}")

        # Map serie → reference value
        if serie_code == "SF63528":  # USD/MXN
            base = _MOCK_REFERENCE_RATES["USD/MXN"]
        elif serie_code == "SF46410":
            base = _MOCK_REFERENCE_RATES["EUR/MXN"]
        elif serie_code == "SF46406":
            base = _MOCK_REFERENCE_RATES["GBP/MXN"]
        elif serie_code == "SF60632":
            base = _MOCK_REFERENCE_RATES["CAD/MXN"]
        elif serie_code == "SF46411":
            base = _MOCK_REFERENCE_RATES["JPY/MXN"]
        elif serie_code == "SF60653":
            base = _MOCK_REFERENCE_RATES["USD/MXN"]  # similar to FIX
        elif serie_code == "SF43783":
            base = _MOCK_TIIE_28
        elif serie_code == "SP74625":
            base = _MOCK_INPC
        elif serie_code == "SP74660":
            base = _MOCK_UMA_DIARIA
        else:
            base = 1.0  # unknown series — produce something benign

        # ±1% jitter; round to 4 decimals like Banxico publishes
        jitter = rng.uniform(-0.01, 0.01)
        value = round(base * (1 + jitter), 4)

        return mark_simulated(
            {
                "fecha": fecha.isoformat(),
                "valor": value,
                "serie": serie_code,
                "fuente": "mock (Banxico no configurado)",
            },
            note="Respuesta simulada — configura BANXICO_TOKEN para valores reales.",
        )


def _now_ms() -> float:
    """Monotonic clock in milliseconds for timing measurements."""
    return asyncio.get_event_loop().time() * 1000 if asyncio.get_event_loop().is_running() else 0.0


def _looks_like_serie_code(s: str) -> bool:
    """Quick syntactic check: 2 letters + 5+ digits."""
    if not s or len(s) < 6:
        return False
    return s[:2].isalpha() and s[2:].isdigit()


def _parse_banxico_date(raw: str) -> str:
    """Convert Banxico's 'DD/MM/YYYY' to ISO 'YYYY-MM-DD'.

    Returns the input unchanged if it's already ISO-shaped — defensive against
    upstream format changes.
    """
    if "-" in raw and len(raw) == 10:
        return raw  # already ISO
    parts = raw.split("/")
    if len(parts) != 3:
        return raw  # give up, let downstream see the raw form
    dd, mm, yyyy = parts
    return f"{yyyy.zfill(4)}-{mm.zfill(2)}-{dd.zfill(2)}"
