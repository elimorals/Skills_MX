"""Handler para webhooks Mercado Libre.

ML envía topics: orders_v2, payments, questions, items, etc.
"""

from __future__ import annotations

from typing import Any


def handle(payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    topic = payload.get("topic", "")
    resource = payload.get("resource", "")

    notes: list[str] = []
    target_workflow: str | None = None
    action = "no_action"

    if topic == "orders_v2":
        action = "procesar_orden_ml"
        target_workflow = "workflow-orden-procesar"
        notes.append(f"resource={resource}")
    elif topic == "payments":
        action = "consultar_pago_ml"
        target_workflow = "workflow-pago-conciliacion"
    elif topic == "questions":
        action = "responder_pregunta_ml"
    elif topic == "items":
        action = "validar_publicacion_item"
    else:
        notes.append(f"topic sin handler: {topic}")

    return {
        "action": action,
        "target_workflow": target_workflow,
        "notes": notes,
        "raw_event_type": topic,
    }
