"""Storage de idempotencia para deduplicar webhooks.

Cuando un servicio externo envía el mismo evento 2 veces (timeout, retry, etc.)
queremos procesarlo solo la primera vez. El receptor llama `seen()` para
verificar y `mark()` cuando termine de procesar.

Backends:
- `sqlite`: persistente, file-based, OK hasta ~10k webhooks/día
- `memory`: in-process dict, solo para tests

Cada entrada vive 30 días por default (suficiente para todos los servicios
que conozco — el más agresivo es Stripe con retries hasta 72h).
"""

from __future__ import annotations

import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Protocol


class IdempotencyStore(Protocol):
    """Interface para storage de idempotencia."""

    def seen(self, source: str, event_id: str) -> bool: ...
    def mark(self, source: str, event_id: str) -> None: ...
    def gc(self, older_than_days: int = 30) -> int: ...


class MemoryStore:
    """In-process dict store — solo para tests."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._data: dict[tuple[str, str], datetime] = {}

    def seen(self, source: str, event_id: str) -> bool:
        with self._lock:
            return (source, event_id) in self._data

    def mark(self, source: str, event_id: str) -> None:
        with self._lock:
            self._data[(source, event_id)] = datetime.now(timezone.utc)

    def gc(self, older_than_days: int = 30) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
        with self._lock:
            stale = [k for k, ts in self._data.items() if ts < cutoff]
            for k in stale:
                del self._data[k]
            return len(stale)


class SQLiteStore:
    """File-based store. Sobrevive restarts."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_schema()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.path), isolation_level=None)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_schema(self) -> None:
        with self._lock, self._conn() as c:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS webhook_events (
                    source TEXT NOT NULL,
                    event_id TEXT NOT NULL,
                    received_at TEXT NOT NULL,
                    PRIMARY KEY (source, event_id)
                )
                """
            )

    def seen(self, source: str, event_id: str) -> bool:
        with self._lock, self._conn() as c:
            cur = c.execute(
                "SELECT 1 FROM webhook_events WHERE source=? AND event_id=?",
                (source, event_id),
            )
            return cur.fetchone() is not None

    def mark(self, source: str, event_id: str) -> None:
        with self._lock, self._conn() as c:
            c.execute(
                "INSERT OR IGNORE INTO webhook_events VALUES (?, ?, ?)",
                (source, event_id, datetime.now(timezone.utc).isoformat()),
            )

    def gc(self, older_than_days: int = 30) -> int:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=older_than_days)).isoformat()
        with self._lock, self._conn() as c:
            cur = c.execute(
                "DELETE FROM webhook_events WHERE received_at < ?", (cutoff,)
            )
            return cur.rowcount or 0


def build_store(backend: str, sqlite_path: Path) -> IdempotencyStore:
    if backend == "memory":
        return MemoryStore()
    if backend == "sqlite":
        return SQLiteStore(sqlite_path)
    raise ValueError(f"Unknown idempotency backend: {backend}")
