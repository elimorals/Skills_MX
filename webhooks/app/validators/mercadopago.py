"""Validador firma webhooks Mercado Pago.

MP envía:
- `x-signature: ts=<unix>,v1=<hex_hmac>`
- `x-request-id: <guid>`
- Body JSON con `data.id` y `type`

HMAC = HMAC-SHA256(f"id:<data_id>;request-id:<x_req_id>;ts:<ts>;", secret) en hex.

Reusa la lógica del MCP `mp_mercado_pago.webhooks` para consistencia.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time

from . import ValidationOutcome


def _parse_signature(header: str) -> tuple[int | None, str | None]:
    ts: int | None = None
    v1: str | None = None
    for part in (header or "").split(","):
        part = part.strip()
        if "=" not in part:
            continue
        k, _, v = part.partition("=")
        k, v = k.strip().lower(), v.strip()
        if k == "ts":
            try:
                ts = int(v)
            except ValueError:
                ts = None
        elif k == "v1":
            v1 = v
    return ts, v1


def _peek(payload: bytes) -> tuple[str | None, str | None]:
    try:
        data = json.loads(payload.decode("utf-8"))
    except Exception:
        return None, None
    if not isinstance(data, dict):
        return None, None
    data_id = None
    inner = data.get("data")
    if isinstance(inner, dict):
        data_id = inner.get("id")
    return (str(data_id) if data_id is not None else None), data.get("type")


def validate(
    *,
    payload: bytes,
    headers: dict[str, str],
    secret: str | None,
    max_age_seconds: int = 300,
    is_mock: bool = False,
    data_id_query: str | None = None,
) -> ValidationOutcome:
    headers_lower = {k.lower(): v for k, v in (headers or {}).items()}
    sig = headers_lower.get("x-signature")
    req_id = headers_lower.get("x-request-id")
    body_data_id, body_type = _peek(payload)
    data_id = data_id_query or body_data_id

    if is_mock and not secret:
        return ValidationOutcome(True, "mock", data_id, body_type)
    if not secret:
        return ValidationOutcome(False, "missing_secret", data_id, body_type)
    if not sig:
        return ValidationOutcome(False, "missing_signature_header", data_id, body_type)
    if not req_id:
        return ValidationOutcome(False, "missing_request_id", data_id, body_type)
    if not data_id:
        return ValidationOutcome(False, "missing_data_id", data_id, body_type)

    ts, v1 = _parse_signature(sig)
    if ts is None or v1 is None:
        return ValidationOutcome(False, "malformed_signature_header", data_id, body_type)
    if max_age_seconds and abs(int(time.time()) - ts) > max_age_seconds:
        return ValidationOutcome(False, "expired_timestamp", data_id, body_type)

    manifest = f"id:{data_id};request-id:{req_id};ts:{ts};"
    computed = hmac.new(secret.encode("utf-8"), manifest.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed, v1):
        return ValidationOutcome(False, "hmac_mismatch", data_id, body_type)

    return ValidationOutcome(True, None, data_id, body_type)
