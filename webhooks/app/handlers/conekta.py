"""Handler para webhooks Conekta."""

from __future__ import annotations

from typing import Any


def handle(payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    event_type = payload.get("type", "")
    data = payload.get("data", {})
    obj = data.get("object", {}) if isinstance(data, dict) else {}

    notes: list[str] = []
    target_workflow: str | None = None
    action = "no_action"

    if event_type == "charge.paid":
        action = "registrar_pago_y_timbrar_cfdi"
        target_workflow = "workflow-pago-conciliacion"
        notes.append(f"amount={obj.get('amount')}")
    elif event_type == "charge.refunded":
        action = "emitir_nota_credito"
        target_workflow = "workflow-cfdi-emision-completa"
    elif event_type == "order.paid":
        action = "procesar_orden_pagada"
    elif event_type and event_type.startswith("subscription."):
        action = "actualizar_suscripcion"
    else:
        notes.append(f"evento sin handler: {event_type}")

    return {
        "action": action,
        "target_workflow": target_workflow,
        "notes": notes,
        "raw_event_type": event_type,
    }
