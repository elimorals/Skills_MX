# ADR 003 — Workflows como código ejecutable (no solo markdown declarativo)

**Status**: ACEPTADO  (2026-06-12)

## Context

Durante los primeros meses del proyecto, los "workflows multinivel" se documentaron como **markdown declarativo** en `docs/specs/` y `<plugin>/agents/workflow-*.md`. Eran tablas con fases + paralelos + condicionales escritos en prosa.

El reconciliation análisis del 2026-06-12 reveló que:
- README y STATUS.md reportaban "23 workflows construidos"
- `find . -type d -name "workflow-*"` devolvía **cero** directorios físicos
- Cuando un cron quería disparar `cierre-fiscal-mensual`, no había nada que ejecutar

Era un **gap silencioso** que ningún reporte capturaba.

## Decision

Adoptar el skill `Workflow` del runtime de Claude Code como el contrato ejecutable de los workflows. Cada workflow vive en `<plugin>/workflows/<nombre>.workflow.js` con:

```js
export const meta = { name, description, whenToUse, phases: [...] }
phase('Nombre')
const r1 = await parallel([() => agent(...), () => agent(...)])
phase('Otra')
return { resultado, advertencias }
```

Los workflows declarativos en `<plugin>/agents/workflow-*.md` se mantienen como **plantillas conceptuales** (útiles para diseño, brief de contadores, documentación de PR), pero el orquestador real es el script JS.

## Alternatives considered

1. **Mantener solo markdown** — alineado con el resto del repo (todo en md) pero NO ejecutable. Descartado: el día que falle un cierre fiscal con $50k en juego, "el markdown lo dice" no aplica.
2. **Python con Temporal / Airflow / Prefect** — overhead enorme (infrastructura externa) para un proyecto que vive en filesystem local. Descartado.
3. **YAML declarativo custom** — habría que escribir el intérprete. El skill `Workflow` ya existe y es mantenido. Descartado.

## Consequences

**Positivas**:
- 16 workflows ejecutables con `phase()/parallel()/pipeline()/agent()/schemas`.
- Smoke test 16/16 (`scripts/smoke_test_workflows.py`) en CI.
- Disparables por cron/webhook/comando vía `Workflow({scriptPath, args})`.
- Mismo lenguaje (JS con schemas) que Claude entiende nativamente.

**Negativas**:
- Onboarding inicial necesita entender el patrón `Workflow` skill (no es estándar).
- Los markdown declarativos en `agents/` corren riesgo de divergir del código. Mitigación: regla cultural "el código es la fuente de verdad; el markdown se actualiza después".

## Ver también

- `core-mexico/workflows/README.md` — patrón estándar
- `scripts/smoke_test_workflows.py` — validación estructural
- ADR 007 (dry_run default) aplica especialmente a workflows con efectos externos.
