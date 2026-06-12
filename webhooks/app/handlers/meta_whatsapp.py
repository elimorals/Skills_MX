"""Handler para webhooks Meta WhatsApp Business."""

from __future__ import annotations

from typing import Any


def handle(payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    entries = payload.get("entry", [])
    notes: list[str] = []
    action = "no_action"

    if isinstance(entries, list):
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            changes = entry.get("changes", [])
            if not isinstance(changes, list):
                continue
            for change in changes:
                if not isinstance(change, dict):
                    continue
                field = change.get("field")
                value = change.get("value", {})
                if field == "messages":
                    messages = value.get("messages", []) if isinstance(value, dict) else []
                    if messages:
                        action = "procesar_mensaje_entrante_wa"
                        notes.append(f"mensajes={len(messages)}")
                        # Si es respuesta a una plantilla cobranza, podría ir a workflow específico
                elif field == "message_template_status_update":
                    action = "actualizar_status_plantilla"

    return {
        "action": action,
        "target_workflow": None,
        "notes": notes or ["sin payload reconocido"],
        "raw_event_type": "meta_whatsapp_messages",
    }
