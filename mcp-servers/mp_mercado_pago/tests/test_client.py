"""Tests for MercadoPagoClient — mock determinism, cache, env detection."""

from __future__ import annotations

import pytest

from mp_mercado_pago.client import MercadoPagoClient
from shared.errors import ConfigError


# ---------- construction ----------


def test_defaults_to_mock_without_token() -> None:
    c = MercadoPagoClient()
    assert c.is_mock is True
    assert c.environment == "mock"


def test_explicit_token_enables_real_mode() -> None:
    c = MercadoPagoClient(access_token="TEST-something")
    assert c.is_mock is False
    assert c.environment == "sandbox"


def test_production_token_detected() -> None:
    c = MercadoPagoClient(access_token="APP_USR-something")
    assert c.is_mock is False
    assert c.environment == "production"


def test_env_token_enables_real_mode(monkeypatch) -> None:
    monkeypatch.setenv("MERCADOPAGO_ACCESS_TOKEN", "TEST-abc")
    c = MercadoPagoClient()
    assert c.is_mock is False
    assert c.environment == "sandbox"


def test_plugins_mx_mock_overrides_real_creds(monkeypatch) -> None:
    monkeypatch.setenv("MERCADOPAGO_ACCESS_TOKEN", "TEST-abc")
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    c = MercadoPagoClient()
    assert c.is_mock is True


def test_unknown_token_prefix_marked_as_unknown() -> None:
    c = MercadoPagoClient(access_token="WEIRD-prefix-xxx")
    assert c.environment == "unknown"


# ---------- create_preference (mock) ----------


async def test_mock_create_preference_returns_id(simple_preference: dict) -> None:
    c = MercadoPagoClient()
    result = await c.create_preference(simple_preference)
    assert result["simulated"] is True
    assert result["preference_id"]
    assert "init_point" in result
    assert "sandbox" in result["init_point"]


async def test_mock_create_preference_deterministic(simple_preference: dict) -> None:
    """Same input → same preference_id (useful for tests)."""
    c1 = MercadoPagoClient()
    c2 = MercadoPagoClient()
    r1 = await c1.create_preference(simple_preference)
    r2 = await c2.create_preference(simple_preference)
    assert r1["preference_id"] == r2["preference_id"]


async def test_mock_create_preference_different_input_different_id(
    simple_preference: dict,
) -> None:
    """Different input → different id."""
    c = MercadoPagoClient()
    other = dict(simple_preference)
    other["external_reference"] = "different-ref"
    r1 = await c.create_preference(simple_preference)
    r2 = await c.create_preference(other)
    assert r1["preference_id"] != r2["preference_id"]


async def test_mock_create_preference_preserves_external_reference(
    simple_preference: dict,
) -> None:
    c = MercadoPagoClient()
    result = await c.create_preference(simple_preference)
    assert result["external_reference"] == simple_preference["external_reference"]


async def test_mock_create_preference_writes_bitacora(simple_preference: dict) -> None:
    c = MercadoPagoClient()
    await c.create_preference(simple_preference)
    entries = c._bitacora.tail()
    assert any(e["tool"] == "create_preference" for e in entries)


async def test_mock_create_preference_hashes_external_reference_in_bitacora(
    simple_preference: dict,
) -> None:
    """External reference must not leak raw into bitacora."""
    c = MercadoPagoClient()
    await c.create_preference(simple_preference)
    entries = c._bitacora.tail()
    raw_ref = simple_preference["external_reference"]
    for e in entries:
        assert raw_ref not in str(e), f"Raw external_reference leaked: {raw_ref}"


# ---------- get_payment (mock) ----------


async def test_mock_get_payment_approved_for_odd_id() -> None:
    c = MercadoPagoClient()
    result = await c.get_payment("1")
    assert result["simulated"] is True
    assert result["status"] == "approved"


async def test_mock_get_payment_pending_for_even_id() -> None:
    c = MercadoPagoClient()
    result = await c.get_payment("2")
    assert result["status"] == "pending"


async def test_mock_get_payment_rejected_for_special_id() -> None:
    c = MercadoPagoClient()
    result = await c.get_payment("reject")
    assert result["status"] == "rejected"


async def test_mock_get_payment_uses_cache() -> None:
    """Second call → from cache (verified by flipping to real mode without token)."""
    c = MercadoPagoClient()
    r1 = await c.get_payment("1")

    c._mock_mode = False
    c._access_token = None
    r2 = await c.get_payment("1")
    assert r1["id"] == r2["id"]
    assert r1["status"] == r2["status"]


# ---------- list_payments (mock) ----------


async def test_mock_list_payments_returns_empty() -> None:
    c = MercadoPagoClient()
    result = await c.list_payments(external_reference="abc")
    assert result["simulated"] is True
    assert result["results"] == []


# ---------- refund (mock) ----------


async def test_mock_refund_full() -> None:
    c = MercadoPagoClient()
    result = await c.refund_payment("123")
    assert result["simulated"] is True
    assert result["amount"] is None  # None = full refund
    assert result["status"] == "approved"


async def test_mock_refund_partial() -> None:
    c = MercadoPagoClient()
    result = await c.refund_payment("123", amount=50.0)
    assert result["amount"] == 50.0
    assert result["status"] == "approved"


async def test_mock_refund_writes_bitacora() -> None:
    c = MercadoPagoClient()
    await c.refund_payment("789", amount=25.0)
    entries = c._bitacora.tail()
    assert any(
        e["tool"] == "refund_payment" and e["params"]["is_partial"] is True
        for e in entries
    )


# ---------- cancel (mock) ----------


async def test_mock_cancel_returns_cancelled() -> None:
    c = MercadoPagoClient()
    result = await c.cancel_payment("123")
    assert result["status"] == "cancelled"
    assert result["simulated"] is True


# ---------- real mode requires token ----------


async def test_real_mode_without_token_raises_config_error(simple_preference: dict) -> None:
    c = MercadoPagoClient(access_token="TEST-foo")  # real mode
    c._access_token = None  # but then null it
    with pytest.raises(ConfigError):
        await c.create_preference(simple_preference)


async def test_real_mode_get_payment_without_token_raises() -> None:
    c = MercadoPagoClient(access_token="TEST-foo")
    c._access_token = None
    with pytest.raises(ConfigError):
        await c.get_payment("123")
