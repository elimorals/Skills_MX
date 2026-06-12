"""Tests para mp_conekta/webhooks.py."""

from __future__ import annotations

import base64
import hashlib
import hmac
import time

from mp_conekta.tests.conftest import DEMO_SECRET
from mp_conekta.webhooks import (
    parse_conekta_signature_header,
    parse_digest_header,
    validate_webhook_auto,
    validate_webhook_digest,
    validate_webhook_signature,
)


PAYLOAD = b'{"event":"charge.paid","data":{"object":{"id":"charge_123"}}}'


def _make_digest(payload: bytes, secret: str) -> str:
    mac = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).digest()
    return "SHA256=" + base64.b64encode(mac).decode("ascii")


def _make_signature(payload: bytes, secret: str, ts: int) -> str:
    signed = f"{ts}.".encode("utf-8") + payload
    mac = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()
    return f"t={ts},v1={mac}"


# ---------- parse helpers ----------


def test_parse_digest_header_ok() -> None:
    assert parse_digest_header("SHA256=abcdef==") == "abcdef=="


def test_parse_digest_header_case_insensitive() -> None:
    assert parse_digest_header("sha256=base64here") == "base64here"


def test_parse_digest_header_invalid() -> None:
    assert parse_digest_header("") is None
    assert parse_digest_header("md5=abc") is None
    assert parse_digest_header("sin signo igual") is None


def test_parse_conekta_signature_ok() -> None:
    ts, v1 = parse_conekta_signature_header("t=1234567890,v1=abc123")
    assert ts == 1234567890
    assert v1 == "abc123"


def test_parse_conekta_signature_orden_invertido() -> None:
    ts, v1 = parse_conekta_signature_header("v1=def456,t=999")
    assert ts == 999
    assert v1 == "def456"


def test_parse_conekta_signature_invalido() -> None:
    ts, v1 = parse_conekta_signature_header("malformed")
    assert ts is None
    assert v1 is None


# ---------- digest validation ----------


def test_digest_ok() -> None:
    digest = _make_digest(PAYLOAD, DEMO_SECRET)
    r = validate_webhook_digest(
        digest_header=digest, payload=PAYLOAD, secret=DEMO_SECRET
    )
    assert r.valid is True
    assert r.reason is None
    assert r.signature_format == "digest"


def test_digest_mismatch() -> None:
    bad = _make_digest(PAYLOAD, "wrong_secret")
    r = validate_webhook_digest(
        digest_header=bad, payload=PAYLOAD, secret=DEMO_SECRET
    )
    assert r.valid is False
    assert r.reason == "hmac_mismatch"


def test_digest_missing_secret() -> None:
    r = validate_webhook_digest(
        digest_header="SHA256=abc", payload=PAYLOAD, secret=""
    )
    assert r.valid is False
    assert r.reason == "missing_secret"


def test_digest_malformed_header() -> None:
    r = validate_webhook_digest(
        digest_header="not a digest", payload=PAYLOAD, secret=DEMO_SECRET
    )
    assert r.valid is False
    assert r.reason == "malformed_signature_header"


def test_digest_payload_no_bytes() -> None:
    r = validate_webhook_digest(
        digest_header="SHA256=abc",
        payload="esto es string no bytes",  # type: ignore[arg-type]
        secret=DEMO_SECRET,
    )
    assert r.valid is False
    assert r.reason == "payload_must_be_bytes"


# ---------- conekta-signature validation ----------


def test_signature_ok() -> None:
    ts = int(time.time())
    sig = _make_signature(PAYLOAD, DEMO_SECRET, ts)
    r = validate_webhook_signature(
        signature_header=sig, payload=PAYLOAD, secret=DEMO_SECRET
    )
    assert r.valid is True
    assert r.timestamp == ts


def test_signature_expired() -> None:
    ts = int(time.time()) - 600  # 10 min atrás
    sig = _make_signature(PAYLOAD, DEMO_SECRET, ts)
    r = validate_webhook_signature(
        signature_header=sig, payload=PAYLOAD, secret=DEMO_SECRET, max_age_seconds=300
    )
    assert r.valid is False
    assert r.reason == "expired_timestamp"


def test_signature_no_max_age_accepts_old() -> None:
    ts = int(time.time()) - 10000
    sig = _make_signature(PAYLOAD, DEMO_SECRET, ts)
    r = validate_webhook_signature(
        signature_header=sig, payload=PAYLOAD, secret=DEMO_SECRET, max_age_seconds=None
    )
    assert r.valid is True


def test_signature_hmac_mismatch() -> None:
    ts = int(time.time())
    sig = _make_signature(PAYLOAD, "wrong_secret", ts)
    r = validate_webhook_signature(
        signature_header=sig, payload=PAYLOAD, secret=DEMO_SECRET
    )
    assert r.valid is False
    assert r.reason == "hmac_mismatch"


def test_signature_malformed() -> None:
    r = validate_webhook_signature(
        signature_header="no es signature", payload=PAYLOAD, secret=DEMO_SECRET
    )
    assert r.valid is False
    assert r.reason == "malformed_signature_header"


# ---------- auto-detection ----------


def test_auto_prefers_conekta_signature() -> None:
    ts = int(time.time())
    sig = _make_signature(PAYLOAD, DEMO_SECRET, ts)
    digest = _make_digest(PAYLOAD, "different_secret")  # mal
    r = validate_webhook_auto(
        headers={"conekta-signature": sig, "Digest": digest},
        payload=PAYLOAD,
        secret=DEMO_SECRET,
    )
    # Debe usar conekta-signature (válido) NO Digest (inválido)
    assert r.valid is True
    assert r.signature_format == "conekta-signature"


def test_auto_falls_back_to_digest() -> None:
    digest = _make_digest(PAYLOAD, DEMO_SECRET)
    r = validate_webhook_auto(
        headers={"Digest": digest},
        payload=PAYLOAD,
        secret=DEMO_SECRET,
    )
    assert r.valid is True
    assert r.signature_format == "digest"


def test_auto_no_signature_headers() -> None:
    r = validate_webhook_auto(
        headers={"User-Agent": "Conekta"},
        payload=PAYLOAD,
        secret=DEMO_SECRET,
    )
    assert r.valid is False
    assert r.reason == "missing_signature_header"


def test_auto_case_insensitive_headers() -> None:
    digest = _make_digest(PAYLOAD, DEMO_SECRET)
    r = validate_webhook_auto(
        headers={"digest": digest},  # lowercase
        payload=PAYLOAD,
        secret=DEMO_SECRET,
    )
    assert r.valid is True
