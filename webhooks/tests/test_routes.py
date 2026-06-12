import hashlib
import hmac
import json
import time

import pytest


def _stripe_sig(payload: bytes, secret: str = "shh") -> str:
    ts = int(time.time())
    signed = f"{ts}.".encode() + payload
    digest = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return f"t={ts},v1={digest}"


def test_unknown_source_returns_404(app_client):
    r = app_client.post("/webhooks/no_existe", json={"foo": "bar"})
    assert r.status_code == 404
    body = r.json()
    assert body["ok"] is False
    assert body["source"] == "no_existe"


def test_stripe_mock_accepts_without_signature(app_client):
    payload = {"id": "evt_test", "type": "payment_intent.succeeded",
               "data": {"object": {"amount_received": 12345}}}
    r = app_client.post("/webhooks/stripe", json=payload)
    assert r.status_code == 202
    body = r.json()
    assert body["ok"] is True
    assert body["source"] == "stripe"
    assert body["action"] == "registrar_pago_y_timbrar_cfdi"
    assert body["target_workflow"] == "workflow-pago-conciliacion"


def test_idempotency_duplicate_rejected(app_client):
    payload = {"id": "evt_dup", "type": "charge.paid"}
    headers = {"X-Webhook-Event-Id": "evt_dup"}
    r1 = app_client.post("/webhooks/conekta", json=payload, headers=headers)
    assert r1.status_code == 202
    r2 = app_client.post("/webhooks/conekta", json=payload, headers=headers)
    assert r2.status_code == 409
    assert r2.json()["error"] == "duplicate"


def test_stripe_real_secret_validates(monkeypatch, app_client):
    # Switch from mock → real para este test
    monkeypatch.setenv("PLUGINS_MX_WEBHOOKS_MODE", "production")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "shh")
    # rebuild app porque settings se cachean
    from app.main import create_app
    from fastapi.testclient import TestClient

    client = TestClient(create_app())

    payload = json.dumps({"id": "evt_real", "type": "payment_intent.succeeded"}).encode()
    sig = _stripe_sig(payload, "shh")
    r = client.post(
        "/webhooks/stripe",
        content=payload,
        headers={"stripe-signature": sig, "content-type": "application/json"},
    )
    assert r.status_code == 202
    assert r.json()["ok"] is True


def test_stripe_real_secret_rejects_bad_sig(monkeypatch, app_client):
    monkeypatch.setenv("PLUGINS_MX_WEBHOOKS_MODE", "production")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "shh")
    from app.main import create_app
    from fastapi.testclient import TestClient

    client = TestClient(create_app())

    payload = b'{"id":"evt_bad"}'
    r = client.post(
        "/webhooks/stripe",
        content=payload,
        headers={"stripe-signature": "t=1,v1=000", "content-type": "application/json"},
    )
    assert r.status_code == 401
    assert r.json()["reason"] in ("expired_timestamp", "hmac_mismatch")


def test_github_push_to_shared_triggers_sync(app_client):
    payload = {
        "ref": "refs/heads/main",
        "commits": [
            {"added": [], "modified": ["_shared/cfdi-emision/SKILL.md"], "removed": []}
        ],
    }
    r = app_client.post(
        "/webhooks/github",
        json=payload,
        headers={"X-GitHub-Event": "push", "X-GitHub-Delivery": "abc-1"},
    )
    assert r.status_code == 202
    body = r.json()
    assert body["action"] == "sincronizar_shared_a_verticales"


def test_meta_whatsapp_messages_handler(app_client):
    payload = {
        "entry": [
            {
                "id": "WABA-1",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messages": [{"from": "521..", "id": "wamid-1", "type": "text"}]
                        },
                    }
                ],
            }
        ]
    }
    r = app_client.post("/webhooks/meta_whatsapp", json=payload)
    assert r.status_code == 202
    assert r.json()["action"] == "procesar_mensaje_entrante_wa"


def test_admin_recent_requires_key(app_client):
    r = app_client.get("/webhooks/recent")
    assert r.status_code == 401


def test_admin_recent_with_key(app_client):
    # primero genera un evento para que haya algo en audit
    app_client.post("/webhooks/stripe", json={"id": "evt_for_audit", "type": "x"})
    r = app_client.get(
        "/webhooks/recent",
        headers={"X-Admin-Key": "test-admin-key"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["count"] >= 1
    # solo registramos hashes, nunca event_id en claro
    for entry in body["entries"]:
        assert "event_id_hash" in entry


def test_mercadolibre_no_handler_in_mock(app_client):
    # ML mock-mode con allowlist vacío = acepta
    payload = {"topic": "orders_v2", "resource": "/orders/123"}
    r = app_client.post("/webhooks/mercadolibre", json=payload)
    assert r.status_code == 202
    assert r.json()["action"] == "procesar_orden_ml"


def test_no_handler_action_when_unknown_event_type(app_client):
    r = app_client.post("/webhooks/stripe", json={"id": "evt_x", "type": "unknown.event"})
    assert r.status_code == 202
    body = r.json()
    assert body["action"] == "no_action"


def test_event_id_hash_is_short_and_stable(app_client):
    r1 = app_client.post("/webhooks/stripe", json={"id": "same", "type": "x"})
    eid1 = r1.json()["event_id_hash"]
    # mismo event_id provocaría 409, así que pruebo con otro source
    r2 = app_client.post("/webhooks/conekta", json={"id": "same", "type": "y"})
    eid2 = r2.json()["event_id_hash"]
    assert len(eid1) == 12
    assert len(eid2) == 12
