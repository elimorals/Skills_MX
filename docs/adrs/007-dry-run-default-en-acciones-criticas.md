# ADR 007 — `dry_run=true` por DEFAULT en workflows con efectos externos críticos

**Status**: ACEPTADO  (2026-06-12)

## Context

Algunos workflows ejecutables mueven dinero o envían masivamente a humanos reales:
- `dispersion-nomina` → SPEI Banxico a empleados (decenas de miles de pesos/quincena)
- `comunicacion-padres-masiva` → WhatsApp a cientos de padres simultáneamente
- `cobranza-multinivel` → mensajes formales a deudores que pueden generar fricción legal

Un parámetro `enviar=true` que el operador olvida activar es tolerable. Un parámetro `dry_run=false` que se confunde por `true` → catástrofe (10 deudores recibiendo cartas formales por error, 50 empleados sin nómina, padres molestos).

## Decision

Para workflows con efectos externos críticos, el default es **NO actuar**. El operador DEBE explícitamente pasar el flag de activación. Patrones:

- `dispersion-nomina`: `dry_run=true` default. Operador pasa `dry_run=false` con confirmación.
- `comunicacion-padres-masiva`: emite el plan + cuenta destinatarios. Envío real requiere paso adicional.
- `cobranza-multinivel`: `enviar_real=false` default → muestra los mensajes preparados sin enviar.

El output del workflow en modo dry-run debe ser INFORMATIVO (cantidad de destinatarios, mensajes generados, monto total) pero CERO acción externa.

## Alternatives considered

1. **Default true (siempre actúa)** — el patrón "Unix philosophy" de hacer lo que el usuario pidió. Descartado: incompatible con acciones irreversibles a humanos reales.
2. **Confirmación interactiva (Y/n)** — Claude Code no soporta prompts interactivos. Descartado.
3. **Modo "test" separado por env var** — añade fricción al testing local. Descartado.

## Consequences

**Positivas**:
- Imposible disparar acción real "por error" — requiere flag explícito + confirmar por el operador.
- Tests E2E pueden correr en dry-run sin moverse a dinero.
- Documentación del workflow muestra claramente `dry_run=true (default)` en cada `meta`.

**Negativas**:
- Operador familiarizado puede olvidar pasar `dry_run=false` y preguntarse por qué "no pasó nada". Mitigación: log explícito `🔵 DRY-RUN: ... NO enviado` en el workflow.
- Patrón inconsistente con workflows "seguros" donde default actúa (CFDI tras pago, debe emitirse siempre).

## Ver también

- `nomina-pymes-mx/workflows/dispersion-nomina.workflow.js`
- `freelancers-mx/workflows/cobranza-multinivel.workflow.js`
- ADR 003 (workflows como código) establece el patrón general
