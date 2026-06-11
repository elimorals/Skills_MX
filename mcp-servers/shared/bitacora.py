"""Append-only audit log for plugins-mx MCP calls.

Why append-only JSONL:
- Tail-able with standard unix tools (tail -f, grep, jq)
- Survives crashes mid-write (only the partial last line is lost)
- One line per call → easy to count, filter, aggregate

Each line carries enough to reconstruct what happened without leaking secrets.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _default_audit_root() -> Path:
    override = os.environ.get("PLUGINS_MX_AUDIT_DIR")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".local" / "share" / "plugins-mx" / "audit-log"


def _hash_sensitive(value: str | None) -> str | None:
    """Stable short hash for identifiers we don't want to log raw.

    Used for RFCs, CURPs, account numbers — preserves "same vs different"
    semantics for analysis without leaking the actual ID.
    """
    if value is None:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


class Bitacora:
    """Audit log writer scoped to a single MCP namespace.

    Files rotate monthly: audit-log/<namespace>/YYYY-MM.jsonl
    """

    def __init__(self, namespace: str, root: Path | None = None) -> None:
        if not namespace or "/" in namespace:
            raise ValueError("namespace must be non-empty and free of slashes")
        self.namespace = namespace
        self.root = (root or _default_audit_root()) / namespace
        self.root.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        tool: str,
        *,
        success: bool,
        duration_ms: float | None = None,
        params_summary: dict[str, Any] | None = None,
        result_summary: dict[str, Any] | None = None,
        error: dict[str, Any] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        """Append one audit entry.

        params_summary should be a DERIVED summary, not the raw params, to avoid
        logging secrets. Pre-hash anything sensitive with `hash_sensitive`.
        """
        entry: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "namespace": self.namespace,
            "tool": tool,
            "success": success,
        }
        if duration_ms is not None:
            entry["duration_ms"] = round(duration_ms, 1)
        if params_summary:
            entry["params"] = params_summary
        if result_summary:
            entry["result"] = result_summary
        if error:
            entry["error"] = error
        if extra:
            entry["extra"] = extra

        path = self._current_path()
        # Append-only mode; one JSON object per line
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def tail(self, n: int = 20) -> list[dict[str, Any]]:
        """Return the last N entries for the current month file. Mostly for tests."""
        path = self._current_path()
        if not path.exists():
            return []
        lines = path.read_text(encoding="utf-8").splitlines()
        return [json.loads(line) for line in lines[-n:] if line.strip()]

    @staticmethod
    def hash_sensitive(value: str | None) -> str | None:
        """Expose the hashing helper so callers can summarize without leaks."""
        return _hash_sensitive(value)

    # ---------- helpers ----------

    def _current_path(self) -> Path:
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        return self.root / f"{month}.jsonl"
