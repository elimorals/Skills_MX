# Arquitectura del monorepo `plugins-mx`

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

Claude Code no tiene "plugin dependencies" nativas — cada plugin se instala autocontenido. La sincronización física resuelve esto: cuando el usuario instala `colegios-mx`, recibe una copia completa de los `_shared/` skills más los específicos del vertical. No depende de tener `core-mexico` instalado.

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

## Integraciones mockeables

Filosofía: **ningún skill asume credenciales reales en su comportamiento default**.

Cada skill que normalmente llamaría a un servicio externo (PAC para CFDI, WhatsApp Business API, Banxico para tipo de cambio) debe:

1. Tener una interfaz abstracta documentada.
2. Implementar un **mock** que devuelva datos plausibles marcados con `simulated: true`.
3. Permitir override por variables de entorno (`FACTURAMA_API_KEY`, `GUPSHUP_API_KEY`, etc.).
4. Si la variable existe, intentar la llamada real; si no, devolver mock con advertencia clara al usuario.

Esto permite:
- Iterar sobre el skill sin credenciales.
- Hacer demos sin riesgo de timbrar/enviar de verdad.
- Probar el patrón completo y solo "encender" producción cuando el cliente quiere.

## Criterios de "producción-grade" para un skill

Un skill se considera producción cuando:

1. **Triggering**: 30+ prompts variados probados y triggers correctos ≥85%.
2. **Cobertura de dominio**: reglas oficiales actualizadas (SAT, INAI, Meta) referenciadas con vigencia.
3. **Casos edge documentados**: al menos 5 patrones edge en el SKILL.md con cómo manejarlos.
4. **Validaciones críticas**: chequeos que evitan errores fiscales/legales silenciosos. Lista explícita en el skill.
5. **Salida estructurada**: formato consistente (JSON intermedio + presentación legible al usuario).
6. **Tono apropiado**: matiz para usuario técnico vs no técnico.
7. **Integración mockeable**: funciona sin credenciales, marca claramente cuando es mock.
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

En `core-mexico` por ahora solo hay skills + commands. Agentes específicos por vertical (ej. `validador-cfdi-batch` para revisar lotes grandes de CFDIs) vendrán en cada plugin vertical cuando se justifiquen.

## Roadmap inmediato

1. Confirmar primer vertical con usuario (de los 16 sectores mapeados).
2. Scaffoldear `<vertical>/` con `.claude-plugin/plugin.json`, skills propios, commands, `.mcp.json`.
3. Implementar 2-3 skills core del vertical en calidad de producción.
4. Dogfooding interno antes de buscar partner.
5. Conseguir partner del sector para validación experta.
6. Iterar a producción-grade.
7. Lanzar a marketplace.

## Convenciones de Git (cuando se inicialice)

```bash
git init
git checkout -b main
# .gitignore: secrets, .mcp.json local con credenciales, node_modules, *.xml de pruebas
```

Commits convencionales:
- `feat(<plugin>): ...`
- `fix(<skill>): ...`
- `docs: ...`
- `chore(scripts): ...`
- `refactor(_shared): ...`

Sync de `_shared/` se hace **antes** de cada release y se commitea como parte del release.
