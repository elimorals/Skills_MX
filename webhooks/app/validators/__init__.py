"""Validadores HMAC por servicio.

Cada función retorna ValidationOutcome con `valid: bool` + `reason: str | None`.
En modo MOCK (settings.is_mock + no secret) retorna valid=True con reason="mock".
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationOutcome:
    valid: bool
    reason: str | None  # None si valid; "mock" si mock-bypass; explica si rechaza
    event_id: str | None = None
    event_type: str | None = None
