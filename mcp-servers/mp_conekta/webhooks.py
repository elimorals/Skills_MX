"""Validación de firma de webhooks Conekta.

Conekta firma cada webhook con HMAC-SHA256 sobre el payload crudo (body bytes).

El header usado es `Digest` con formato `SHA256=<base64_hmac>` cuando la cuenta
tiene "firma de webhook" activada en el panel.

Alternativa moderna (algunas cuentas): header `conekta-signature` con formato
similar a Stripe: `t=<unix>,v1=<hex_hmac>`.

Esta capa soporta AMBOS formatos. Si el header no se reconoce, retorna
`malformed_signature_header`.

⚠ Sin validar firma, cualquiera puede mandar POSTs falsos al endpoint y
disparar acciones (timbrar CFDI, registrar pago) por eventos que no ocurrieron.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class WebhookValidationResult:
    """Resultado de validar una firma de webhook Conekta."""

    valid: bool
    reason: str | None  # None si valid; explicación si no
    timestamp: int | None  # ts si el header lo trae (formato moderno)
    signature_format: str | None  # "digest" | "conekta-signature" | None

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "signature_format": self.signature_format,
        }


def parse_digest_header(digest: str) -> str | None:
    """Extrae el hash base64 del header `Digest: SHA256=<base64>`.

    Tolera espacios y mayúsculas variantes. Retorna None si no parsea.
    """
    if not digest or not isinstance(digest, str):
        return None
    parts = digest.strip().split("=", 1)
    if len(parts) != 2:
        return None
    algo, value = parts[0].strip().lower(), parts[1].strip()
    if algo != "sha256":
        return None
    return value or None


def parse_conekta_signature_header(header: str) -> tuple[int | None, str | None]:
    """Extrae (ts, v1) del header `conekta-signature: t=...,v1=...`.

    Mismo formato que Stripe. Tolera espacios.
    """
    if not header or not isinstance(header, str):
        return None, None

    ts: int | None = None
    v1: str | None = None
    for part in header.split(","):
        part = part.strip()
        if not part or "=" not in part:
            continue
        key, _, value = part.partition("=")
        key = key.strip().lower()
        value = value.strip()
        if key == "t":
            try:
                ts = int(value)
            except ValueError:
                ts = None
        elif key == "v1":
            v1 = value
    return ts, v1


def validate_webhook_digest(
    *,
    digest_header: str,
    payload: bytes,
    secret: str,
) -> WebhookValidationResult:
    """Valida usando formato `Digest: SHA256=<base64>`.

    El base64 es del HMAC-SHA256(payload, secret) — el payload son los bytes
    crudos del body, sin re-serializar.
    """
    if not secret:
        return WebhookValidationResult(False, "missing_secret", None, "digest")

    expected_b64 = parse_digest_header(digest_header)
    if expected_b64 is None:
        return WebhookValidationResult(
            False, "malformed_signature_header", None, "digest"
        )

    if not isinstance(payload, (bytes, bytearray)):
        return WebhookValidationResult(False, "payload_must_be_bytes", None, "digest")

    computed = base64.b64encode(
        hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).digest()
    ).decode("ascii")

    if not hmac.compare_digest(computed, expected_b64):
        return WebhookValidationResult(False, "hmac_mismatch", None, "digest")

    return WebhookValidationResult(True, None, None, "digest")


def validate_webhook_signature(
    *,
    signature_header: str,
    payload: bytes,
    secret: str,
    max_age_seconds: int | None = 300,
) -> WebhookValidationResult:
    """Valida usando formato `conekta-signature: t=...,v1=...`.

    v1 es HMAC-SHA256(f"{ts}.{payload_str}", secret) en hex.
    """
    if not secret:
        return WebhookValidationResult(False, "missing_secret", None, "conekta-signature")

    ts, v1 = parse_conekta_signature_header(signature_header)
    if ts is None or v1 is None:
        return WebhookValidationResult(
            False, "malformed_signature_header", ts, "conekta-signature"
        )

    if not isinstance(payload, (bytes, bytearray)):
        return WebhookValidationResult(
            False, "payload_must_be_bytes", ts, "conekta-signature"
        )

    if max_age_seconds is not None:
        now = int(time.time())
        if abs(now - ts) > max_age_seconds:
            return WebhookValidationResult(
                False, "expired_timestamp", ts, "conekta-signature"
            )

    signed = f"{ts}.".encode("utf-8") + payload
    computed = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed, v1):
        return WebhookValidationResult(False, "hmac_mismatch", ts, "conekta-signature")

    return WebhookValidationResult(True, None, ts, "conekta-signature")


def validate_webhook_auto(
    *,
    headers: dict[str, str],
    payload: bytes,
    secret: str,
    max_age_seconds: int | None = 300,
) -> WebhookValidationResult:
    """Detecta el formato del header de firma y delega al validador correcto.

    Busca en orden:
    1. `conekta-signature` (moderno) — `Digest` se ignora si este existe
    2. `Digest` (legacy)
    Si no encuentra ninguno → `missing_signature_header`.
    """
    headers_lower = {k.lower(): v for k, v in (headers or {}).items()}

    if "conekta-signature" in headers_lower:
        return validate_webhook_signature(
            signature_header=headers_lower["conekta-signature"],
            payload=payload,
            secret=secret,
            max_age_seconds=max_age_seconds,
        )
    if "digest" in headers_lower:
        return validate_webhook_digest(
            digest_header=headers_lower["digest"],
            payload=payload,
            secret=secret,
        )
    return WebhookValidationResult(False, "missing_signature_header", None, None)
