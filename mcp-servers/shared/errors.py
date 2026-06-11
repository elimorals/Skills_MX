"""Standardized error handling for plugins-mx MCP servers.

All MCPs use the same error envelope to make agent reasoning predictable.
"""

from __future__ import annotations

from typing import Any


class McpError(Exception):
    """Base exception for plugins-mx MCPs.

    Carries a stable `code` field so callers can branch on error type
    without parsing free-text messages.
    """

    code: str = "mcp_error"

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": True,
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class ValidationError(McpError):
    """Input failed local validation before reaching the external service."""

    code = "validation_error"


class AuthError(McpError):
    """Authentication / authorization with the external service failed."""

    code = "auth_error"


class RateLimitError(McpError):
    """External service rejected request due to rate limiting."""

    code = "rate_limit_error"


class UpstreamError(McpError):
    """External service returned an error (5xx or unexpected)."""

    code = "upstream_error"


class NotFoundError(McpError):
    """Requested resource was not found upstream."""

    code = "not_found"


class TimeoutError(McpError):  # noqa: A001 — intentionally shadowing builtin for clarity
    """Request to upstream service timed out."""

    code = "timeout"


class ConfigError(McpError):
    """MCP is misconfigured (missing env vars, bad credentials format)."""

    code = "config_error"


def handle_httpx_error(exc: Exception) -> McpError:
    """Convert an httpx exception into a typed McpError.

    Used by every MCP to produce consistent error envelopes regardless of
    which upstream API failed.
    """
    # Avoid hard dependency on httpx at import time for shared module
    try:
        import httpx
    except ImportError:  # pragma: no cover
        return UpstreamError(f"Unexpected error: {type(exc).__name__}", {"raw": str(exc)})

    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        body_preview = exc.response.text[:300] if exc.response.text else ""
        details = {"status_code": status, "body_preview": body_preview}

        if status == 401 or status == 403:
            return AuthError(
                f"Authentication failed (HTTP {status}). Check API credentials.",
                details,
            )
        if status == 404:
            return NotFoundError(
                f"Resource not found (HTTP {status}).",
                details,
            )
        if status == 429:
            return RateLimitError(
                f"Rate limit exceeded (HTTP {status}). Wait before retrying.",
                details,
            )
        if 500 <= status < 600:
            return UpstreamError(
                f"Upstream server error (HTTP {status}). Service may be down.",
                details,
            )
        return UpstreamError(
            f"Upstream returned HTTP {status}.",
            details,
        )

    if isinstance(exc, httpx.TimeoutException):
        return TimeoutError("Request timed out. Upstream is slow or unreachable.")

    if isinstance(exc, httpx.RequestError):
        return UpstreamError(
            f"Network error: {type(exc).__name__}. Check connectivity.",
            {"raw": str(exc)},
        )

    # Unexpected — wrap as UpstreamError to preserve the typed envelope
    return UpstreamError(
        f"Unexpected error: {type(exc).__name__}",
        {"raw": str(exc)},
    )
