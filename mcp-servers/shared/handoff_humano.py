"""Handoff humano estructurado (regla 3 del plan mock→real: nunca saltar CAPTCHAs).

Cuando un portal exige CAPTCHA, login del titular o un bot manager, el tool no
intenta pasarlo: devuelve este dict para que una persona complete la consulta.
"""

from __future__ import annotations

from typing import Any, Literal

Motivo = Literal["captcha", "login", "bot_manager"]


def handoff_humano(
    *,
    portal: str,
    motivo: Motivo,
    pasos: list[str],
    detalle: str = "",
    **extra: Any,
) -> dict[str, Any]:
    return {
        "requiere_humano": True,
        "consultado": False,
        "simulated": False,
        "motivo": motivo,
        "detalle": detalle,
        "portal": portal,
        "pasos": pasos,
        **extra,
    }
