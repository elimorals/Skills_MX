# ADR 006 — Evals con `should_trigger` + `should_NOT_trigger`

**Status**: ACEPTADO  (2026-04)

## Context

Cada skill de Claude Code se carga cuando su `description:` matchea con el contexto del prompt del usuario. Si el matching es muy laxo, se cargan skills irrelevantes (over-triggering: ruido en contexto, posibles acciones equivocadas). Si es muy estricto, no se cargan cuando deberían (under-triggering: el usuario pide algo y Claude no usa el skill correcto).

Necesitábamos una forma de **calibrar las `description:`** sistemáticamente.

## Decision

Cada skill que merece evaluación tiene un archivo `evals/<vertical>/<skill>.eval.json` con array de casos:

```json
[
  {"query": "factura colegiatura primaria", "should_trigger": true, "rationale": "Match directo CFDI D10 colegio"},
  {"query": "deducir universidad", "should_trigger": true, "rationale": "Casi edge — universidad NO deducible, skill debe responder esto"},
  {"query": "factura honorarios médicos", "should_trigger": false, "rationale": "D01 médico, no D10 colegio — distinto skill"}
]
```

Idealmente 10+ `should_trigger=true` + 10+ `should_trigger=false` por skill. Objetivo: ≥85% accuracy.

Los casos `should_trigger=false` son **tan importantes como los true**: previenen over-triggering en skills adyacentes (ej. "factura colegiatura primaria" debe disparar `cfdi-colegiaturas-deducibles` pero NO `cfdi-honorarios-d01`).

## Alternatives considered

1. **Solo casos positivos** — descubre over-triggering tarde, en producción. Descartado.
2. **Evaluación humana ad-hoc** — no replicable. Descartado.
3. **A/B test de descriptions** — vacío inicial (no hay tráfico real). Después de tracción real, complementario.

## Consequences

**Positivas**:
- 188 evals (.eval.json) cubren 49% de skills.
- Casos de `should_NOT` previenen errores típicos (ej. "facturar a mi cliente" NO debe triggerar `freelance-tax-mx`).
- Cuando una description se ajusta, los evals validan que no rompió otros casos.

**Negativas**:
- 51% de skills aún sin evals (health-check lo reporta). Trabajo pendiente.
- Correr los evals contra Claude real es manual hoy (skill `skill-creator` lo automatiza pero requiere `claude -p` con prompts en loop). Mitigación: los .eval.json son válidos como datos aunque no se ejecuten en CI todavía.

## Ver también

- `scripts/health-check.sh` reporta cobertura
- `evals/` por vertical
- ADR 003 (workflows como código) complementa: workflows + evals cubren el flujo completo.
