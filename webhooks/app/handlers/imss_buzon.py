"""Handler para notificaciones IMSS Buzón.

⚠ IMSS Buzón no envía webhooks oficiales — esto es para triggers manuales
desde un cron que consulta IMSS y empuja al receptor.
"""

from __future__ import annotations

from typing import Any


def handle(payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    notificacion_id = payload.get("notificacion_id") or payload.get("id")
    tipo = payload.get("tipo")

    notes: list[str] = ["imss_buzon es manual-trigger"]
    action = "no_action"

    if notificacion_id:
        action = "alertar_usuario_notificacion_imss"
        notes.append(f"notificacion_id={notificacion_id}, tipo={tipo}")

    return {
        "action": action,
        "target_workflow": None,
        "notes": notes,
        "raw_event_type": "imss_buzon_manual",
    }
