# ADR 004 — Retry queue persistente con SQLite (no Redis)

**Status**: ACEPTADO  (2026-06-12)

## Context

El webhook receiver V1 procesaba handlers síncronamente best-effort: si un handler fallaba (timeout PAC, error 500 transitorio), el evento se perdía. Para V2 necesitábamos una cola persistente con reintentos y dead-letter.

El volumen esperado es **<1000 webhooks/día por instancia**: PyMEs con cobros recurrentes + cierres fiscales mensuales + integraciones de marketplace. Lejos del régimen donde una cola distribuida tiene sentido.

## Decision

Implementar `app/retry_queue.py` con **SQLite local** + WAL mode + backoff exponencial + dead-letter table. Sin dependencias externas. Worker en proceso separado o background task que llama a `claim_next() → dispatch → mark_success/mark_failure_or_dead`.

Backoff: `[30s, 2m, 10m, 1h, 6h]` con `max_attempts=5`. Total < 12h (no atrasar webhooks más de medio día).

## Alternatives considered

1. **Redis + Celery / RQ** — estándar de industria. Descartado por:
   - Una dependencia externa más (Redis) que el operador debe instalar/mantener.
   - Overkill para <1000 webhooks/día.
   - Onboarding más complejo.

2. **Cloudflare Queues / AWS SQS** — escala infinita pero requiere lock-in a cloud + costo + manejar conexión desde local development. Para PyMEs autoadministradas: NO.

3. **In-memory queue** — pierde eventos si el proceso reinicia. Inaceptable para pagos.

4. **PostgreSQL con SKIP LOCKED** — más robusto que SQLite para concurrencia alta. Pero requiere otro servicio corriendo. Para volumen actual no se justifica.

## Consequences

**Positivas**:
- Cero dependencias externas. Funciona local + en Railway/CF Container con persistent volume.
- WAL mode permite worker + receiver concurrentes.
- Dead-letter table explícita: el operador puede ver/resolver casos huérfanos.
- 13 tests del queue + worker (42 total en webhooks).

**Negativas**:
- SQLite NO escala a múltiples instancias concurrentes (lock contention con WAL es bajo pero existe). Si el proyecto crece a >5000 webhooks/día, migrar a Postgres SKIP LOCKED.
- Cloudflare Workers Python NO soporta SQLite — requiere migrar a D1 si se elige esa plataforma. Documentado en `webhooks/DEPLOY.md`.

## Ver también

- `webhooks/app/retry_queue.py`
- `webhooks/DEPLOY.md` opción A (Railway) vs B (Cloudflare).
- `webhooks/tests/test_retry_queue.py`
