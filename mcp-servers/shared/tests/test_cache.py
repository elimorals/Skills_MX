"""Tests for shared.cache.FileCache.

These tests run without network/credentials. They use a tmp directory via
the PLUGINS_MX_CACHE_DIR env var trick.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

from shared.cache import FileCache


@pytest.fixture
def cache(tmp_path: Path) -> FileCache:
    """Fresh FileCache rooted under a tmp path."""
    return FileCache("test_ns", root=tmp_path)


def test_set_and_get_roundtrip(cache: FileCache) -> None:
    cache.set("k1", {"hello": "world"}, ttl_hours=1)
    assert cache.get("k1") == {"hello": "world"}


def test_missing_key_returns_none(cache: FileCache) -> None:
    assert cache.get("nope") is None


def test_expired_entry_returns_none(cache: FileCache) -> None:
    cache.set("k1", "v", ttl_minutes=0.001)  # ~60ms
    time.sleep(0.2)
    assert cache.get("k1") is None


def test_expired_entry_is_deleted_on_read(cache: FileCache, tmp_path: Path) -> None:
    cache.set("k1", "v", ttl_minutes=0.001)
    time.sleep(0.2)
    cache.get("k1")  # triggers cleanup
    # File should be gone
    assert list((tmp_path / "test_ns").glob("k1*.json")) == []


def test_invalidate_drops_entry(cache: FileCache) -> None:
    cache.set("k1", "v", ttl_hours=24)
    cache.invalidate("k1")
    assert cache.get("k1") is None


def test_invalidate_missing_key_is_noop(cache: FileCache) -> None:
    cache.invalidate("never-existed")  # should not raise


def test_clear_drops_all_entries(cache: FileCache) -> None:
    cache.set("a", 1, ttl_hours=1)
    cache.set("b", 2, ttl_hours=1)
    cache.set("c", 3, ttl_hours=1)
    removed = cache.clear()
    assert removed == 3
    assert cache.get("a") is None
    assert cache.get("b") is None


def test_long_key_is_hashed(tmp_path: Path) -> None:
    cache = FileCache("test_ns", root=tmp_path)
    long_key = "x" * 200
    cache.set(long_key, "payload", ttl_hours=1)
    # Stored file name uses hash, but get() still works via same hashing
    assert cache.get(long_key) == "payload"


def test_unicode_key_is_hashed(tmp_path: Path) -> None:
    cache = FileCache("test_ns", root=tmp_path)
    cache.set("café/año", "ok", ttl_hours=1)
    assert cache.get("café/año") == "ok"


def test_namespace_isolation(tmp_path: Path) -> None:
    c1 = FileCache("ns1", root=tmp_path)
    c2 = FileCache("ns2", root=tmp_path)
    c1.set("k", "from_ns1", ttl_hours=1)
    assert c2.get("k") is None


def test_corrupted_file_returns_none(cache: FileCache, tmp_path: Path) -> None:
    # Plant a corrupted cache file directly
    bad_path = tmp_path / "test_ns" / "broken.json"
    bad_path.write_text("not valid json {{{")
    assert cache.get("broken") is None
    assert not bad_path.exists()  # corrupted file gets removed


def test_no_ttl_means_no_expiration(cache: FileCache) -> None:
    cache.set("k", "v")  # no ttl_* passed
    assert cache.get("k") == "v"


def test_multiple_ttl_params_raise(cache: FileCache) -> None:
    with pytest.raises(ValueError):
        cache.set("k", "v", ttl_hours=1, ttl_minutes=5)


def test_invalid_namespace_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        FileCache("", root=tmp_path)
    with pytest.raises(ValueError):
        FileCache("bad/ns", root=tmp_path)


def test_keys_lists_live_entries(cache: FileCache) -> None:
    cache.set("a", 1, ttl_hours=1)
    cache.set("b", 2, ttl_hours=1)
    assert set(cache.keys()) == {"a", "b"}


def test_stats_returns_summary(cache: FileCache) -> None:
    cache.set("a", "hello", ttl_hours=1)
    s = cache.stats()
    assert s["namespace"] == "test_ns"
    assert s["entries"] == 1
    assert s["bytes"] > 0


def test_env_var_overrides_root(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "via_env"))
    c = FileCache("test_ns")
    c.set("k", "v", ttl_hours=1)
    assert (tmp_path / "via_env" / "test_ns" / "k.json").exists()


def test_atomic_write_does_not_leave_tmp(cache: FileCache, tmp_path: Path) -> None:
    cache.set("k", "v", ttl_hours=1)
    # No .tmp files should remain after a successful write
    tmps = list((tmp_path / "test_ns").glob("*.tmp"))
    assert tmps == []


def test_stored_file_is_valid_json(cache: FileCache, tmp_path: Path) -> None:
    cache.set("k", {"a": 1}, ttl_hours=1)
    path = tmp_path / "test_ns" / "k.json"
    raw = json.loads(path.read_text())
    assert raw["payload"] == {"a": 1}
    assert "stored_at" in raw
    assert "expires_at" in raw
