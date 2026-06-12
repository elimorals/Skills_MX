"""Tests del retry queue + worker."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.retry_queue import (
    DEFAULT_BACKOFF_SECONDS,
    JobStatus,
    QueueWorker,
    RetryQueue,
)


@pytest.fixture
def queue(tmp_path: Path) -> RetryQueue:
    db = tmp_path / "queue.sqlite"
    return RetryQueue(db_path=db, max_attempts=3, backoff_seconds=[0, 0, 0])


def test_enqueue_creates_job(queue: RetryQueue):
    job_id = queue.enqueue(
        "stripe", "evt_001", {"foo": "bar"}, {"x-sig": "abc"}
    )
    assert job_id > 0
    stats = queue.get_stats()
    assert stats.get(JobStatus.PENDING.value) == 1


def test_enqueue_is_idempotent(queue: RetryQueue):
    a = queue.enqueue("stripe", "evt_001", {}, {})
    b = queue.enqueue("stripe", "evt_001", {}, {})
    assert a == b
    stats = queue.get_stats()
    assert stats.get(JobStatus.PENDING.value) == 1


def test_claim_returns_oldest(queue: RetryQueue):
    queue.enqueue("a", "1", {}, {})
    queue.enqueue("b", "2", {}, {})
    job = queue.claim_next()
    assert job is not None
    assert job.source == "a"
    assert job.event_id == "1"


def test_claim_marks_in_progress(queue: RetryQueue):
    queue.enqueue("a", "1", {}, {})
    job1 = queue.claim_next()
    assert job1 is not None
    # Otro claim no debería traerlo de nuevo
    job2 = queue.claim_next()
    assert job2 is None


def test_mark_success(queue: RetryQueue):
    queue.enqueue("a", "1", {}, {})
    job = queue.claim_next()
    assert job is not None
    queue.mark_success(job.id or 0, 1)
    stats = queue.get_stats()
    assert stats.get(JobStatus.DONE.value) == 1
    assert stats.get(JobStatus.PENDING.value, 0) == 0


def test_mark_failure_retries(queue: RetryQueue):
    queue.enqueue("a", "1", {}, {})
    job = queue.claim_next()
    assert job is not None
    outcome = queue.mark_failure_or_dead(job, 1, "boom")
    assert outcome == "retry"
    stats = queue.get_stats()
    assert stats.get(JobStatus.PENDING.value) == 1
    # Job re-claimable
    job2 = queue.claim_next()
    assert job2 is not None
    assert job2.attempts == 1


def test_mark_failure_goes_to_dead_letter_after_max(queue: RetryQueue):
    queue.enqueue("a", "1", {}, {})
    for attempt in range(1, 4):
        job = queue.claim_next()
        assert job is not None
        outcome = queue.mark_failure_or_dead(job, attempt, f"err {attempt}")
        if attempt < 3:
            assert outcome == "retry"
        else:
            assert outcome == "dead"
    stats = queue.get_stats()
    assert stats.get(JobStatus.DEAD.value) == 1
    assert stats.get("dead_letter_unresolved") == 1


def test_list_dead_letter(queue: RetryQueue):
    queue.enqueue("a", "1", {"k": "v"}, {})
    for attempt in range(1, 4):
        job = queue.claim_next()
        if job is None:
            break
        queue.mark_failure_or_dead(job, attempt, f"err {attempt}")
    dead = queue.list_dead_letter()
    assert len(dead) == 1
    assert dead[0]["source"] == "a"
    assert dead[0]["last_error"] == "err 3"


def test_resolve_dead_letter(queue: RetryQueue):
    queue.enqueue("a", "1", {}, {})
    for attempt in range(1, 4):
        job = queue.claim_next()
        if job is None:
            break
        queue.mark_failure_or_dead(job, attempt, "boom")
    dead = queue.list_dead_letter()
    queue.resolve_dead_letter(dead[0]["id"], "manualmente resuelto: facturado a mano")
    # Verificar que ya no aparece en unresolved
    assert queue.list_dead_letter(unresolved_only=True) == []
    # Pero sí en histórico
    all_dead = queue.list_dead_letter(unresolved_only=False)
    assert len(all_dead) == 1
    assert all_dead[0]["resolved"] == 1


def test_worker_tick_success(queue: RetryQueue):
    calls = {"n": 0}

    def fake_dispatch(source, payload, headers):
        calls["n"] += 1
        return {"ok": True}

    queue.enqueue("stripe", "evt_1", {"a": 1}, {})
    worker = QueueWorker(queue, dispatch_fn=fake_dispatch, idle_sleep_seconds=0)
    result = worker.tick()
    assert result is not None
    assert result["outcome"] == "success"
    assert calls["n"] == 1


def test_worker_tick_failure_then_retry(queue: RetryQueue):
    queue.enqueue("stripe", "evt_1", {}, {})

    def failing(source, payload, headers):
        raise RuntimeError("upstream caída")

    worker = QueueWorker(queue, dispatch_fn=failing, idle_sleep_seconds=0)
    result = worker.tick()
    assert result is not None
    assert result["outcome"] == "retry"
    assert "upstream" in result["error"]


def test_worker_tick_returns_none_when_idle(queue: RetryQueue):
    worker = QueueWorker(queue, dispatch_fn=lambda *_: {}, idle_sleep_seconds=0)
    assert worker.tick() is None


def test_backoff_constants_are_sensible():
    # Sanity: backoff debe ser creciente y razonable
    for i in range(len(DEFAULT_BACKOFF_SECONDS) - 1):
        assert DEFAULT_BACKOFF_SECONDS[i] < DEFAULT_BACKOFF_SECONDS[i + 1]
    # Total backoff < 12h (no atrasar webhooks > medio día)
    assert sum(DEFAULT_BACKOFF_SECONDS) < 12 * 3600
