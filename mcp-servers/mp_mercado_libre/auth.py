"""OAuth 2.0 token management for Mercado Libre.

ML's OAuth flow:
1. User authorizes the app at:
   https://auth.mercadolibre.com.mx/authorization?response_type=code&client_id=APP_ID&redirect_uri=...
2. App receives `code` at redirect_uri, exchanges it for tokens:
   POST https://api.mercadolibre.com/oauth/token
   Body: grant_type=authorization_code, client_id, client_secret, code, redirect_uri
3. Receives access_token (TTL 6h) + refresh_token (TTL 6 months)

This module handles:
- Storing refresh_token (user must obtain it once and pass it via env)
- Auto-refreshing access_token when expired
- Caching access_token across calls via shared.cache.FileCache

⚠ This file does NOT implement the initial OAuth authorize redirect — that
requires a browser flow and is out of scope for an MCP. The user provides
the refresh_token they obtained externally (via cli, web app, or postman).
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.cache import FileCache  # noqa: E402
from shared.errors import (  # noqa: E402
    AuthError,
    ConfigError,
    handle_httpx_error,
)

OAUTH_TOKEN_URL = "https://api.mercadolibre.com/oauth/token"
# Refresh tokens are 6h-valid; we refresh proactively at 5h to avoid race windows.
ACCESS_TOKEN_CACHE_HOURS = 5.0


class MeliTokenManager:
    """Manages access tokens for a single ML seller.

    The refresh_token must be obtained once externally (e.g., via the OAuth
    authorization flow in a browser) and provided here. This class then
    handles the periodic refresh transparently.

    Usage:
        tm = MeliTokenManager(app_id="...", secret="...", refresh_token="...")
        token = await tm.get_access_token()  # cached or freshly refreshed
        # ... use token in API calls ...
    """

    def __init__(
        self,
        app_id: str,
        secret: str,
        refresh_token: str,
        cache: FileCache | None = None,
        cache_key_prefix: str = "default",
    ) -> None:
        if not app_id:
            raise ConfigError("ML_APP_ID is required for OAuth.")
        if not secret:
            raise ConfigError("ML_SECRET is required for OAuth.")
        if not refresh_token:
            raise ConfigError("ML_REFRESH_TOKEN is required for OAuth.")

        self._app_id = app_id
        self._secret = secret
        self._refresh_token = refresh_token
        self._cache = cache or FileCache("mercadolibre_mcp_auth")
        # Allow multiple sellers to coexist by prefixing cache keys
        self._cache_key = f"access_token_{cache_key_prefix}"

    async def get_access_token(self, force_refresh: bool = False) -> str:
        """Return a valid access token, refreshing if needed."""
        if not force_refresh:
            cached = self._cache.get(self._cache_key)
            if cached and isinstance(cached, dict) and cached.get("access_token"):
                return cached["access_token"]

        return await self._refresh()

    async def _refresh(self) -> str:
        """Hit ML's token endpoint to obtain a fresh access_token."""
        data = {
            "grant_type": "refresh_token",
            "client_id": self._app_id,
            "client_secret": self._secret,
            "refresh_token": self._refresh_token,
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    OAUTH_TOKEN_URL,
                    data=data,
                    headers={"Accept": "application/json"},
                )
                resp.raise_for_status()
                body = resp.json()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            if status in (400, 401):
                raise AuthError(
                    f"OAuth refresh failed (HTTP {status}). The refresh_token may be "
                    "expired (6 months) or revoked. Re-run the OAuth authorize flow.",
                    {"status_code": status},
                ) from exc
            raise handle_httpx_error(exc) from exc
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        access_token = body.get("access_token")
        if not access_token:
            raise AuthError(
                "OAuth response missing access_token.",
                {"body_preview": str(body)[:200]},
            )

        # ML may rotate the refresh_token on each refresh — keep the new one
        new_refresh = body.get("refresh_token")
        if new_refresh and new_refresh != self._refresh_token:
            self._refresh_token = new_refresh

        # Cache the access_token with TTL slightly less than its expiry
        self._cache.set(
            self._cache_key,
            {
                "access_token": access_token,
                "expires_in": body.get("expires_in"),
                "obtained_at": datetime.now(timezone.utc).isoformat(),
                "refresh_token": self._refresh_token,
            },
            ttl_hours=ACCESS_TOKEN_CACHE_HOURS,
        )

        return access_token

    @property
    def current_refresh_token(self) -> str:
        """Expose the latest refresh_token (may have rotated since construction)."""
        return self._refresh_token
