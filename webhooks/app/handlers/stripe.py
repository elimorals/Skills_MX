"""Handler para webhooks Stripe.

Eventos relevantes para plugins-mx:
- payment_intent.succeeded → workflow-pago-conciliacion
- charge.refunded → registrar nota crédito CFDI
- invoice.payment_succeeded → emitir CFDI
- customer.subscription.updated → cobranza suscripción
"""

from __future__ import annotations

from typing import Any


def handle(payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    event_type = payload.get("type", "")
    data = payload.get("data", {})
    obj = data.get("object", {}) if isinstance(data, dict) else {}

    notes: list[str] = []
    target_workflow: str | None = None
    action = "no_action"

    if event_type == "payment_intent.succeeded":
        action = "registrar_pago_y_timbrar_cfdi"
        target_workflow = "workflow-pago-conciliacion"
        notes.append(f"amount_received={obj.get('amount_received')}")
    elif event_type == "charge.refunded":
        action = "emitir_nota_credito"
        target_workflow = "workflow-cfdi-emision-completa"
        notes.append(f"refund_amount={obj.get('amount_refunded')}")
    elif event_type == "invoice.payment_succeeded":
        action = "emitir_cfdi"
        target_workflow = "workflow-cfdi-emision-completa"
    elif event_type and event_type.startswith("customer.subscription."):
        action = "actualizar_status_suscripcion"
        notes.append("suscripción modificada — revisar cobranza")
    else:
        notes.append(f"evento sin handler específico: {event_type}")

    return {
        "action": action,
        "target_workflow": target_workflow,
        "notes": notes,
        "raw_event_type": event_type,
    }
