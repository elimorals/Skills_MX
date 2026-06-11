"""Tests for BanxicoClient — covers mock mode, cache, and response parsing."""

from __future__ import annotations

from datetime import date

import pytest

from mp_banxico.client import BanxicoClient
from mp_banxico.series import TC_USD_MXN_FIX
from shared.errors import ConfigError, McpError, UpstreamError, ValidationError


# ---------- construction ----------


def test_client_defaults_to_mock_when_no_token() -> None:
    c = BanxicoClient()
    assert c.is_mock is True


def test_client_real_mode_when_token_set(monkeypatch) -> None:
    monkeypatch.setenv("BANXICO_TOKEN", "real-token")
    c = BanxicoClient()
    assert c.is_mock is False


def test_explicit_token_overrides_env(monkeypatch) -> None:
    monkeypatch.delenv("BANXICO_TOKEN", raising=False)
    c = BanxicoClient(token="explicit")
    assert c.is_mock is False


def test_mock_env_overrides_real_token(monkeypatch) -> None:
    monkeypatch.setenv("BANXICO_TOKEN", "real-token")
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    c = BanxicoClient()
    assert c.is_mock is True


# ---------- mock mode behavior ----------


async def test_mock_returns_plausible_usd_value() -> None:
    c = BanxicoClient()
    obs = await c.get_serie_value(TC_USD_MXN_FIX.code, date(2026, 3, 15))
    # Anchored around 18.50 ± 1%
    assert 18.0 < obs["valor"] < 19.0
    assert obs["simulated"] is True
    assert obs["fecha"] == "2026-03-15"
    assert "simulada" in obs["advertencias"][0].lower()


async def test_mock_is_deterministic_for_same_inputs() -> None:
    c1 = BanxicoClient()
    c2 = BanxicoClient()
    obs1 = await c1.get_serie_value(TC_USD_MXN_FIX.code, date(2026, 3, 15))
    obs2 = await c2.get_serie_value(TC_USD_MXN_FIX.code, date(2026, 3, 15))
    assert obs1["valor"] == obs2["valor"]


async def test_mock_differs_across_dates() -> None:
    c = BanxicoClient()
    obs1 = await c.get_serie_value(TC_USD_MXN_FIX.code, date(2026, 3, 15))
    obs2 = await c.get_serie_value(TC_USD_MXN_FIX.code, date(2026, 3, 16))
    # Same series, different days → different values (jittered)
    assert obs1["valor"] != obs2["valor"]


# ---------- validation ----------


async def test_invalid_serie_code_raises_validation() -> None:
    c = BanxicoClient()
    with pytest.raises(ValidationError):
        await c.get_serie_value("not-a-code", date(2026, 3, 15))


async def test_invalid_serie_code_empty_raises() -> None:
    c = BanxicoClient()
    with pytest.raises(ValidationError):
        await c.get_serie_value("", date(2026, 3, 15))


# ---------- cache behavior ----------


async def test_second_call_hits_cache(tmp_path) -> None:
    """A second lookup for the same (serie, fecha) must read from cache.

    We verify by flipping the client to real mode without a token after the
    first call. If cache works, the second call still returns the same value
    without trying to reach the network. If cache failed, it would raise
    ConfigError (real mode + no token).
    """
    c = BanxicoClient()
    obs1 = await c.get_serie_value(TC_USD_MXN_FIX.code, date(2026, 3, 15))

    # Flip to real mode but no token — only the cache can serve this now
    c._mock_mode = False
    c._token = None
    obs2 = await c.get_serie_value(TC_USD_MXN_FIX.code, date(2026, 3, 15))
    assert obs1["valor"] == obs2["valor"]
    assert obs1["fecha"] == obs2["fecha"]


async def test_different_dates_produce_separate_cache_entries() -> None:
    c = BanxicoClient()
    obs_15 = await c.get_serie_value(TC_USD_MXN_FIX.code, date(2026, 3, 15))
    obs_16 = await c.get_serie_value(TC_USD_MXN_FIX.code, date(2026, 3, 16))
    # Both should be cached with distinct keys
    keys = c._cache.keys()
    assert any("2026-03-15" in k for k in keys)
    assert any("2026-03-16" in k for k in keys)
    assert obs_15["valor"] != obs_16["valor"]


# ---------- real mode requires token ----------


async def test_real_mode_without_token_raises_config_error(monkeypatch) -> None:
    monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
    # Construct client with token, then null it to simulate misconfiguration
    c = BanxicoClient(token="dummy")
    c._token = None
    c._mock_mode = False
    with pytest.raises(ConfigError):
        await c.get_serie_value(TC_USD_MXN_FIX.code, date(2026, 3, 15))


# ---------- response parsing ----------


def test_parse_normal_response() -> None:
    body = {
        "bmx": {
            "series": [
                {
                    "idSerie": "SF63528",
                    "titulo": "TC FIX",
                    "datos": [{"fecha": "15/03/2026", "dato": "18.5432"}],
                }
            ]
        }
    }
    result = BanxicoClient._parse_banxico_response(body, "SF63528", date(2026, 3, 15))
    assert result["valor"] == 18.5432
    assert result["fecha"] == "2026-03-15"
    assert result["simulated"] is False


def test_parse_iso_date_unchanged() -> None:
    body = {
        "bmx": {
            "series": [
                {"datos": [{"fecha": "2026-03-15", "dato": "18.0"}]}
            ]
        }
    }
    result = BanxicoClient._parse_banxico_response(body, "SF63528", date(2026, 3, 15))
    assert result["fecha"] == "2026-03-15"


def test_parse_no_data_raises_upstream() -> None:
    body = {"bmx": {"series": [{"datos": []}]}}
    with pytest.raises(UpstreamError):
        BanxicoClient._parse_banxico_response(body, "SF63528", date(2026, 3, 15))


def test_parse_no_data_marker_raises_upstream() -> None:
    body = {
        "bmx": {
            "series": [
                {"datos": [{"fecha": "15/03/2026", "dato": "N/E"}]}
            ]
        }
    }
    with pytest.raises(UpstreamError):
        BanxicoClient._parse_banxico_response(body, "SF63528", date(2026, 3, 15))


def test_parse_non_numeric_value_raises() -> None:
    body = {
        "bmx": {
            "series": [
                {"datos": [{"fecha": "15/03/2026", "dato": "abc"}]}
            ]
        }
    }
    with pytest.raises(UpstreamError):
        BanxicoClient._parse_banxico_response(body, "SF63528", date(2026, 3, 15))


def test_parse_malformed_shape_raises() -> None:
    with pytest.raises(UpstreamError):
        BanxicoClient._parse_banxico_response({"wrong": "shape"}, "SF63528", date(2026, 3, 15))


# ---------- bitacora is written ----------


async def test_mock_call_writes_bitacora_entry() -> None:
    c = BanxicoClient()
    await c.get_serie_value(TC_USD_MXN_FIX.code, date(2026, 3, 15))
    entries = c._bitacora.tail()
    assert len(entries) == 1
    assert entries[0]["tool"] == "get_serie_value"
    assert entries[0]["success"] is True
    assert entries[0]["params"]["mode"] == "mock"
