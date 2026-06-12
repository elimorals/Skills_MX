"""Retry queue persistente SQLite para webhooks.

V1 procesaba handlers síncronamente best-effort: si fallaban, se perdía el evento.
V2 introduce esta cola: cada webhook entrante se persiste y un worker en background
lo procesa con backoff exponencial; si excede `max_attempts` va a dead-letter para
revisión manual.

Diseño deliberado:
- Sin dependencias externas (Redis, Celery): SQLite local es suficiente para el
  volumen esperado (<1000 webhooks/día por instancia).
- Reintentos visibles: cada attempt deja un row en `attempts` para auditoría.
- Idempotente: la propia cola hereda la idempotencia del receiver (no encolar
  duplicados detectados).
- Dead-letter explícito: tabla `dead_letter` con TODO el contexto + último error
  para que un humano lo resuelva.
"""

from __future__ import annotations

import json
import sqlite3
import time
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional


DEFAULT_DB_PATH = Path("~/.local/share/plugins-mx/webhooks/retry_queue.sqlite").expanduser()

# Backoff por attempt: 30s → 2m → 10m → 1h → 6h
DEFAULT_BACKOFF_SECONDS = [30, 120, 600, 3600, 21600]


class JobStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    DEAD = "dead"


@dataclass
class Job:
    id: int | None
    source: str
    event_id: str
    payload: dict[str, Any]
    headers: dict[str, str]
    status: JobStatus
    attempts: int
    next_attempt_at: datetime
    created_at: datetime
    last_error: str | None = None

    def to_row(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "event_id": self.event_id,
            "payload_json": json.dumps(self.payload, ensure_ascii=False),
            "headers_json": json.dumps(self.headers, ensure_ascii=False),
            "status": self.status.value,
            "attempts": self.attempts,
            "next_attempt_at": self.next_attempt_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "last_error": self.last_error,
        }


_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    event_id TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    headers_json TEXT NOT NULL,
    status TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    next_attempt_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    last_error TEXT,
    UNIQUE(source, event_id)
);

CREATE INDEX IF NOT EXISTS idx_jobs_status_next ON jobs(status, next_attempt_at);

CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    attempt_number INTEGER NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    success INTEGER NOT NULL DEFAULT 0,
    error TEXT,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

CREATE TABLE IF NOT EXISTS dead_letter (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    event_id TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    headers_json TEXT NOT NULL,
    attempts INTEGER NOT NULL,
    last_error TEXT,
    died_at TEXT NOT NULL,
    resolved INTEGER NOT NULL DEFAULT 0,
    resolved_note TEXT
);

CREATE INDEX IF NOT EXISTS idx_dead_letter_unresolved ON dead_letter(resolved, died_at);
"""


class RetryQueue:
    """Cola persistente de webhooks pendientes.

    Uso típico:
        q = RetryQueue()
        q.enqueue('stripe', 'evt_123', payload, headers)
        # ... en otro proceso ...
        worker = QueueWorker(q, dispatch_fn=handlers.dispatch.dispatch)
        worker.run_forever()
    """

    def __init__(
        self,
        db_path: Path | None = None,
        *,
        max_attempts: int = 5,
        backoff_seconds: list[int] | None = None,
    ) -> None:
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.max_attempts = max_attempts
        self.backoff_seconds = backoff_seconds or DEFAULT_BACKOFF_SECONDS
        self._init_schema()

    def _init_schema(self) -> None:
        with self._conn() as conn:
            conn.executescript(_SCHEMA)
            conn.commit()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, isolation_level="DEFERRED")
        conn.row_factory = sqlite3.Row
        # WAL mejora concurrencia entre worker y FastAPI handlers
        with closing(conn.cursor()) as cur:
            cur.execute("PRAGMA journal_mode=WAL")
            cur.execute("PRAGMA synchronous=NORMAL")
        return conn

    # ------- enqueue -------

    def enqueue(
        self,
        source: str,
        event_id: str,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> int:
        """Encola un webhook. Si ya existe (source, event_id), retorna id existente.

        Returns:
            id del job en la cola.
        """
        now = datetime.now(timezone.utc)
        job = Job(
            id=None,
            source=source,
            event_id=event_id,
            payload=payload,
            headers=headers,
            status=JobStatus.PENDING,
            attempts=0,
            next_attempt_at=now,
            created_at=now,
        )
        row = job.to_row()
        with self._conn() as conn:
            try:
                cur = conn.execute(
                    """INSERT INTO jobs
                       (source, event_id, payload_json, headers_json, status, attempts, next_attempt_at, created_at, last_error)
                       VALUES (:source, :event_id, :payload_json, :headers_json, :status, :attempts, :next_attempt_at, :created_at, :last_error)""",
                    row,
                )
                conn.commit()
                return cur.lastrowid or 0
            except sqlite3.IntegrityError:
                # Ya existía — devolver id existente
                cur = conn.execute(
                    "SELECT id FROM jobs WHERE source=? AND event_id=?",
                    (source, event_id),
                )
                existing = cur.fetchone()
                return existing["id"] if existing else 0

    # ------- claim / process -------

    def claim_next(self) -> Job | None:
        """Reclama el siguiente job listo. Marca status=in_progress atómicamente.

        Returns None si no hay jobs listos.
        """
        now = datetime.now(timezone.utc).isoformat()
        with self._conn() as conn:
            cur = conn.execute(
                """SELECT * FROM jobs
                   WHERE status=? AND next_attempt_at <= ?
                   ORDER BY next_attempt_at ASC
                   LIMIT 1""",
                (JobStatus.PENDING.value, now),
            )
            row = cur.fetchone()
            if row is None:
                return None
            conn.execute(
                "UPDATE jobs SET status=? WHERE id=? AND status=?",
                (JobStatus.IN_PROGRESS.value, row["id"], JobStatus.PENDING.value),
            )
            if conn.total_changes == 0:
                # Race condition: otro worker se lo llevó
                conn.commit()
                return self.claim_next()
            conn.commit()
        return self._row_to_job(row)

    def mark_success(self, job_id: int, attempt_number: int) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._conn() as conn:
            conn.execute(
                "UPDATE jobs SET status=?, last_error=NULL WHERE id=?",
                (JobStatus.DONE.value, job_id),
            )
            conn.execute(
                """INSERT INTO attempts (job_id, attempt_number, started_at, finished_at, success, error)
                   VALUES (?, ?, ?, ?, 1, NULL)""",
                (job_id, attempt_number, now, now),
            )
            conn.commit()

    def mark_failure_or_dead(
        self, job: Job, attempt_number: int, error: str
    ) -> str:
        """Falla un attempt. Si excede max_attempts → dead-letter.

        Returns: "retry" si quedó en queue, "dead" si fue a dead-letter.
        """
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat()
        new_attempts = job.attempts + 1

        with self._conn() as conn:
            conn.execute(
                """INSERT INTO attempts (job_id, attempt_number, started_at, finished_at, success, error)
                   VALUES (?, ?, ?, ?, 0, ?)""",
                (job.id, attempt_number, now_iso, now_iso, error[:2000]),
            )

            if new_attempts >= self.max_attempts:
                # Mover a dead-letter
                conn.execute(
                    """INSERT INTO dead_letter
                       (source, event_id, payload_json, headers_json, attempts, last_error, died_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        job.source,
                        job.event_id,
                        json.dumps(job.payload, ensure_ascii=False),
                        json.dumps(job.headers, ensure_ascii=False),
                        new_attempts,
                        error[:2000],
                        now_iso,
                    ),
                )
                conn.execute(
                    "UPDATE jobs SET status=?, attempts=?, last_error=? WHERE id=?",
                    (JobStatus.DEAD.value, new_attempts, error[:2000], job.id),
                )
                conn.commit()
                return "dead"
            else:
                # Re-encolar con backoff
                backoff_idx = min(new_attempts - 1, len(self.backoff_seconds) - 1)
                backoff = self.backoff_seconds[backoff_idx]
                next_attempt = now_dt.timestamp() + backoff
                next_attempt_iso = datetime.fromtimestamp(
                    next_attempt, tz=timezone.utc
                ).isoformat()
                conn.execute(
                    """UPDATE jobs
                       SET status=?, attempts=?, next_attempt_at=?, last_error=?
                       WHERE id=?""",
                    (
                        JobStatus.PENDING.value,
                        new_attempts,
                        next_attempt_iso,
                        error[:2000],
                        job.id,
                    ),
                )
                conn.commit()
                return "retry"

    # ------- queries -------

    def get_stats(self) -> dict[str, int]:
        with self._conn() as conn:
            cur = conn.execute(
                "SELECT status, COUNT(*) AS c FROM jobs GROUP BY status"
            )
            stats = {row["status"]: row["c"] for row in cur.fetchall()}
            cur = conn.execute("SELECT COUNT(*) AS c FROM dead_letter WHERE resolved=0")
            stats["dead_letter_unresolved"] = cur.fetchone()["c"]
            return stats

    def list_dead_letter(self, *, unresolved_only: bool = True, limit: int = 50) -> list[dict[str, Any]]:
        with self._conn() as conn:
            where = "WHERE resolved=0" if unresolved_only else ""
            cur = conn.execute(
                f"SELECT * FROM dead_letter {where} ORDER BY died_at DESC LIMIT ?",
                (limit,),
            )
            return [dict(row) for row in cur.fetchall()]

    def resolve_dead_letter(self, dead_id: int, note: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE dead_letter SET resolved=1, resolved_note=? WHERE id=?",
                (note, dead_id),
            )
            conn.commit()

    def _row_to_job(self, row: sqlite3.Row) -> Job:
        return Job(
            id=row["id"],
            source=row["source"],
            event_id=row["event_id"],
            payload=json.loads(row["payload_json"]),
            headers=json.loads(row["headers_json"]),
            status=JobStatus(row["status"]),
            attempts=row["attempts"],
            next_attempt_at=datetime.fromisoformat(row["next_attempt_at"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            last_error=row["last_error"],
        )


class QueueWorker:
    """Worker que procesa jobs de la cola. Pensado para correr como background task
    o proceso separado.

    Uso:
        from app.handlers.dispatch import dispatch
        worker = QueueWorker(RetryQueue(), dispatch_fn=dispatch)
        worker.run_forever()  # bloquea — correr en thread/proceso

    Para tests:
        result = worker.tick()  # procesa un job y retorna
    """

    def __init__(
        self,
        queue: RetryQueue,
        dispatch_fn: Callable[[str, dict[str, Any], dict[str, str]], dict[str, Any]],
        *,
        idle_sleep_seconds: float = 5.0,
    ) -> None:
        self.queue = queue
        self.dispatch_fn = dispatch_fn
        self.idle_sleep_seconds = idle_sleep_seconds
        self._stop = False

    def tick(self) -> Optional[dict[str, Any]]:
        """Procesa un job si hay uno listo. Retorna info o None si idle."""
        job = self.queue.claim_next()
        if job is None:
            return None
        try:
            result = self.dispatch_fn(job.source, job.payload, job.headers)
            self.queue.mark_success(job.id or 0, job.attempts + 1)
            return {"job_id": job.id, "outcome": "success", "result": result}
        except Exception as exc:
            outcome = self.queue.mark_failure_or_dead(job, job.attempts + 1, str(exc))
            return {"job_id": job.id, "outcome": outcome, "error": str(exc)}

    def run_forever(self) -> None:
        while not self._stop:
            result = self.tick()
            if result is None:
                time.sleep(self.idle_sleep_seconds)

    def stop(self) -> None:
        self._stop = True
