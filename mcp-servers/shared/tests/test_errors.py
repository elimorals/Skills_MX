"""Tests for shared.errors error envelope."""

from __future__ import annotations

import httpx
import pytest

from shared.errors import (
    AuthError,
    McpError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
    UpstreamError,
    ValidationError,
    handle_httpx_error,
)


def test_mcp_error_to_dict_has_required_fields() -> None:
    err = McpError("something bad", details={"x": 1})
    out = err.to_dict()
    assert out["error"] is True
    assert out["code"] == "mcp_error"
    assert out["message"] == "something bad"
    assert out["details"] == {"x": 1}


def test_specific_errors_have_distinct_codes() -> None:
    assert ValidationError("").code == "validation_error"
    assert AuthError("").code == "auth_error"
    assert RateLimitError("").code == "rate_limit_error"
    assert UpstreamError("").code == "upstream_error"
    assert NotFoundError("").code == "not_found"
    assert TimeoutError("").code == "timeout"


def _make_status_error(status_code: int, body: str = "") -> httpx.HTTPStatusError:
    """Build a real HTTPStatusError with a fake response/request."""
    request = httpx.Request("GET", "https://example.test/")
    response = httpx.Response(status_code, content=body.encode("utf-8"), request=request)
    return httpx.HTTPStatusError("err", request=request, response=response)


def test_handle_401_returns_auth_error() -> None:
    err = handle_httpx_error(_make_status_error(401))
    assert isinstance(err, AuthError)
    assert err.details["status_code"] == 401


def test_handle_403_returns_auth_error() -> None:
    err = handle_httpx_error(_make_status_error(403))
    assert isinstance(err, AuthError)


def test_handle_404_returns_not_found() -> None:
    err = handle_httpx_error(_make_status_error(404))
    assert isinstance(err, NotFoundError)


def test_handle_429_returns_rate_limit() -> None:
    err = handle_httpx_error(_make_status_error(429))
    assert isinstance(err, RateLimitError)


def test_handle_500_returns_upstream_error() -> None:
    err = handle_httpx_error(_make_status_error(500))
    assert isinstance(err, UpstreamError)


def test_handle_other_4xx_returns_upstream() -> None:
    err = handle_httpx_error(_make_status_error(418))
    assert isinstance(err, UpstreamError)


def test_handle_timeout_returns_timeout_error() -> None:
    err = handle_httpx_error(httpx.TimeoutException("timed out"))
    assert isinstance(err, TimeoutError)


def test_handle_request_error_returns_upstream() -> None:
    err = handle_httpx_error(httpx.RequestError("network broken"))
    assert isinstance(err, UpstreamError)


def test_handle_unknown_exception_wraps_as_upstream() -> None:
    err = handle_httpx_error(RuntimeError("weird"))
    assert isinstance(err, UpstreamError)
    assert "RuntimeError" in err.message


def test_body_preview_truncated() -> None:
    big_body = "x" * 5000
    err = handle_httpx_error(_make_status_error(500, body=big_body))
    assert len(err.details["body_preview"]) <= 300
