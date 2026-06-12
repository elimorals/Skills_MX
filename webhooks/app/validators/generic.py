"""Validadores genéricos para servicios sin HMAC standard.

- `bearer_only`: valida Authorization: Bearer <token>
- `ip_allowlist`: valida que el cliente esté en una lista de IPs/CIDRs
- `no_validation`: para servicios manual-trigger (mock siempre)
"""

from __future__ import annotations

import ipaddress
import json

from . import ValidationOutcome


def _peek(payload: bytes) -> tuple[str | None, str | None]:
    try:
        data = json.loads(payload.decode("utf-8"))
    except Exception:
        return None, None
    if not isinstance(data, dict):
        return None, None
    return data.get("id"), data.get("type") or data.get("event")


def bearer_only(
    *,
    payload: bytes,
    headers: dict[str, str],
    expected_token: str | None,
    is_mock: bool = False,
) -> ValidationOutcome:
    headers_lower = {k.lower(): v for k, v in (headers or {}).items()}
    event_id, event_type = _peek(payload)

    if is_mock and not expected_token:
        return ValidationOutcome(True, "mock", event_id, event_type)
    if not expected_token:
        return ValidationOutcome(False, "missing_secret", event_id, event_type)

    auth = headers_lower.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        return ValidationOutcome(False, "missing_signature_header", event_id, event_type)
    token = auth[7:].strip()
    if token != expected_token:
        return ValidationOutcome(False, "hmac_mismatch", event_id, event_type)
    return ValidationOutcome(True, None, event_id, event_type)


def ip_in_allowlist(client_ip: str, allowlist_csv: str) -> bool:
    if not allowlist_csv.strip():
        return False
    try:
        addr = ipaddress.ip_address(client_ip)
    except ValueError:
        return False
    for entry in allowlist_csv.split(","):
        entry = entry.strip()
        if not entry:
            continue
        try:
            net = ipaddress.ip_network(entry, strict=False)
            if addr in net:
                return True
        except ValueError:
            continue
    return False


def no_validation(
    *, payload: bytes, headers: dict[str, str], is_mock: bool = True
) -> ValidationOutcome:
    """Para servicios manual-trigger. SIEMPRE retorna válido con reason mock."""
    event_id, event_type = _peek(payload)
    return ValidationOutcome(True, "mock", event_id, event_type)
