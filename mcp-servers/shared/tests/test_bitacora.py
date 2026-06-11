"""Tests for shared.bitacora.Bitacora."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from shared.bitacora import Bitacora


@pytest.fixture
def bitacora(tmp_path: Path) -> Bitacora:
    return Bitacora("test_ns", root=tmp_path)


def test_log_writes_line(bitacora: Bitacora) -> None:
    bitacora.log("my_tool", success=True, duration_ms=12.3)
    entries = bitacora.tail()
    assert len(entries) == 1
    assert entries[0]["tool"] == "my_tool"
    assert entries[0]["success"] is True
    assert entries[0]["duration_ms"] == 12.3


def test_log_with_params_and_result(bitacora: Bitacora) -> None:
    bitacora.log(
        "get_thing",
        success=True,
        params_summary={"id_hash": "abc123"},
        result_summary={"count": 5},
    )
    e = bitacora.tail()[0]
    assert e["params"] == {"id_hash": "abc123"}
    assert e["result"] == {"count": 5}


def test_log_with_error(bitacora: Bitacora) -> None:
    bitacora.log(
        "broken_tool",
        success=False,
        error={"code": "auth_error", "message": "bad creds"},
    )
    e = bitacora.tail()[0]
    assert e["success"] is False
    assert e["error"]["code"] == "auth_error"


def test_multiple_logs_appear_in_order(bitacora: Bitacora) -> None:
    bitacora.log("a", success=True)
    bitacora.log("b", success=True)
    bitacora.log("c", success=True)
    entries = bitacora.tail()
    assert [e["tool"] for e in entries] == ["a", "b", "c"]


def test_tail_limit(bitacora: Bitacora) -> None:
    for i in range(10):
        bitacora.log(f"tool_{i}", success=True)
    last3 = bitacora.tail(n=3)
    assert len(last3) == 3
    assert [e["tool"] for e in last3] == ["tool_7", "tool_8", "tool_9"]


def test_hash_sensitive_is_stable() -> None:
    h1 = Bitacora.hash_sensitive("RFC123456")
    h2 = Bitacora.hash_sensitive("RFC123456")
    assert h1 == h2
    assert h1 is not None
    assert len(h1) == 12


def test_hash_sensitive_differs_for_different_inputs() -> None:
    assert Bitacora.hash_sensitive("a") != Bitacora.hash_sensitive("b")


def test_hash_sensitive_none_returns_none() -> None:
    assert Bitacora.hash_sensitive(None) is None


def test_entries_are_valid_jsonl(bitacora: Bitacora, tmp_path: Path) -> None:
    bitacora.log("a", success=True, params_summary={"key": "val"})
    bitacora.log("b", success=False, error={"code": "x", "message": "y"})

    # Find the file
    files = list((tmp_path / "test_ns").glob("*.jsonl"))
    assert len(files) == 1

    lines = files[0].read_text().splitlines()
    assert len(lines) == 2
    for line in lines:
        parsed = json.loads(line)  # must be valid JSON each
        assert "ts" in parsed


def test_invalid_namespace_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        Bitacora("", root=tmp_path)
    with pytest.raises(ValueError):
        Bitacora("bad/ns", root=tmp_path)


def test_tail_on_empty_returns_empty(bitacora: Bitacora) -> None:
    assert bitacora.tail() == []
