"""Handler para webhooks Mercado Pago."""

from __future__ import annotations

from typing import Any


def handle(payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    event_type = payload.get("type") or payload.get("action") or ""
    data = payload.get("data", {})
    payment_id = data.get("id") if isinstance(data, dict) else None

    notes: list[str] = []
    target_workflow: str | None = None
    action = "no_action"

    if event_type in ("payment", "payment.created", "payment.updated"):
        action = "consultar_pago_y_conciliar"
        target_workflow = "workflow-pago-conciliacion"
        notes.append(f"payment_id={payment_id}")
    elif event_type in ("merchant_order", "merchant_order.updated"):
        action = "consultar_order_y_validar"
        notes.append(f"order_id={payment_id}")
    elif event_type in ("plan", "subscription"):
        action = "actualizar_suscripcion"
        notes.append(f"resource_id={payment_id}")
    else:
        notes.append(f"evento sin handler: {event_type}")

    return {
        "action": action,
        "target_workflow": target_workflow,
        "notes": notes,
        "raw_event_type": event_type,
    }
