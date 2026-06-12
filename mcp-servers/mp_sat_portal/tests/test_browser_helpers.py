"""Tests de los helpers de browser (sin requerir Playwright instalado)."""

from __future__ import annotations

from pathlib import Path

import pytest

from mp_sat_portal._browser_helpers import (
    DEFAULT_FAILURE_DUMP_DIR,
    LoginFailedError,
    dump_failure_artifacts,
    with_retry,
)
from shared.errors import AuthError, UpstreamError


def test_login_failed_error_is_auth_error():
    """LoginFailedError es AuthError → no se reintenta automáticamente."""
    exc = LoginFailedError("test")
    assert isinstance(exc, AuthError)
    assert exc.code == "login_failed"


def test_default_failure_dump_dir_is_under_cache():
    assert "plugins-mx" in str(DEFAULT_FAILURE_DUMP_DIR)
    assert "sat_portal" in str(DEFAULT_FAILURE_DUMP_DIR)


def test_with_retry_returns_on_first_success():
    calls = {"count": 0}

    def fn():
        calls["count"] += 1
        return "ok"

    assert with_retry(fn) == "ok"
    assert calls["count"] == 1


def test_with_retry_retries_upstream_then_succeeds():
    calls = {"count": 0}

    def fn():
        calls["count"] += 1
        if calls["count"] < 3:
            raise UpstreamError("transitorio")
        return "ok"

    result = with_retry(fn, max_attempts=3, backoff_seconds=0.001)
    assert result == "ok"
    assert calls["count"] == 3


def test_with_retry_propagates_after_max_attempts():
    calls = {"count": 0}

    def fn():
        calls["count"] += 1
        raise UpstreamError("siempre falla")

    with pytest.raises(UpstreamError):
        with_retry(fn, max_attempts=2, backoff_seconds=0.001)
    assert calls["count"] == 2


def test_with_retry_does_not_retry_auth_error():
    """AuthError no es retryable por default — si las credenciales son malas,
    no van a mejorar con backoff."""
    calls = {"count": 0}

    def fn():
        calls["count"] += 1
        raise AuthError("creds malas")

    with pytest.raises(AuthError):
        with_retry(fn, max_attempts=5, backoff_seconds=0.001)
    assert calls["count"] == 1  # No reintenta


def test_dump_failure_artifacts_handles_missing_page(tmp_path: Path):
    """No debe romper si la page no tiene los métodos esperados."""

    class FakePage:
        def screenshot(self, **_):
            raise RuntimeError("simulado")

        def content(self):
            return "<html><body>test</body></html>"

    artifacts = dump_failure_artifacts(
        FakePage(), operation="test_op", dump_dir=tmp_path
    )
    # Screenshot falló, pero HTML sí guardó
    assert "html" in artifacts
    assert "screenshot" not in artifacts
    assert Path(artifacts["html"]).exists()
