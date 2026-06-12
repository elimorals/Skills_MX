"""Autenticación HMAC-SHA256 para Bitso API privada.

Algoritmo oficial:
    nonce = current_unix_ms
    message = f"{nonce}{http_verb}{request_path}{json_payload}"
    signature = HMAC-SHA256(message, api_secret).hexdigest()
    Authorization: Bitso {api_key}:{nonce}:{signature}

⚠ Bitso rechaza si nonce no es estrictamente creciente. Mantener
counter persistente o usar `time.time_ns() // 1_000_000`.
"""

from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any


def build_signature(
    *,
    api_key: str,
    api_secret: str,
    http_verb: str,
    request_path: str,
    json_payload: str = "",
    nonce: int | None = None,
) -> dict[str, str]:
    """Construye headers Authorization para una request Bitso.

    Returns:
        dict con keys: Authorization, Content-Type.

    Args:
        api_key: BITSO_API_KEY
        api_secret: BITSO_API_SECRET (hex string)
        http_verb: GET, POST, DELETE
        request_path: ej. "/v3/balance/"
        json_payload: body JSON serializado (vacío para GET)
        nonce: opcional; default = ms desde epoch
    """
    if nonce is None:
        nonce = int(time.time() * 1000)

    message = f"{nonce}{http_verb.upper()}{request_path}{json_payload}"
    signature = hmac.new(
        api_secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return {
        "Authorization": f"Bitso {api_key}:{nonce}:{signature}",
        "Content-Type": "application/json",
    }
