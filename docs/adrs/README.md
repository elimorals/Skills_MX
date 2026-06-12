# Architecture Decision Records (ADRs)

Decisiones arquitecturales clave del proyecto `plugins-mx`, documentadas con su contexto + alternativas consideradas + consecuencias. Útil para entender el "por qué" de elecciones que sin documentar parecen arbitrarias.

## Formato

Cada ADR sigue el patrón:
- **Status**: PROPUESTO / ACEPTADO / SUPERSEDED por ADR-N / DEPRECATED
- **Context**: qué problema veníamos enfrentando
- **Decision**: qué decidimos hacer
- **Alternatives considered**: qué descartamos y por qué
- **Consequences**: qué pasó después (positivas + negativas)

## Lista vigente

| ADR | Decisión | Status |
|---|---|---|
| [001](001-shared-skills-source-of-truth.md) | `_shared/` como fuente de verdad sincronizada | ACEPTADO |
| [002](002-mcps-mock-first.md) | MCPs mock-first por default | ACEPTADO |
| [003](003-workflows-como-codigo.md) | Workflows como código ejecutable (no solo markdown) | ACEPTADO |
| [004](004-retry-queue-sqlite-no-redis.md) | Retry queue SQLite local (no Redis) | ACEPTADO |
| [005](005-playwright-selectors-versionados.md) | Selectores Playwright versionados en módulo separado | ACEPTADO |
| [006](006-evals-dual-trigger-no-trigger.md) | Evals con casos should-trigger + should-NOT-trigger | ACEPTADO |
| [007](007-dry-run-default-en-acciones-criticas.md) | dry_run=true default en workflows que mueven dinero/datos | ACEPTADO |
