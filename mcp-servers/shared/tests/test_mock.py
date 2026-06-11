"""Tests for shared.mock helpers."""

from __future__ import annotations

import pytest

from shared.mock import is_mock_mode, mark_simulated


def test_mock_when_no_creds_set(monkeypatch) -> None:
    monkeypatch.delenv("FAKE_TOKEN", raising=False)
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    assert is_mock_mode(["FAKE_TOKEN"]) is True


def test_real_when_credential_set(monkeypatch) -> None:
    monkeypatch.setenv("FAKE_TOKEN", "real-value")
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    assert is_mock_mode(["FAKE_TOKEN"]) is False


def test_empty_credential_still_mock(monkeypatch) -> None:
    monkeypatch.setenv("FAKE_TOKEN", "   ")  # whitespace only
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    assert is_mock_mode(["FAKE_TOKEN"]) is True


def test_plugins_mx_mock_overrides(monkeypatch) -> None:
    monkeypatch.setenv("FAKE_TOKEN", "real-value")
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    assert is_mock_mode(["FAKE_TOKEN"]) is True


def test_multiple_credentials_any_satisfies(monkeypatch) -> None:
    monkeypatch.delenv("TOKEN_A", raising=False)
    monkeypatch.setenv("TOKEN_B", "value")
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    assert is_mock_mode(["TOKEN_A", "TOKEN_B"]) is False


def test_mark_simulated_adds_flag() -> None:
    out = mark_simulated({"value": 18.5})
    assert out["simulated"] is True
    assert out["value"] == 18.5
    assert "advertencias" in out


def test_mark_simulated_does_not_mutate_input() -> None:
    payload = {"v": 1}
    mark_simulated(payload)
    assert "simulated" not in payload  # original untouched


def test_mark_simulated_appends_to_existing_advertencias() -> None:
    out = mark_simulated({"x": 1, "advertencias": ["primero"]}, note="segundo")
    assert out["advertencias"] == ["primero", "segundo"]


def test_mark_simulated_default_advertencia_present() -> None:
    out = mark_simulated({"x": 1})
    assert len(out["advertencias"]) == 1
    assert "simulada" in out["advertencias"][0].lower()
