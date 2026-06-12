"""Tests para mp_bitso/auth.py — HMAC signature."""

from __future__ import annotations

import hashlib
import hmac

from mp_bitso.auth import build_signature


def test_signature_estructura_correcta() -> None:
    headers = build_signature(
        api_key="demo_key",
        api_secret="demo_secret",
        http_verb="GET",
        request_path="/v3/balance/",
        nonce=1234567890,
    )
    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Bitso demo_key:1234567890:")
    assert headers["Content-Type"] == "application/json"


def test_signature_hmac_correcto() -> None:
    """Verifica que el HMAC computado coincide con el algoritmo oficial."""
    api_key = "demo_key"
    api_secret = "demo_secret"
    nonce = 1234567890
    path = "/v3/balance/"
    expected_message = f"{nonce}GET{path}"
    expected_sig = hmac.new(
        api_secret.encode("utf-8"),
        expected_message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    headers = build_signature(
        api_key=api_key,
        api_secret=api_secret,
        http_verb="GET",
        request_path=path,
        nonce=nonce,
    )
    assert expected_sig in headers["Authorization"]


def test_signature_con_payload() -> None:
    """POST con body JSON debe incluirlo en el message."""
    api_key = "k"
    api_secret = "s"
    nonce = 999
    path = "/v3/orders/"
    payload = '{"book":"btc_mxn","side":"buy"}'
    expected_message = f"{nonce}POST{path}{payload}"
    expected_sig = hmac.new(
        api_secret.encode("utf-8"),
        expected_message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    headers = build_signature(
        api_key=api_key,
        api_secret=api_secret,
        http_verb="POST",
        request_path=path,
        json_payload=payload,
        nonce=nonce,
    )
    assert expected_sig in headers["Authorization"]


def test_signature_normaliza_verb_a_mayusculas() -> None:
    """get → GET en el message."""
    h = build_signature(
        api_key="k", api_secret="s", http_verb="get",
        request_path="/v3/x/", nonce=1,
    )
    # Construir manualmente con GET (mayúscula) debe coincidir
    expected = hmac.new(b"s", b"1GET/v3/x/", hashlib.sha256).hexdigest()
    assert expected in h["Authorization"]


def test_signature_nonce_default_es_actual() -> None:
    """Sin nonce, usar time.time() * 1000."""
    h = build_signature(
        api_key="k", api_secret="s", http_verb="GET", request_path="/v3/x/",
    )
    # Extraer nonce del header
    parts = h["Authorization"].split(":")
    nonce_extraido = int(parts[1])
    # Debe ser reciente (últimas 24h en ms)
    import time
    now_ms = int(time.time() * 1000)
    assert abs(now_ms - nonce_extraido) < 86400000
