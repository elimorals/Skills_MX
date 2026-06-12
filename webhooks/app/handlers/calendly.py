"""Handler para webhooks Calendly (onboarding / agenda)."""

from __future__ import annotations

from typing import Any


def handle(payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    event_type = payload.get("event", "")
    payload_data = payload.get("payload", {})

    notes: list[str] = []
    action = "no_action"

    if event_type == "invitee.created":
        action = "iniciar_onboarding_cliente"
        email = (payload_data.get("email") if isinstance(payload_data, dict) else None)
        notes.append("nuevo invitee — iniciar pipeline onboarding")
        if email:
            notes.append("email recibido (no se loguea)")
    elif event_type == "invitee.canceled":
        action = "registrar_cancelacion_cita"
    else:
        notes.append(f"evento sin handler: {event_type}")

    return {
        "action": action,
        "target_workflow": None,
        "notes": notes,
        "raw_event_type": event_type,
    }
