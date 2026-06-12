"""Handler para webhooks Facturama (CFDI timbrado / cancelado)."""

from __future__ import annotations

from typing import Any


def handle(payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    event_type = payload.get("event") or payload.get("type", "")
    cfdi = payload.get("cfdi") or payload.get("data", {})
    uuid = cfdi.get("uuid") if isinstance(cfdi, dict) else None

    notes: list[str] = []
    action = "no_action"

    if event_type in ("cfdi.stamped", "cfdi.timbrado"):
        action = "registrar_cfdi_timbrado"
        notes.append(f"uuid={uuid}")
    elif event_type in ("cfdi.cancelled", "cfdi.canceled", "cfdi.cancelado"):
        action = "registrar_cancelacion"
        notes.append(f"uuid={uuid}")
    elif event_type and event_type.startswith("cfdi."):
        action = "registrar_evento_cfdi"
    else:
        notes.append(f"evento sin handler: {event_type}")

    return {
        "action": action,
        "target_workflow": None,
        "notes": notes,
        "raw_event_type": event_type,
    }
