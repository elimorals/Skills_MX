"""File-based cache with TTL for plugins-mx MCP servers.

Why file-based instead of in-memory:
- Survives process restarts (MCPs spawn fresh per session)
- Visible/auditable to the user (just files on disk)
- Cheap, no Redis required for PyME-scale workloads

Design:
- Keyed by (namespace, key). Namespace = MCP name, key = caller-provided.
- Stored as JSON: { "stored_at": iso, "expires_at": iso, "payload": {...} }
- TTL is per-write, not global — caller decides freshness budget per tool.
- Manual `invalidate(namespace, key)` and `clear(namespace)` for write ops.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def _default_cache_root() -> Path:
    """Return base directory for cache files.

    Honors PLUGINS_MX_CACHE_DIR env var so tests can isolate cache state.
    """
    override = os.environ.get("PLUGINS_MX_CACHE_DIR")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".cache" / "plugins-mx"


def _safe_key(key: str) -> str:
    """Make a key safe for filesystem use.

    Long or weird keys (params containing slashes, unicode, etc.) become a hash.
    Short alphanumeric keys are preserved as-is for human-readable cache dirs.
    """
    if len(key) <= 64 and all(c.isalnum() or c in "-_." for c in key):
        return key
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]


class FileCache:
    """JSON cache with explicit TTL per entry.

    Example:
        cache = FileCache("banxico_mcp")
        cache.set("usd_mxn_2026-03-15", {"rate": 18.5}, ttl_hours=24)
        hit = cache.get("usd_mxn_2026-03-15")  # → {"rate": 18.5}
    """

    def __init__(self, namespace: str, root: Path | None = None) -> None:
        if not namespace or "/" in namespace:
            raise ValueError("namespace must be non-empty and free of slashes")
        self.namespace = namespace
        self.root = (root or _default_cache_root()) / namespace
        self.root.mkdir(parents=True, exist_ok=True)

    # ---------- core API ----------

    def get(self, key: str) -> Any | None:
        """Return cached payload or None if missing/expired.

        Expired entries are deleted on read to keep the cache directory tidy.
        """
        path = self._path(key)
        if not path.exists():
            return None

        try:
            raw = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            # Corrupted entry — drop it
            path.unlink(missing_ok=True)
            return None

        expires_at = raw.get("expires_at")
        if expires_at and datetime.fromisoformat(expires_at) <= datetime.now(timezone.utc):
            path.unlink(missing_ok=True)
            return None

        return raw.get("payload")

    def set(
        self,
        key: str,
        payload: Any,
        ttl_hours: float | None = None,
        ttl_minutes: float | None = None,
        ttl_days: float | None = None,
    ) -> None:
        """Store payload with TTL. Pass exactly one ttl_* parameter."""
        ttl = self._coalesce_ttl(ttl_hours=ttl_hours, ttl_minutes=ttl_minutes, ttl_days=ttl_days)
        now = datetime.now(timezone.utc)
        entry = {
            "stored_at": now.isoformat(),
            "expires_at": (now + ttl).isoformat() if ttl else None,
            "payload": payload,
        }
        path = self._path(key)
        # Atomic write: write to .tmp then rename
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(entry, ensure_ascii=False, indent=2))
        tmp.replace(path)

    def invalidate(self, key: str) -> None:
        """Drop a single entry. Safe if it doesn't exist."""
        self._path(key).unlink(missing_ok=True)

    def clear(self) -> int:
        """Drop all entries in this namespace. Returns count removed."""
        count = 0
        for f in self.root.glob("*.json"):
            f.unlink(missing_ok=True)
            count += 1
        return count

    # ---------- introspection ----------

    def keys(self) -> list[str]:
        """List currently-cached keys (post-expiry filter)."""
        result = []
        for f in self.root.glob("*.json"):
            if self.get(f.stem) is not None:
                result.append(f.stem)
        return result

    def stats(self) -> dict[str, Any]:
        """Return summary stats for monitoring."""
        files = list(self.root.glob("*.json"))
        total_bytes = sum(f.stat().st_size for f in files if f.exists())
        return {
            "namespace": self.namespace,
            "entries": len(files),
            "bytes": total_bytes,
            "root": str(self.root),
        }

    # ---------- helpers ----------

    def _path(self, key: str) -> Path:
        return self.root / f"{_safe_key(key)}.json"

    @staticmethod
    def _coalesce_ttl(
        ttl_hours: float | None,
        ttl_minutes: float | None,
        ttl_days: float | None,
    ) -> timedelta | None:
        """Convert exclusive ttl_* params to a single timedelta."""
        provided = [t for t in (ttl_hours, ttl_minutes, ttl_days) if t is not None]
        if not provided:
            return None  # No expiration
        if len(provided) > 1:
            raise ValueError("Pass at most one of ttl_hours, ttl_minutes, ttl_days")
        if ttl_hours is not None:
            return timedelta(hours=ttl_hours)
        if ttl_minutes is not None:
            return timedelta(minutes=ttl_minutes)
        if ttl_days is not None:
            return timedelta(days=ttl_days)
        return None  # unreachable
