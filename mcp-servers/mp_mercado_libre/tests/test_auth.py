"""Tests for MeliTokenManager: OAuth refresh, cache, rotation, errors."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from mp_mercado_libre.auth import (
    OAUTH_TOKEN_URL,
    MeliTokenManager,
)
from shared.cache import FileCache
from shared.errors import AuthError, ConfigError


def _token() -> str:
    return hashlib.sha256(b"mp-meli-test-refresh-v1").hexdigest()


def _secret() -> str:
    return hashlib.sha256(b"mp-meli-test-secret-v1").hexdigest()


@pytest.fixture
def cache(tmp_path: Path) -> FileCache:
    return FileCache("test_meli_auth", root=tmp_path)


def _ok_body(access_token: str = "AT-fresh-1", expires_in: int = 21600) -> dict[str, Any]:
    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": expires_in,
        "scope": "offline_access read write",
        "user_id": 12345,
        "refresh_token": _token(),  # unchanged unless rotated
    }


def test_construct_requires_app_id() -> None:
    with pytest.raises(ConfigError):
        MeliTokenManager(app_id="", secret=_secret(), refresh_token=_token())


def test_construct_requires_secret() -> None:
    with pytest.raises(ConfigError):
        MeliTokenManager(app_id="APP", secret="", refresh_token=_token())


def test_construct_requires_refresh_token() -> None:
    with pytest.raises(ConfigError):
        MeliTokenManager(app_id="APP", secret=_secret(), refresh_token="")


@respx.mock
@pytest.mark.asyncio
async def test_refresh_returns_fresh_access_token(cache: FileCache) -> None:
    respx.post(OAUTH_TOKEN_URL).mock(return_value=httpx.Response(200, json=_ok_body("AT-1")))

    tm = MeliTokenManager(app_id="APP", secret=_secret(), refresh_token=_token(), cache=cache)
    token = await tm.get_access_token()
    assert token == "AT-1"


@respx.mock
@pytest.mark.asyncio
async def test_second_call_serves_from_cache(cache: FileCache) -> None:
    route = respx.post(OAUTH_TOKEN_URL).mock(
        return_value=httpx.Response(200, json=_ok_body("AT-cached"))
    )

    tm = MeliTokenManager(app_id="APP", secret=_secret(), refresh_token=_token(), cache=cache)
    first = await tm.get_access_token()
    second = await tm.get_access_token()
    assert first == second == "AT-cached"
    assert route.call_count == 1


@respx.mock
@pytest.mark.asyncio
async def test_force_refresh_bypasses_cache(cache: FileCache) -> None:
    route = respx.post(OAUTH_TOKEN_URL).mock(
        side_effect=[
            httpx.Response(200, json=_ok_body("AT-first")),
            httpx.Response(200, json=_ok_body("AT-second")),
        ]
    )

    tm = MeliTokenManager(app_id="APP", secret=_secret(), refresh_token=_token(), cache=cache)
    a = await tm.get_access_token()
    b = await tm.get_access_token(force_refresh=True)
    assert a == "AT-first"
    assert b == "AT-second"
    assert route.call_count == 2


@respx.mock
@pytest.mark.asyncio
async def test_refresh_token_rotation_updates_internal(cache: FileCache) -> None:
    rotated = hashlib.sha256(b"rotated-v1").hexdigest()
    respx.post(OAUTH_TOKEN_URL).mock(
        return_value=httpx.Response(
            200,
            json={**_ok_body("AT-x"), "refresh_token": rotated},
        )
    )

    tm = MeliTokenManager(app_id="APP", secret=_secret(), refresh_token=_token(), cache=cache)
    await tm.get_access_token()
    assert tm.current_refresh_token == rotated


@respx.mock
@pytest.mark.asyncio
async def test_400_response_raises_auth_error_with_helpful_message(cache: FileCache) -> None:
    respx.post(OAUTH_TOKEN_URL).mock(
        return_value=httpx.Response(400, json={"error": "invalid_grant"})
    )

    tm = MeliTokenManager(app_id="APP", secret=_secret(), refresh_token=_token(), cache=cache)
    with pytest.raises(AuthError) as exc:
        await tm.get_access_token()
    assert "OAuth" in exc.value.message or "refresh_token" in exc.value.message


@respx.mock
@pytest.mark.asyncio
async def test_401_response_raises_auth_error(cache: FileCache) -> None:
    respx.post(OAUTH_TOKEN_URL).mock(return_value=httpx.Response(401, json={}))

    tm = MeliTokenManager(app_id="APP", secret=_secret(), refresh_token=_token(), cache=cache)
    with pytest.raises(AuthError):
        await tm.get_access_token()


@respx.mock
@pytest.mark.asyncio
async def test_body_missing_access_token_raises_auth_error(cache: FileCache) -> None:
    respx.post(OAUTH_TOKEN_URL).mock(
        return_value=httpx.Response(200, json={"token_type": "Bearer"})
    )

    tm = MeliTokenManager(app_id="APP", secret=_secret(), refresh_token=_token(), cache=cache)
    with pytest.raises(AuthError) as exc:
        await tm.get_access_token()
    assert "access_token" in exc.value.message


@respx.mock
@pytest.mark.asyncio
async def test_cache_key_prefix_isolates_multiple_sellers(cache: FileCache) -> None:
    """Dos sellers distintos no deben sobrescribirse en la misma cache."""
    respx.post(OAUTH_TOKEN_URL).mock(
        side_effect=[
            httpx.Response(200, json=_ok_body("AT-seller-a")),
            httpx.Response(200, json=_ok_body("AT-seller-b")),
        ]
    )

    tm_a = MeliTokenManager(
        app_id="APP", secret=_secret(), refresh_token=_token(), cache=cache, cache_key_prefix="a"
    )
    tm_b = MeliTokenManager(
        app_id="APP", secret=_secret(), refresh_token=_token(), cache=cache, cache_key_prefix="b"
    )
    a = await tm_a.get_access_token()
    b = await tm_b.get_access_token()
    assert a == "AT-seller-a"
    assert b == "AT-seller-b"
    # Cada uno cacheado independientemente
    assert (await tm_a.get_access_token()) == "AT-seller-a"
    assert (await tm_b.get_access_token()) == "AT-seller-b"
