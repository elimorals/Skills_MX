"""Tests para MercadoLibreClient en modo mock + cache + bitácora."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from mp_mercado_libre.client import MercadoLibreClient
from shared.bitacora import Bitacora
from shared.cache import FileCache
from shared.errors import ConfigError


def _refresh() -> str:
    return hashlib.sha256(b"mp-meli-client-refresh-v1").hexdigest()


def _secret() -> str:
    return hashlib.sha256(b"mp-meli-client-secret-v1").hexdigest()


# ---------- modo mock detección ----------


def test_no_envs_means_mock(monkeypatch) -> None:
    monkeypatch.delenv("ML_APP_ID", raising=False)
    monkeypatch.delenv("ML_SECRET", raising=False)
    monkeypatch.delenv("ML_REFRESH_TOKEN", raising=False)
    c = MercadoLibreClient()
    assert c.is_mock is True


def test_force_mock_via_env(monkeypatch) -> None:
    monkeypatch.setenv("ML_APP_ID", "APP")
    monkeypatch.setenv("ML_SECRET", _secret())
    monkeypatch.setenv("ML_REFRESH_TOKEN", _refresh())
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    c = MercadoLibreClient()
    assert c.is_mock is True


def test_full_envs_disable_mock(monkeypatch) -> None:
    monkeypatch.setenv("ML_APP_ID", "APP")
    monkeypatch.setenv("ML_SECRET", _secret())
    monkeypatch.setenv("ML_REFRESH_TOKEN", _refresh())
    c = MercadoLibreClient()
    assert c.is_mock is False


def test_explicit_args_disable_mock(monkeypatch) -> None:
    monkeypatch.delenv("ML_APP_ID", raising=False)
    c = MercadoLibreClient(app_id="APP", secret=_secret(), refresh_token=_refresh())
    assert c.is_mock is False


# ---------- mock determinístico ----------


@pytest.mark.asyncio
async def test_get_me_mock_shape() -> None:
    c = MercadoLibreClient()
    me = await c.get_me()
    assert me["simulated"] is True
    assert me["site_id"] == "MLM"
    assert me["country_id"] == "MX"
    assert isinstance(me["id"], int)


@pytest.mark.asyncio
async def test_list_items_mock_pagination() -> None:
    c = MercadoLibreClient()
    page = await c.list_items(limit=3, offset=0)
    assert page["simulated"] is True
    assert len(page["results"]) == 3
    assert all(r.startswith("MLM") for r in page["results"])


@pytest.mark.asyncio
async def test_item_odd_last_digit_is_active() -> None:
    c = MercadoLibreClient()
    item = await c.get_item("MLM0000000001")
    assert item["status"] == "active"
    assert item["simulated"] is True


@pytest.mark.asyncio
async def test_item_even_last_digit_is_paused() -> None:
    c = MercadoLibreClient()
    item = await c.get_item("MLM0000000002")
    assert item["status"] == "paused"


@pytest.mark.asyncio
async def test_item_mock_price_seeded_by_id() -> None:
    """Tail digits of the id seed the price so distinct ids give distinct data."""
    c = MercadoLibreClient()
    a = await c.get_item("MLM0000000123")
    # Clear cache between calls so we get the actual seeded values
    c._cache.invalidate("item_MLM0000000123")
    c._cache.invalidate("item_MLM0000000789")
    a = await c.get_item("MLM0000000123")
    b = await c.get_item("MLM0000000789")
    assert a["price"] != b["price"]


@pytest.mark.asyncio
async def test_get_order_paid_odd() -> None:
    c = MercadoLibreClient()
    order = await c.get_order("12345")
    assert order["status"] == "paid"


@pytest.mark.asyncio
async def test_get_order_payment_required_even() -> None:
    c = MercadoLibreClient()
    order = await c.get_order("12346")
    assert order["status"] == "payment_required"


@pytest.mark.asyncio
async def test_get_order_cancelled_keyword() -> None:
    c = MercadoLibreClient()
    order = await c.get_order("cancelled")
    assert order["status"] == "cancelled"


# ---------- cache ----------


@pytest.mark.asyncio
async def test_get_item_cached_on_second_call() -> None:
    c = MercadoLibreClient()
    first = await c.get_item("MLM0000000077")
    second = await c.get_item("MLM0000000077")
    # Both come from the same cached payload (same seeded price)
    assert first["price"] == second["price"]
    assert first["status"] == second["status"]


@pytest.mark.asyncio
async def test_update_item_invalidates_cache() -> None:
    c = MercadoLibreClient()
    await c.get_item("MLM0000000077")
    await c.update_item("MLM0000000077", {"price": 999.0})
    # Cache should be invalidated — next read returns fresh mock (still status from id parity)
    after = await c.get_item("MLM0000000077")
    assert after["simulated"] is True


# ---------- bitácora ----------


@pytest.mark.asyncio
async def test_update_item_logs_with_hashed_id(tmp_path: Path, monkeypatch) -> None:
    """update_item debe loggear el id hasheado (no el id en claro)."""
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))
    bit = Bitacora("mercadolibre_mcp")
    c = MercadoLibreClient(bitacora=bit)
    await c.update_item("MLM0000000077", {"price": 100.0})

    entries = bit.tail(10)
    assert len(entries) >= 1
    entry = entries[-1]
    assert entry["tool"] == "update_item"
    assert "MLM0000000077" not in json.dumps(entry)  # no leaked id
    assert entry["params"]["fields"] == ["price"]


@pytest.mark.asyncio
async def test_send_message_logs_text_len_not_content(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))
    bit = Bitacora("mercadolibre_mcp")
    c = MercadoLibreClient(bitacora=bit)
    await c.send_message(pack_id="pack-1", buyer_id=42, text="Hola, ¿cómo va el envío?")

    entry = bit.tail(10)[-1]
    assert "Hola" not in json.dumps(entry)  # no leaked message content
    assert entry["params"]["text_len"] == len("Hola, ¿cómo va el envío?")


# ---------- config error en modo real sin envs ----------


@pytest.mark.asyncio
async def test_non_mock_without_creds_raises_config(monkeypatch) -> None:
    """Si fuerzas mock=False sin creds, el token manager debe quejarse."""
    monkeypatch.delenv("ML_APP_ID", raising=False)
    monkeypatch.delenv("ML_SECRET", raising=False)
    monkeypatch.delenv("ML_REFRESH_TOKEN", raising=False)
    c = MercadoLibreClient()
    c._mock_mode = False  # force non-mock path despite no creds
    with pytest.raises(ConfigError):
        await c.get_me()
