"""Validador firma webhooks Meta WhatsApp Business.

Meta envía `X-Hub-Signature-256: sha256=<hex_hmac>`.
HMAC = HMAC-SHA256(payload_raw, app_secret).
"""

from __future__ import annotations

import hashlib
import hmac
import json

from . import ValidationOutcome


def _peek(payload: bytes) -> tuple[str | None, str | None]:
    try:
        data = json.loads(payload.decode("utf-8"))
    except Exception:
        return None, None
    if not isinstance(data, dict):
        return None, None
    entries = data.get("entry", [])
    event_id = None
    event_type = None
    if isinstance(entries, list) and entries:
        first = entries[0]
        if isinstance(first, dict):
            event_id = first.get("id")
            changes = first.get("changes", [])
            if isinstance(changes, list) and changes:
                ch = changes[0]
                if isinstance(ch, dict):
                    event_type = ch.get("field")
    return event_id, event_type


def validate(
    *,
    payload: bytes,
    headers: dict[str, str],
    secret: str | None,
    is_mock: bool = False,
) -> ValidationOutcome:
    headers_lower = {k.lower(): v for k, v in (headers or {}).items()}
    event_id, event_type = _peek(payload)

    if is_mock and not secret:
        return ValidationOutcome(True, "mock", event_id, event_type)
    if not secret:
        return ValidationOutcome(False, "missing_secret", event_id, event_type)

    sig_header = headers_lower.get("x-hub-signature-256")
    if not sig_header or "=" not in sig_header:
        return ValidationOutcome(False, "missing_signature_header", event_id, event_type)
    algo, _, expected = sig_header.partition("=")
    if algo.strip().lower() != "sha256":
        return ValidationOutcome(False, "malformed_signature_header", event_id, event_type)

    computed = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed, expected.strip()):
        return ValidationOutcome(False, "hmac_mismatch", event_id, event_type)

    return ValidationOutcome(True, None, event_id, event_type)
