"""Handler para webhooks Typeform (formularios)."""

from __future__ import annotations

from typing import Any


def handle(payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    event_type = payload.get("event_type", "")
    form_response = payload.get("form_response", {})

    notes: list[str] = []
    action = "no_action"

    if event_type == "form_response":
        form_id = form_response.get("form_id") if isinstance(form_response, dict) else None
        action = "procesar_respuesta_form"
        notes.append(f"form_id={form_id}")
    else:
        notes.append(f"evento sin handler: {event_type}")

    return {
        "action": action,
        "target_workflow": None,
        "notes": notes,
        "raw_event_type": event_type,
    }
