# Workflows ejecutables (código real)

Scripts del skill `Workflow` con sintaxis `phase()` / `parallel()` / `pipeline()` / `agent()` / `log()` — invocables como `Workflow({scriptPath: "core-mexico/workflows/<nombre>.workflow.js", args: {...}})`.

## Por qué carpeta separada (no `agents/`)

- `agents/` contiene **subagentes** (markdown declarativo, prompts).
- `workflows/` contiene **orquestaciones ejecutables** (scripts JS con control de flujo).

Los workflows declarados en `agents/workflow-*.md` son las **plantillas conceptuales** (qué fases, qué MCPs, qué outputs). Los scripts en `workflows/*.workflow.js` son las **implementaciones ejecutables** de esas plantillas.

## Patrón estándar

```js
export const meta = {
  name: 'nombre-del-workflow',
  description: '... una sola oración ...',
  whenToUse: 'cuándo dispararlo (cron, /comando, manual)',
  phases: [
    { title: 'Fase 1', detail: 'qué hace' },
    { title: 'Fase 2', detail: 'qué hace' },
  ],
}

const { inputA, inputB } = args || {}
if (!inputA) throw new Error('args.inputA requerido')

phase('Fase 1')
const r1 = await parallel([
  () => agent('prompt 1', { schema: schema1() }),
  () => agent('prompt 2', { schema: schema2() }),
])

phase('Fase 2')
const r2 = await agent('procesar r1', { schema: schema3() })

return { resultado: r2, advertencias: [] }
```

## Reglas

- **Siempre tipar inputs con schemas** — el `Workflow` skill garantiza validación cuando se usa `schema:`.
- **Marcar `vigencia_validada`** en outputs que dependen de fuente externa cambiante (tarifa SAT, RMF). Default `false` hasta que un contador firme.
- **Usar `parallel()` solo cuando hay barrier real** (necesitas todos los resultados juntos). Para procesos con stages independientes, usar `pipeline()`.
- **Pasar IDs/hashes en bitácora**, no datos sensibles raw.
- **Soportar modo mock**: si los agents invocan MCPs en modo mock, el workflow debe correr sin fallar — devolverá data sintética con `simulated: true`.

## Workflows en este plugin (core-mexico)

| Archivo | Disparador típico |
|---|---|
| `cierre-fiscal-mensual.workflow.js` | Cron día 14 del mes / `/freelancers:cierre-fiscal` |

Pendientes de convertir desde `agents/workflow-*.md`:

- `workflow-cfdi-emision-completa.md` → `cfdi-emision-completa.workflow.js`
- `workflow-pago-conciliacion.md` → `pago-conciliacion.workflow.js`
- `workflow-due-diligence-cliente.md` → `due-diligence-cliente.workflow.js`
- `workflow-conciliacion-bancaria-mensual.md` → `conciliacion-bancaria.workflow.js`
- `workflow-emitir-cfdi-tras-pago.md` → `emitir-cfdi-tras-pago.workflow.js`
- `workflow-procesar-wa-pendientes.md` → `procesar-wa-pendientes.workflow.js`
- `workflow-verificar-conciliacion-5dia.md` → `verificar-conciliacion-5dia.workflow.js`
- `workflow-validacion-cfdis-historico.md` → `validacion-cfdis-historico.workflow.js`

Esfuerzo estimado por conversión: 25-40h (incluye tests).

## Ver también

- `agents/workflow-*.md` — plantillas declarativas originales
- `docs/specs/05-vertical-pf-anual-mx.md` — spec del vertical PF anual
- `docs/analisis-profundo-2026-06.md` §3.7 y §7 — por qué este gap importa
