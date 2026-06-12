"""Validador firma webhooks Conekta.

Conekta soporta 2 formatos:
1. Moderno: `conekta-signature: t=<unix>,v1=<hex_hmac>` (mismo formato que Stripe)
2. Legacy: `Digest: SHA256=<base64_hmac_de_payload>`
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time

from . import ValidationOutcome


def _peek(payload: bytes) -> tuple[str | None, str | None]:
    try:
        data = json.loads(payload.decode("utf-8"))
    except Exception:
        return None, None
    if not isinstance(data, dict):
        return None, None
    return data.get("id"), data.get("type")


def _parse_conekta_sig(header: str) -> tuple[int | None, str | None]:
    ts: int | None = None
    v1: str | None = None
    for part in (header or "").split(","):
        part = part.strip()
        if "=" not in part:
            continue
        k, _, v = part.partition("=")
        k, v = k.strip().lower(), v.strip()
        if k == "t":
            try:
                ts = int(v)
            except ValueError:
                ts = None
        elif k == "v1":
            v1 = v
    return ts, v1


def _parse_digest(header: str) -> str | None:
    if not header:
        return None
    parts = header.split("=", 1)
    if len(parts) != 2:
        return None
    algo, value = parts[0].strip().lower(), parts[1].strip()
    if algo != "sha256":
        return None
    return value or None


def validate(
    *,
    payload: bytes,
    headers: dict[str, str],
    secret: str | None,
    max_age_seconds: int = 300,
    is_mock: bool = False,
) -> ValidationOutcome:
    headers_lower = {k.lower(): v for k, v in (headers or {}).items()}
    body_id, body_type = _peek(payload)

    if is_mock and not secret:
        return ValidationOutcome(True, "mock", body_id, body_type)
    if not secret:
        return ValidationOutcome(False, "missing_secret", body_id, body_type)

    # Formato moderno tiene prioridad
    if "conekta-signature" in headers_lower:
        ts, v1 = _parse_conekta_sig(headers_lower["conekta-signature"])
        if ts is None or v1 is None:
            return ValidationOutcome(False, "malformed_signature_header", body_id, body_type)
        if max_age_seconds and abs(int(time.time()) - ts) > max_age_seconds:
            return ValidationOutcome(False, "expired_timestamp", body_id, body_type)
        signed = f"{ts}.".encode("utf-8") + payload
        computed = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(computed, v1):
            return ValidationOutcome(False, "hmac_mismatch", body_id, body_type)
        return ValidationOutcome(True, None, body_id, body_type)

    if "digest" in headers_lower:
        expected_b64 = _parse_digest(headers_lower["digest"])
        if expected_b64 is None:
            return ValidationOutcome(False, "malformed_signature_header", body_id, body_type)
        computed = base64.b64encode(
            hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).digest()
        ).decode("ascii")
        if not hmac.compare_digest(computed, expected_b64):
            return ValidationOutcome(False, "hmac_mismatch", body_id, body_type)
        return ValidationOutcome(True, None, body_id, body_type)

    return ValidationOutcome(False, "missing_signature_header", body_id, body_type)
