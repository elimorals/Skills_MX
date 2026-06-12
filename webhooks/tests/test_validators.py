import hashlib
import hmac
import json
import time

from app.validators import stripe as v_stripe
from app.validators import mercadopago as v_mp
from app.validators import conekta as v_conekta
from app.validators import github as v_github
from app.validators import meta_whatsapp as v_meta
from app.validators import generic as v_generic


# ---------- Stripe ----------

def _stripe_sign(payload: bytes, secret: str, ts: int | None = None) -> str:
    ts = ts or int(time.time())
    signed = f"{ts}.".encode() + payload
    digest = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return f"t={ts},v1={digest}"


def test_stripe_valid_signature():
    payload = json.dumps({"id": "evt_1", "type": "payment_intent.succeeded"}).encode()
    sig = _stripe_sign(payload, "shh")
    res = v_stripe.validate(
        payload=payload, headers={"stripe-signature": sig}, secret="shh"
    )
    assert res.valid is True
    assert res.event_id == "evt_1"


def test_stripe_invalid_signature_hmac_mismatch():
    payload = json.dumps({"id": "evt_1", "type": "x"}).encode()
    bad_sig = f"t={int(time.time())},v1=0000"
    res = v_stripe.validate(
        payload=payload, headers={"stripe-signature": bad_sig}, secret="shh"
    )
    assert res.valid is False
    assert res.reason == "hmac_mismatch"


def test_stripe_mock_mode_no_secret():
    payload = b'{"id":"evt_1"}'
    res = v_stripe.validate(payload=payload, headers={}, secret=None, is_mock=True)
    assert res.valid is True
    assert res.reason == "mock"


def test_stripe_replay_rejected():
    payload = b'{"id":"evt_1"}'
    old_ts = int(time.time()) - 10_000
    sig = _stripe_sign(payload, "shh", ts=old_ts)
    res = v_stripe.validate(
        payload=payload, headers={"stripe-signature": sig}, secret="shh"
    )
    assert res.valid is False
    assert res.reason == "expired_timestamp"


# ---------- Mercado Pago ----------

def test_mercadopago_valid():
    payload = json.dumps({"type": "payment", "data": {"id": "123456"}}).encode()
    ts = int(time.time())
    req_id = "req-guid-1"
    manifest = f"id:123456;request-id:{req_id};ts:{ts};"
    digest = hmac.new(b"mpsecret", manifest.encode(), hashlib.sha256).hexdigest()
    headers = {
        "x-signature": f"ts={ts},v1={digest}",
        "x-request-id": req_id,
    }
    res = v_mp.validate(payload=payload, headers=headers, secret="mpsecret")
    assert res.valid is True
    assert res.event_id == "123456"


def test_mercadopago_missing_request_id():
    payload = json.dumps({"type": "payment", "data": {"id": "1"}}).encode()
    res = v_mp.validate(
        payload=payload,
        headers={"x-signature": "ts=1,v1=abc"},
        secret="x",
    )
    assert res.valid is False


# ---------- Conekta ----------

def test_conekta_digest_valid():
    import base64

    payload = json.dumps({"type": "charge.paid", "id": "ch_1"}).encode()
    digest = base64.b64encode(
        hmac.new(b"cnk", payload, hashlib.sha256).digest()
    ).decode("ascii")
    res = v_conekta.validate(
        payload=payload, headers={"digest": f"SHA256={digest}"}, secret="cnk"
    )
    assert res.valid is True


def test_conekta_modern_signature_valid():
    payload = json.dumps({"id": "ch_2", "type": "charge.paid"}).encode()
    ts = int(time.time())
    signed = f"{ts}.".encode() + payload
    digest = hmac.new(b"cnk", signed, hashlib.sha256).hexdigest()
    headers = {"conekta-signature": f"t={ts},v1={digest}"}
    res = v_conekta.validate(payload=payload, headers=headers, secret="cnk")
    assert res.valid is True


# ---------- GitHub ----------

def test_github_valid():
    payload = b'{"action":"push"}'
    digest = hmac.new(b"gh", payload, hashlib.sha256).hexdigest()
    headers = {
        "x-hub-signature-256": f"sha256={digest}",
        "x-github-delivery": "guid-1",
        "x-github-event": "push",
    }
    res = v_github.validate(payload=payload, headers=headers, secret="gh")
    assert res.valid is True
    assert res.event_id == "guid-1"


# ---------- Meta WhatsApp ----------

def test_meta_whatsapp_valid():
    payload = json.dumps(
        {"entry": [{"id": "ent1", "changes": [{"field": "messages"}]}]}
    ).encode()
    digest = hmac.new(b"meta", payload, hashlib.sha256).hexdigest()
    headers = {"x-hub-signature-256": f"sha256={digest}"}
    res = v_meta.validate(payload=payload, headers=headers, secret="meta")
    assert res.valid is True


# ---------- Generic IP allowlist ----------

def test_ip_in_allowlist_cidr():
    assert v_generic.ip_in_allowlist("200.94.0.5", "200.94.0.0/24")
    assert not v_generic.ip_in_allowlist("8.8.8.8", "200.94.0.0/24")
    assert v_generic.ip_in_allowlist("10.0.0.1", "10.0.0.1, 192.168.0.0/16")
    assert not v_generic.ip_in_allowlist("not-an-ip", "10.0.0.0/8")


def test_bearer_valid():
    res = v_generic.bearer_only(
        payload=b"{}",
        headers={"authorization": "Bearer mytoken"},
        expected_token="mytoken",
    )
    assert res.valid is True


def test_bearer_mismatch():
    res = v_generic.bearer_only(
        payload=b"{}",
        headers={"authorization": "Bearer wrong"},
        expected_token="right",
    )
    assert res.valid is False
    assert res.reason == "hmac_mismatch"
