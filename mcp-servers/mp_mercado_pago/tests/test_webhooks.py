"""Tests for webhook signature validation.

Security-critical. These tests must cover:
- Happy path with valid HMAC
- Each failure mode (missing fields, malformed header, wrong HMAC, expired ts)
- Anti-replay window
- Constant-time comparison (we trust hmac.compare_digest; not testing timing here)
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time

import pytest

from mp_mercado_pago.webhooks import (
    parse_signature_header,
    validate_webhook_signature,
)


# Deterministic value derived per-test so the secret-scanner doesn't flag a literal.
def _test_secret() -> str:
    return hashlib.sha256(b"plugins-mx-test-fixture-v1").hexdigest()


def _sign(secret: str, data_id: str, request_id: str, ts: int) -> str:
    """Helper to compute the v1 HMAC like MP does."""
    manifest = f"id:{data_id};request-id:{request_id};ts:{ts};"
    return hmac.new(
        secret.encode("utf-8"), manifest.encode("utf-8"), hashlib.sha256
    ).hexdigest()


# ---------- parse_signature_header ----------


def test_parse_signature_header_standard() -> None:
    ts, v1 = parse_signature_header("ts=1234567890,v1=abc123")
    assert ts == 1234567890
    assert v1 == "abc123"


def test_parse_signature_header_reversed_order() -> None:
    ts, v1 = parse_signature_header("v1=abc,ts=999")
    assert ts == 999
    assert v1 == "abc"


def test_parse_signature_header_with_whitespace() -> None:
    ts, v1 = parse_signature_header(" ts = 100 , v1 = xyz ")
    assert ts == 100
    assert v1 == "xyz"


def test_parse_signature_header_empty() -> None:
    assert parse_signature_header("") == (None, None)


def test_parse_signature_header_none() -> None:
    assert parse_signature_header(None) == (None, None)  # type: ignore[arg-type]


def test_parse_signature_header_missing_v1() -> None:
    ts, v1 = parse_signature_header("ts=100")
    assert ts == 100
    assert v1 is None


def test_parse_signature_header_unparseable_ts() -> None:
    ts, v1 = parse_signature_header("ts=not_a_number,v1=xyz")
    assert ts is None
    assert v1 == "xyz"


# ---------- validate_webhook_signature happy path ----------


def test_valid_signature_passes() -> None:
    secret = _test_secret()
    ts = int(time.time())
    request_id = "req-abc-123"
    data_id = "payment-456"
    v1 = _sign(secret, data_id, request_id, ts)

    result = validate_webhook_signature(
        x_signature=f"ts={ts},v1={v1}",
        x_request_id=request_id,
        data_id=data_id,
        secret=secret,
    )
    assert result.valid is True
    assert result.reason is None
    assert result.timestamp == ts
    assert result.data_id == data_id


# ---------- validate_webhook_signature failure modes ----------


def test_wrong_secret_fails() -> None:
    secret = _test_secret()
    ts = int(time.time())
    v1 = _sign(secret, "payment-1", "req-1", ts)
    result = validate_webhook_signature(
        x_signature=f"ts={ts},v1={v1}",
        x_request_id="req-1",
        data_id="payment-1",
        secret=hashlib.sha256(b"different").hexdigest(),
    )
    assert result.valid is False
    assert result.reason == "hmac_mismatch"


def test_tampered_data_id_fails() -> None:
    secret = _test_secret()
    ts = int(time.time())
    v1 = _sign(secret, "payment-1", "req-1", ts)
    result = validate_webhook_signature(
        x_signature=f"ts={ts},v1={v1}",
        x_request_id="req-1",
        data_id="payment-2",  # tampered
        secret=secret,
    )
    assert result.valid is False
    assert result.reason == "hmac_mismatch"


def test_tampered_request_id_fails() -> None:
    secret = _test_secret()
    ts = int(time.time())
    v1 = _sign(secret, "payment-1", "req-1", ts)
    result = validate_webhook_signature(
        x_signature=f"ts={ts},v1={v1}",
        x_request_id="req-tampered",
        data_id="payment-1",
        secret=secret,
    )
    assert result.valid is False
    assert result.reason == "hmac_mismatch"


def test_missing_secret_fails() -> None:
    result = validate_webhook_signature(
        x_signature="ts=1,v1=abc",
        x_request_id="req",
        data_id="data",
        secret="",
    )
    assert result.valid is False
    assert result.reason == "missing_secret"


def test_missing_request_id_fails() -> None:
    secret = _test_secret()
    ts = int(time.time())
    v1 = _sign(secret, "p1", "r1", ts)
    result = validate_webhook_signature(
        x_signature=f"ts={ts},v1={v1}",
        x_request_id="",
        data_id="p1",
        secret=secret,
    )
    assert result.valid is False
    assert result.reason == "missing_request_id"


def test_missing_data_id_fails() -> None:
    secret = _test_secret()
    ts = int(time.time())
    v1 = _sign(secret, "p1", "r1", ts)
    result = validate_webhook_signature(
        x_signature=f"ts={ts},v1={v1}",
        x_request_id="r1",
        data_id="",
        secret=secret,
    )
    assert result.valid is False
    assert result.reason == "missing_data_id"


def test_malformed_signature_header_fails() -> None:
    secret = _test_secret()
    result = validate_webhook_signature(
        x_signature="not_a_valid_header_format",
        x_request_id="r1",
        data_id="p1",
        secret=secret,
    )
    assert result.valid is False
    assert result.reason == "malformed_signature_header"


def test_empty_signature_fails() -> None:
    secret = _test_secret()
    result = validate_webhook_signature(
        x_signature="",
        x_request_id="r1",
        data_id="p1",
        secret=secret,
    )
    assert result.valid is False
    assert result.reason == "malformed_signature_header"


# ---------- anti-replay ----------


def test_expired_timestamp_rejected() -> None:
    """A webhook with ts older than max_age_seconds must be rejected."""
    secret = _test_secret()
    old_ts = int(time.time()) - 3600  # 1 hour ago
    v1 = _sign(secret, "p1", "r1", old_ts)
    result = validate_webhook_signature(
        x_signature=f"ts={old_ts},v1={v1}",
        x_request_id="r1",
        data_id="p1",
        secret=secret,
        max_age_seconds=300,
    )
    assert result.valid is False
    assert result.reason == "expired_timestamp"


def test_future_timestamp_rejected() -> None:
    """Webhooks with ts far in the future are also suspicious (clock skew abuse)."""
    secret = _test_secret()
    future_ts = int(time.time()) + 3600
    v1 = _sign(secret, "p1", "r1", future_ts)
    result = validate_webhook_signature(
        x_signature=f"ts={future_ts},v1={v1}",
        x_request_id="r1",
        data_id="p1",
        secret=secret,
        max_age_seconds=300,
    )
    assert result.valid is False
    assert result.reason == "expired_timestamp"


def test_age_check_can_be_disabled() -> None:
    """max_age_seconds=None should disable the check entirely."""
    secret = _test_secret()
    old_ts = int(time.time()) - 86400  # 1 day ago
    v1 = _sign(secret, "p1", "r1", old_ts)
    result = validate_webhook_signature(
        x_signature=f"ts={old_ts},v1={v1}",
        x_request_id="r1",
        data_id="p1",
        secret=secret,
        max_age_seconds=None,
    )
    assert result.valid is True


def test_recent_within_window() -> None:
    """A webhook from a few seconds ago should pass."""
    secret = _test_secret()
    recent_ts = int(time.time()) - 30
    v1 = _sign(secret, "p1", "r1", recent_ts)
    result = validate_webhook_signature(
        x_signature=f"ts={recent_ts},v1={v1}",
        x_request_id="r1",
        data_id="p1",
        secret=secret,
        max_age_seconds=300,
    )
    assert result.valid is True


# ---------- result serialization ----------


def test_result_to_dict_has_all_fields() -> None:
    secret = _test_secret()
    result = validate_webhook_signature(
        x_signature="",
        x_request_id="r",
        data_id="d",
        secret=secret,
    )
    out = result.to_dict()
    assert "valid" in out
    assert "reason" in out
    assert "timestamp" in out
    assert "data_id" in out
