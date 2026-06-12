"""Endpoint genérico `POST /webhooks/{source}`.

Flujo:
1. Lee body raw + headers
2. Valida firma (HMAC / Bearer / IP allowlist según source)
3. Si firma inválida → 401, log, NO procesa
4. Si event_id ya procesado → 409, log
5. Parsea payload, despacha al handler correspondiente
6. Logea outcome y retorna 202
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Header, Query, Request, Response

from ..audit import WebhookAudit
from ..config import Settings, get_settings
from ..handlers.dispatch import SUPPORTED_SOURCES, dispatch
from ..idempotency import build_store
from ..validators import ValidationOutcome
from ..validators import (
    conekta as v_conekta,
    generic as v_generic,
    github as v_github,
    mercadopago as v_mp,
    meta_whatsapp as v_meta,
    stripe as v_stripe,
)

router = APIRouter()

# Lazy singleton — el store se inicializa una sola vez.
_STORE = None


def _get_store():
    global _STORE
    if _STORE is None:
        settings = get_settings()
        _STORE = build_store(settings.idempotency_backend, settings.idempotency_resolved_path)
    return _STORE


def _client_ip(request: Request) -> str:
    # Cloudflare / proxy forwarded IP
    fwd = request.headers.get("cf-connecting-ip") or request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    if request.client:
        return request.client.host
    return ""


def _fallback_event_id(source: str, payload: bytes) -> str:
    """Genera un event_id estable si el servicio no envía uno explícito."""
    return f"{source}-{hashlib.sha256(payload).hexdigest()[:16]}-{int(time.time())//60}"


def _validate(
    source: str,
    *,
    payload: bytes,
    headers: dict[str, str],
    settings: Settings,
    client_ip: str,
    data_id_query: str | None,
) -> ValidationOutcome:
    is_mock = settings.is_mock

    if source == "stripe":
        return v_stripe.validate(
            payload=payload, headers=headers, secret=settings.stripe_secret, is_mock=is_mock
        )
    if source == "mercadopago":
        return v_mp.validate(
            payload=payload,
            headers=headers,
            secret=settings.mercadopago_secret,
            is_mock=is_mock,
            data_id_query=data_id_query,
        )
    if source == "conekta":
        return v_conekta.validate(
            payload=payload, headers=headers, secret=settings.conekta_secret, is_mock=is_mock
        )
    if source == "github":
        return v_github.validate(
            payload=payload, headers=headers, secret=settings.github_secret, is_mock=is_mock
        )
    if source == "meta_whatsapp":
        return v_meta.validate(
            payload=payload,
            headers=headers,
            secret=settings.meta_whatsapp_app_secret,
            is_mock=is_mock,
        )
    if source == "facturama":
        outcome = v_generic.bearer_only(
            payload=payload,
            headers=headers,
            expected_token=settings.facturama_bearer,
            is_mock=is_mock,
        )
        if outcome.valid and settings.facturama_allowed_ips and not is_mock:
            if not v_generic.ip_in_allowlist(client_ip, settings.facturama_allowed_ips):
                return ValidationOutcome(False, "ip_not_in_allowlist", outcome.event_id, outcome.event_type)
        return outcome
    if source == "mercadolibre":
        # ML solo IP allowlist (no HMAC). En mock siempre acepta.
        if is_mock and not settings.mercadolibre_allowed_ips.strip():
            return v_generic.no_validation(payload=payload, headers=headers, is_mock=True)
        if not settings.mercadolibre_allowed_ips.strip():
            return ValidationOutcome(False, "missing_secret", None, None)
        if v_generic.ip_in_allowlist(client_ip, settings.mercadolibre_allowed_ips):
            return v_generic.no_validation(payload=payload, headers=headers, is_mock=True)
        return ValidationOutcome(False, "ip_not_in_allowlist", None, None)

    # Genericos sin firma: calendly, typeform, banxico_cep, imss_buzon, condusef
    # Calendly/Typeform sí tienen firma; los implementamos similar a github en V2.
    if source in ("calendly", "typeform"):
        # Por ahora: bearer si está configurado, mock otherwise
        secret = settings.calendly_secret if source == "calendly" else settings.typeform_secret
        return v_generic.bearer_only(
            payload=payload, headers=headers, expected_token=secret, is_mock=is_mock
        )

    if source in ("banxico_cep", "imss_buzon", "condusef"):
        return v_generic.no_validation(payload=payload, headers=headers, is_mock=True)

    return ValidationOutcome(False, "unsupported_source", None, None)


@router.post("/webhooks/{source}", status_code=202)
async def receive(
    source: str,
    request: Request,
    response: Response,
    x_webhook_event_id: str | None = Header(default=None, alias="X-Webhook-Event-Id"),
    data_id_query: str | None = Query(default=None, alias="data.id"),
) -> dict[str, Any]:
    settings = get_settings()
    audit = WebhookAudit()

    if source not in SUPPORTED_SOURCES:
        audit.log(
            source=source,
            event_id=None,
            event_type=None,
            signature_valid=False,
            outcome="no_handler",
        )
        response.status_code = 404
        return {"ok": False, "error": "source not supported", "source": source}

    raw_body = await request.body()
    headers = dict(request.headers)

    outcome = _validate(
        source,
        payload=raw_body,
        headers=headers,
        settings=settings,
        client_ip=_client_ip(request),
        data_id_query=data_id_query,
    )

    # explicit event_id header > body event_id (per source) > fallback
    event_id = x_webhook_event_id or outcome.event_id or _fallback_event_id(source, raw_body)

    if not outcome.valid:
        audit.log(
            source=source,
            event_id=event_id,
            event_type=outcome.event_type,
            signature_valid=False,
            outcome="rejected_signature",
            details={"reason": outcome.reason},
        )
        response.status_code = 401
        return {"ok": False, "error": "invalid signature", "reason": outcome.reason}

    store = _get_store()
    if store.seen(source, event_id):
        audit.log(
            source=source,
            event_id=event_id,
            event_type=outcome.event_type,
            signature_valid=True,
            outcome="duplicate",
        )
        response.status_code = 409
        return {"ok": False, "error": "duplicate", "event_id_hash": _hash_short(event_id)}

    try:
        payload_json: dict[str, Any] = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        if not isinstance(payload_json, dict):
            payload_json = {"_raw_non_dict": payload_json}
    except json.JSONDecodeError:
        payload_json = {"_raw_bytes_len": len(raw_body)}

    result = dispatch(source, payload_json, headers)

    store.mark(source, event_id)

    audit.log(
        source=source,
        event_id=event_id,
        event_type=outcome.event_type or result.get("raw_event_type"),
        signature_valid=True,
        outcome="dispatched" if result.get("action") != "no_action" else "no_action",
        details={"action": result.get("action"), "target_workflow": result.get("target_workflow")},
    )

    return {
        "ok": True,
        "source": source,
        "event_id_hash": _hash_short(event_id),
        "action": result.get("action"),
        "target_workflow": result.get("target_workflow"),
        "notes": result.get("notes", []),
        "signature_reason": outcome.reason,
    }


def _hash_short(event_id: str) -> str:
    return hashlib.sha256(event_id.encode("utf-8")).hexdigest()[:12]
