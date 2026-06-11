"""Mock mode helpers for plugins-mx MCP servers.

Every MCP supports a mock mode that produces plausible responses without
hitting the real upstream. Activated when:
- Credentials env var is unset OR
- PLUGINS_MX_MOCK=1 is set (forces mock even with credentials)

Responses include `simulated: true` so downstream skills/agents can tell
they're not real and avoid relying on them for production decisions.
"""

from __future__ import annotations

import os
from typing import Any


def is_mock_mode(credential_env_vars: list[str]) -> bool:
    """Decide whether to run in mock mode.

    Args:
        credential_env_vars: Env vars that, if set, indicate real credentials.

    Returns:
        True if mock mode should be used.

    Rules:
    - PLUGINS_MX_MOCK=1 → always mock (testing override)
    - Any of credential_env_vars set to non-empty → real mode
    - Otherwise → mock
    """
    if os.environ.get("PLUGINS_MX_MOCK") == "1":
        return True
    for var in credential_env_vars:
        value = os.environ.get(var, "").strip()
        if value:
            return False
    return True


def mark_simulated(payload: dict[str, Any], note: str | None = None) -> dict[str, Any]:
    """Attach simulation markers to a response payload.

    Returns a new dict — does NOT mutate the input. Adds:
    - simulated: true
    - advertencias: [note] appended to any existing list
    """
    out = dict(payload)
    out["simulated"] = True
    if note:
        existing = list(out.get("advertencias", []))
        existing.append(note)
        out["advertencias"] = existing
    elif "advertencias" not in out:
        out["advertencias"] = ["Respuesta simulada — no usar para decisiones de producción."]
    return out
