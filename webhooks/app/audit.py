"""Append-only audit log para webhooks recibidos.

Similar a `shared/bitacora.py` del monorepo MCP pero local a webhooks/ para
no acoplar el deployment.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _default_audit_root() -> Path:
    override = os.environ.get("PLUGINS_MX_WEBHOOKS_AUDIT_DIR")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".local" / "share" / "plugins-mx" / "webhooks-audit"


def hash_sensitive(value: str | None) -> str | None:
    """SHA256-12 stable hash para identificadores sensibles."""
    if value is None:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


class WebhookAudit:
    """Audit log scoped al receptor de webhooks.

    Rota mensualmente: <root>/YYYY-MM.jsonl
    """

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or _default_audit_root()
        self.root.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        *,
        source: str,
        event_id: str | None,
        event_type: str | None,
        signature_valid: bool,
        outcome: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Registra un webhook recibido.

        outcome: "accepted" | "rejected_signature" | "duplicate" | "dispatched"
                 | "handler_error" | "no_handler" | ...
        """
        entry: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "source": source,
            "event_id_hash": hash_sensitive(event_id),
            "event_type": event_type,
            "signature_valid": signature_valid,
            "outcome": outcome,
        }
        if details:
            entry["details"] = details

        path = self.root / f"{datetime.now(timezone.utc).strftime('%Y-%m')}.jsonl"
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def tail(self, n: int = 100) -> list[dict[str, Any]]:
        path = self.root / f"{datetime.now(timezone.utc).strftime('%Y-%m')}.jsonl"
        if not path.exists():
            return []
        lines = path.read_text(encoding="utf-8").splitlines()
        return [json.loads(line) for line in lines[-n:] if line.strip()]
