"""Validación de firma de webhooks Mercado Pago.

Mercado Pago firma cada webhook con HMAC-SHA256 sobre un manifest específico.
Sin validar la firma, cualquiera puede mandarte POSTs falsos al endpoint y
hacerte timbrar CFDIs por pagos que nunca ocurrieron.

Algoritmo oficial (https://www.mercadopago.com.mx/developers/es/docs/your-integrations/notifications/webhooks):

1. Headers que envía MP:
   - `x-signature`: "ts=1234567890,v1=abcdef..."
   - `x-request-id`: GUID único de la request

2. Manifest a firmar:
   `id:<DATA_ID>;request-id:<X_REQUEST_ID>;ts:<TS>;`

3. HMAC-SHA256(manifest, secret) en hex debe igualar el `v1=...` del header.

Si NO coincide → rechazar el webhook como inválido.

⚠ El timestamp `ts` también debería validarse para evitar replay attacks
(rechazar webhooks con ts más viejo que ~5 min). Esto se hace opcional —
algunos receptores lentos legítimamente procesan webhooks tardíos.
"""

from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class WebhookValidationResult:
    """Resultado de validar una firma de webhook."""

    valid: bool
    reason: str | None  # None si valid; explicación si no
    timestamp: int | None  # ts extracted del header si pudo parsearse
    data_id: str | None  # ID del recurso notificado

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "data_id": self.data_id,
        }


def parse_signature_header(x_signature: str) -> tuple[int | None, str | None]:
    """Extrae (ts, v1) del header `x-signature` de Mercado Pago.

    Header tiene la forma `ts=1234567890,v1=abc123def456...`.
    Es lenient con whitespace y orden de los campos.

    Returns:
        (timestamp, hmac_hex) — None si no se pudo parsear.
    """
    if not x_signature or not isinstance(x_signature, str):
        return None, None

    ts: int | None = None
    v1: str | None = None

    for part in x_signature.split(","):
        part = part.strip()
        if not part or "=" not in part:
            continue
        key, _, value = part.partition("=")
        key = key.strip().lower()
        value = value.strip()
        if key == "ts":
            try:
                ts = int(value)
            except ValueError:
                ts = None
        elif key == "v1":
            v1 = value

    return ts, v1


def build_manifest(data_id: str, x_request_id: str, ts: int) -> str:
    """Construye el manifest que se firma con HMAC.

    Formato oficial: `id:<DATA_ID>;request-id:<X_REQUEST_ID>;ts:<TS>;`

    El orden y los separadores importan — cualquier variación produce
    un HMAC distinto.
    """
    return f"id:{data_id};request-id:{x_request_id};ts:{ts};"


def validate_webhook_signature(
    *,
    x_signature: str,
    x_request_id: str,
    data_id: str,
    secret: str,
    max_age_seconds: int | None = 300,
) -> WebhookValidationResult:
    """Valida una firma de webhook Mercado Pago.

    Args:
        x_signature: Valor crudo del header `x-signature`.
        x_request_id: Valor del header `x-request-id`.
        data_id: ID del recurso notificado (típicamente extracted del query
            string `?data.id=...` o del body JSON `data.id`).
        secret: Webhook secret obtenido del panel MP (no es el access_token).
        max_age_seconds: Si se pasa, rechaza webhooks con timestamp más viejo
            que esto (anti-replay). None desactiva la check.

    Returns:
        WebhookValidationResult con valid + reason si no es válida.

    Reasons posibles:
        - "missing_signature_header"
        - "malformed_signature_header"
        - "missing_secret"
        - "missing_request_id"
        - "missing_data_id"
        - "hmac_mismatch"
        - "expired_timestamp"
    """
    if not secret:
        return WebhookValidationResult(False, "missing_secret", None, data_id)

    ts, expected_hmac = parse_signature_header(x_signature)

    if ts is None or expected_hmac is None:
        return WebhookValidationResult(
            False, "malformed_signature_header", ts, data_id
        )

    if not x_request_id:
        return WebhookValidationResult(False, "missing_request_id", ts, data_id)
    if not data_id:
        return WebhookValidationResult(False, "missing_data_id", ts, data_id)

    # Anti-replay (opcional)
    if max_age_seconds is not None:
        now = int(time.time())
        if abs(now - ts) > max_age_seconds:
            return WebhookValidationResult(False, "expired_timestamp", ts, data_id)

    manifest = build_manifest(data_id, x_request_id, ts)
    computed = hmac.new(
        secret.encode("utf-8"),
        manifest.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    # Compare in constant time to prevent timing attacks
    if not hmac.compare_digest(computed, expected_hmac):
        return WebhookValidationResult(False, "hmac_mismatch", ts, data_id)

    return WebhookValidationResult(True, None, ts, data_id)
