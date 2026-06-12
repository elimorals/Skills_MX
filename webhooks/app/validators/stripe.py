"""Validador firma webhooks Stripe.

Stripe envía header `Stripe-Signature: t=<unix>,v1=<hex_hmac>[,v0=...]`.
HMAC se calcula sobre `{t}.{payload_raw}` con el webhook secret.

Docs: https://stripe.com/docs/webhooks/signatures
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time

from . import ValidationOutcome


def _parse_signature(header: str) -> tuple[int | None, list[str]]:
    """Extrae (ts, [v1_hashes]) del header."""
    ts: int | None = None
    v1s: list[str] = []
    for part in (header or "").split(","):
        part = part.strip()
        if not part or "=" not in part:
            continue
        key, _, value = part.partition("=")
        key, value = key.strip().lower(), value.strip()
        if key == "t":
            try:
                ts = int(value)
            except ValueError:
                ts = None
        elif key == "v1":
            v1s.append(value)
    return ts, v1s


def validate(
    *,
    payload: bytes,
    headers: dict[str, str],
    secret: str | None,
    max_age_seconds: int = 300,
    is_mock: bool = False,
) -> ValidationOutcome:
    headers_lower = {k.lower(): v for k, v in (headers or {}).items()}
    sig_header = headers_lower.get("stripe-signature")
    body_event_id, body_event_type = _peek_event(payload)

    if is_mock and not secret:
        return ValidationOutcome(True, "mock", body_event_id, body_event_type)

    if not secret:
        return ValidationOutcome(False, "missing_secret", body_event_id, body_event_type)
    if not sig_header:
        return ValidationOutcome(False, "missing_signature_header", body_event_id, body_event_type)

    ts, v1s = _parse_signature(sig_header)
    if ts is None or not v1s:
        return ValidationOutcome(False, "malformed_signature_header", body_event_id, body_event_type)

    if max_age_seconds and abs(int(time.time()) - ts) > max_age_seconds:
        return ValidationOutcome(False, "expired_timestamp", body_event_id, body_event_type)

    signed = f"{ts}.".encode("utf-8") + payload
    computed = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()
    if not any(hmac.compare_digest(computed, v) for v in v1s):
        return ValidationOutcome(False, "hmac_mismatch", body_event_id, body_event_type)

    return ValidationOutcome(True, None, body_event_id, body_event_type)


def _peek_event(payload: bytes) -> tuple[str | None, str | None]:
    """Lee event_id + event_type del payload sin validar (best-effort)."""
    try:
        data = json.loads(payload.decode("utf-8"))
    except Exception:
        return None, None
    if not isinstance(data, dict):
        return None, None
    return data.get("id"), data.get("type")
