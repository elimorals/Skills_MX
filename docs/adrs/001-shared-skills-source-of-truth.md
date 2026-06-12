# ADR 001 — `_shared/` como fuente de verdad sincronizada

**Status**: ACEPTADO  (2026-04, sigue vigente)

## Context

Cada plugin vertical (`freelancers-mx`, `colegios-mx`, `talleres-mx`, etc.) necesita capacidades comunes: emisión CFDI 4.0, validación RFC, formato MXN, templates WhatsApp, compliance LFPDPPP.

Si cada vertical mantiene su propia copia del skill `cfdi-emision`, el día que el SAT publique una actualización del Anexo 20, hay que editarlo en N lugares idénticos. Propenso a olvidar uno y dejar verticales rotos.

Claude Code NO tiene "plugin dependencies" nativas — cada plugin se instala autocontenido.

## Decision

Crear directorio `_shared/` en la raíz con los skills base reutilizables (`cfdi-emision`, `iva-retenciones-mx`, `rfc-validacion`, `whatsapp-business-mx`, `compliance-lfpdppp`, `mxn-formato`). Cada vertical es **consumidor**: nunca edita su copia local, solo recibe sincronización vía `scripts/sync-shared.sh` antes de cada release.

Convención dura: `_shared/<skill>/SKILL.md` es la fuente. `<plugin>/skills/<shared-skill>/SKILL.md` es copia derivada.

## Alternatives considered

1. **NPM workspace / monorepo dependency tool** — Claude Code no consume `package.json`. Descartado.
2. **Symlinks** — frágiles en empaquetado/distribución cross-platform. Descartado.
3. **Cada vertical es responsable de su propia copia** — propenso a divergencia silenciosa (probado y demostrado fallido en otros proyectos). Descartado.
4. **Build step que injecta `_shared/` en cada plugin antes de zip** — opción válida pero requiere infraestructura CI. La sincronización con script bash es más simple y operable manualmente.

## Consequences

**Positivas**:
- Una sola edición en `_shared/cfdi-emision/SKILL.md` se propaga a todos los verticales con un `bash scripts/sync-shared.sh`.
- Cada plugin permanece autocontenido al distribuir (no requiere `core-mexico` pre-instalado).
- Pre-commit hook `sincronizar-shared-post-edit.sh` evita olvidar sync.
- Health check valida sincronización con `diff -q`.

**Negativas**:
- Cada plugin tiene archivos duplicados físicamente — desperdicio espacio (40 plugins × 6 shared = 240 copias).
- Tentación de editar `<plugin>/skills/<shared>/SKILL.md` directamente. Mitigación: hook + lint que alerta cuando una copia diverge.
- Sync no es automático: requiere disciplina del operador.

## Ver también

- `scripts/sync-shared.sh`
- `scripts/hooks/sincronizar-shared-post-edit.sh`
- `docs/arquitectura.md` § "Modelo `_shared/` + verticales"
