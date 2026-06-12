"""Handler para CONDUSEF (queja contra entidad financiera).

⚠ Manual trigger — operador empuja status update."""

from __future__ import annotations

from typing import Any


def handle(payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    queja_id = payload.get("queja_id") or payload.get("id")
    status = payload.get("status")

    notes: list[str] = ["condusef es manual-trigger"]
    action = "no_action"

    if queja_id:
        action = "registrar_status_queja_condusef"
        notes.append(f"queja_id={queja_id}, status={status}")

    return {
        "action": action,
        "target_workflow": None,
        "notes": notes,
        "raw_event_type": "condusef_manual",
    }
