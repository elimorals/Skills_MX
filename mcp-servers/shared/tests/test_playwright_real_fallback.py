import pytest

from shared.errors import UpstreamError
from shared.playwright_real import with_real_or_fallback


def _falla():
    raise UpstreamError("portal caído")


def test_sin_mock_forzado_propaga(monkeypatch):
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    with pytest.raises(UpstreamError):
        with_real_or_fallback(_falla, lambda: {"x": 1}, portal="p")


def test_mock_forzado_cae_a_fallback_marcado(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    r = with_real_or_fallback(_falla, lambda: {"x": 1}, portal="p")
    assert r["simulated"] is True and r["advertencias"]
