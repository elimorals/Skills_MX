# Arquitectura del monorepo `plugins-mx` (Skills_MX)

> Cifras vigentes y estado de los MCPs: [README raíz](../../README.md) y [`mcp-servers/CATALOGO.md`](../../mcp-servers/CATALOGO.md).

## Componentes

| Pieza | Dónde | Qué hace |
|---|---|---|
| Skills (342) | `_shared/` (6 base) y `<vertical>/skills/` | Saben *qué* hacer: reglas fiscales, plantillas, flujos |
| MCP servers (83, 417 tools) | `mcp-servers/mp_*` + `shared/` | *Hacen* la consulta real: SAT, Banxico, municipios, pasarelas |
| Workflows (26) | `<plugin>/workflows/*.workflow.js` | Orquestan skills y MCPs para un proceso completo |
| Hooks (19) | `scripts/hooks/`, registrados en `.claude/settings.json` | Validan antes de acciones sensibles (timbrar, WhatsApp masivo) y llevan bitácora |
| Webhooks (13 handlers) | `webhooks/` | Receptor FastAPI de Stripe, Mercado Pago, Conekta, Facturama, WhatsApp… |
| Marketplace (40 plugins) | `.claude-plugin/marketplace.json` | Generado por `scripts/generar-marketplace.py` desde cada `plugin.json` |


## Modelo: `_shared/` + verticales

El monorepo separa **capacidades base reutilizables** de **plugins verticales por industria**:

```
_shared/  ← fuente de verdad para skills compartidos
  ├── cfdi-emision/
  ├── iva-retenciones-mx/
  ├── rfc-validacion/
  ├── whatsapp-business-mx/
  ├── compliance-lfpdppp/
  └── mxn-formato/

core-mexico/                    ← plugin base, instala los 6 anteriores
freelancers-mx/                 ← vertical, agrega skills propios + sync _shared/
colegios-mx/                    ← vertical, agrega skills propios + sync _shared/
talleres-mx/                    ← vertical, agrega skills propios + sync _shared/
...
```

### Por qué este modelo

Sin `_shared/`, cada vertical mantiene su propia copia de "cómo emitir CFDI 4.0". El día que el SAT publica una actualización en el Anexo 20 (cambio en catálogo, validación nueva), hay que actualizar N skills idénticos, propenso a olvidar uno y dejar verticales rotos.

Con `_shared/`, editamos una vez en la fuente de verdad y `sync-shared.sh` propaga a cada vertical antes del release. Los verticales son consumidores; nunca modifican `skills/<shared>/` directamente.

### Trade-off: distribución vs mantenibilidad

La sincronización física hace que cada vertical traiga una copia completa de las skills de `_shared/` más las suyas. Aun así, `core-mexico` se instala como base (`compatibility.requires`) porque aporta los MCPs comunes (Banxico, Facturama, SAT, Mercado Pago, Conekta…) que los verticales heredan.

**Consecuencia operativa**: nunca editar `core-mexico/skills/<x>/SKILL.md` ni `freelancers-mx/skills/<x>/SKILL.md` directamente para skills que vinieron de `_shared/`. Editar en `_shared/` y re-sincronizar.

## Política de versiones

- **Versionado semántico** para cada plugin (`major.minor.patch` en `plugin.json`).
- **Cambios en `_shared/`** que rompen contratos requieren bump `minor` en todos los plugins que consumen el skill afectado.
- **Tag git** por release: `core-mexico-v0.2.0`, `freelancers-mx-v0.1.0`, etc.

## Convenciones de naming

- **Plugins**: `<nombre>-<region>` o `<nombre>-<scope>` en kebab-case. Ej. `freelancers-mx`, `microdrama-latam`.
- **Skills compartidos**: descriptivos del dominio, sufijo `-mx` si es específico de México: `iva-retenciones-mx`, `compliance-lfpdppp`.
- **Skills de vertical**: prefijados con el nombre del vertical si hay riesgo de colisión con otro vertical. Ej. dentro de `freelancers-mx`, un skill podría llamarse `cotizacion-mxn` (no requiere prefijo porque no colisiona). Pero dentro de `salon-mx` el skill de inventario podría ser `salon-inventario` si hubiera otro `inventario` en otro vertical.
- **Commands**: namespace por plugin con `:`. Ej. `/freelancers:cotizar`, `/colegios:reporte-mensual`.

## Idioma de `description:`

Convención: **español MX prioritario, con sinónimos en inglés al final del párrafo**.

Razones:
1. Triggering robusto cuando el usuario escribe en español ("quiero facturar", "necesito un CFDI") y también en inglés ("send the invoice", "issue a tax receipt").
2. Los sinónimos en inglés aumentan recall sin penalizar especificidad porque van al final.
3. El cuerpo del SKILL.md está 100% en español MX porque ese es el público objetivo.

Patrón:
```yaml
description: [Descripción funcional en español MX, 1-2 oraciones]. Usar cuando el usuario diga [sinónimo MX 1], [sinónimo MX 2], [sinónimo MX 3], [sinónimo EN 1], [sinónimo EN 2]. NO usar para [caso 1], [caso 2].
```

La cláusula explícita `NO usar para...` previene over-triggering en casos adyacentes.

## MCPs: estado real, sin fallback silencioso

Regla vigente desde la oleada 1 ([ADR 008](../adrs/008-estado-real-sin-fallback-silencioso.md), reemplaza al ADR 002 "mock-first"):

1. **Sin credenciales**: el MCP responde datos de ejemplo marcados `simulated: true`. `PLUGINS_MX_MOCK=1` fuerza ese modo.
2. **Con credenciales**: consulta real. Cualquier error del proveedor se propaga como error tipado (`AuthError`, `UpstreamError`, `NotFoundError`, `ConfigError`…). Nunca se sustituye por datos de ejemplo.
3. **CAPTCHA o login**: entrega a humano con formato único (`shared/portal_handoff.py`). El solver de CAPTCHA (`shared/captcha_solver.py`) es opt-in con `PLUGINS_MX_CAPTCHA_SOLVER=2captcha` + `TWOCAPTCHA_API_KEY`.
4. **Sin API pública**: `ConfigError` con `motivo: sin_api_publica` y la alternativa manual.
5. **Estado documentado**: cada `mp_*/README.md` tiene la sección "Estado real", y `scripts/generar-estado-mcps.py` arma con ellas `mcp-servers/CATALOGO.md` y la tabla del README.

**Distribución**: los MCPs se lanzan con `uv run --no-project --with "plugins-mx-mcp-servers[extras] @ git+https://github.com/elimorals/Skills_MX@main#subdirectory=mcp-servers" python -m mp_x.server`. No hay `cwd` ni rutas locales; `scripts/mcp-config-portable.py --check` lo verifica en CI.

Para acciones que mueven dinero o datos, los workflows usan `dry_run=true` por defecto ([ADR 007](../adrs/007-dry-run-default-en-acciones-criticas.md)).

## Criterios de "producción-grade" para un skill

Un skill se considera producción cuando:

1. **Triggering**: 30+ prompts variados probados y triggers correctos ≥85%.
2. **Cobertura de dominio**: reglas oficiales actualizadas (SAT, INAI, Meta) referenciadas con vigencia.
3. **Casos edge documentados**: al menos 5 patrones edge en el SKILL.md con cómo manejarlos.
4. **Validaciones críticas**: chequeos que evitan errores fiscales/legales silenciosos. Lista explícita en el skill.
5. **Salida estructurada**: formato consistente (JSON intermedio + presentación legible al usuario).
6. **Tono apropiado**: matiz para usuario técnico vs no técnico.
7. **Integración honesta**: sin credenciales devuelve `simulated: true`; con credenciales, los errores se propagan.
8. **Lint passing**: `lint-skills.sh` lo aprueba.
9. **Validación con experto del dominio**: al menos un revisor del sector confirmó outputs reales (contador, abogado, dentista, etc.).

Hasta que se cumpla el #9, el skill está en estado **beta** y debe marcarse así en el README del plugin.

## Skills vs Agents vs Subagents

- **Skill (`SKILL.md` en `skills/`)**: capacidad reutilizable que Claude carga cuando detecta relevancia. No es un agente independiente; vive en el contexto del Claude principal.
- **Agent (`agents/<name>.md`)**: subagente que Claude despacha con tarea específica. Tiene su propio contexto, herramientas restringidas. Útil para tareas que merecen aislamiento (revisar grandes outputs, ejecutar validaciones complejas).
- **Subagent (lo mismo que Agent en plugin context)**: a veces el término se usa intercambiable.

**Cuándo usar cada uno**:
- ¿Es una capacidad/conocimiento que Claude usa inline? → Skill.
- ¿Es una tarea costosa o ruidosa que merece contexto separado? → Agent.
- ¿Es un workflow disparado por el usuario con sintaxis específica? → Command (en `commands/`).

Varios plugins traen agentes en `agents/` (p. ej. `validador-cfdi-batch` en `core-mexico`).

## Convenciones de Git

Commits convencionales:
- `feat(<plugin>): ...`
- `fix(<skill>): ...`
- `docs: ...`
- `chore(scripts): ...`
- `refactor(_shared): ...`

Sync de `_shared/` se hace **antes** de cada release y se commitea como parte del release.
