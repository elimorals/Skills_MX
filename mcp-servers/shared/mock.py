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


def is_mock_mode(
    credential_env_vars: list[str],
    default_when_no_creds: bool = True,
) -> bool:
    """Decide whether to run in mock mode.

    Args:
        credential_env_vars: Env vars that, if set, indicate real credentials.
        default_when_no_creds: Behavior when no credentials are needed and
            PLUGINS_MX_MOCK is not explicitly set.
            - True (default): mock — safe for CI / dev / MCPs that need creds.
            - False: real — for public portals without auth (SAT 32-D, SIPRES, IMPI).

    Returns:
        True if mock mode should be used.

    Rules (in order):
    1. PLUGINS_MX_MOCK=1 → always mock (testing override)
    2. PLUGINS_MX_MOCK=0 → always real (production override)
    3. Any credential in credential_env_vars set non-empty → real
    4. Otherwise → default_when_no_creds
    """
    mock_env = os.environ.get("PLUGINS_MX_MOCK", "").strip()
    if mock_env == "1":
        return True
    if mock_env == "0":
        return False
    for var in credential_env_vars:
        value = os.environ.get(var, "").strip()
        if value:
            return False
    return default_when_no_creds


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
