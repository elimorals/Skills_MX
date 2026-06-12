"""Handler para webhooks GitHub.

Uso típico en plugins-mx: cuando alguien hace push a `_shared/`, re-sincronizar
a todos los verticales (CI-style).
"""

from __future__ import annotations

from typing import Any


def handle(payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    event_type = headers.get("X-GitHub-Event") or headers.get("x-github-event", "")

    notes: list[str] = []
    action = "no_action"

    if event_type == "push":
        commits = payload.get("commits", [])
        affected_paths: set[str] = set()
        for c in commits if isinstance(commits, list) else []:
            for change_type in ("added", "modified", "removed"):
                paths = c.get(change_type, []) if isinstance(c, dict) else []
                if isinstance(paths, list):
                    affected_paths.update(paths)

        shared_changes = [p for p in affected_paths if p.startswith("_shared/")]
        if shared_changes:
            action = "sincronizar_shared_a_verticales"
            notes.append(f"{len(shared_changes)} archivo(s) en _shared/ modificados")
        else:
            notes.append("push sin cambios en _shared/")
    elif event_type in ("pull_request", "pull_request.opened"):
        action = "notificar_pr"
        notes.append(f"PR #{payload.get('number')}")
    else:
        notes.append(f"evento sin handler: {event_type}")

    return {
        "action": action,
        "target_workflow": None,
        "notes": notes,
        "raw_event_type": event_type,
    }
