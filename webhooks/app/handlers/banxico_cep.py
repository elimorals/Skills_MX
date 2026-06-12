"""Handler para webhooks Banxico CEP (Comprobantes Electrónicos de Pago).

⚠ Banxico CEP no expone webhooks oficiales — esta ruta es para triggers
manuales del operador o de un cron que detecta pago via API CEP.
"""

from __future__ import annotations

from typing import Any


def handle(payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    clave_rastreo = payload.get("clave_rastreo") or payload.get("clave")
    monto = payload.get("monto")

    notes: list[str] = ["banxico_cep es manual-trigger (no firma estándar)"]
    action = "no_action"
    target_workflow: str | None = None

    if clave_rastreo:
        action = "validar_pago_spei_y_conciliar"
        target_workflow = "workflow-pago-conciliacion"
        notes.append(f"clave_rastreo={clave_rastreo}, monto={monto}")

    return {
        "action": action,
        "target_workflow": target_workflow,
        "notes": notes,
        "raw_event_type": "banxico_cep_manual",
    }
