# Guía de desarrollo

**Propósito**: cómo extender, modificar y contribuir al monorepo.

**Audiencia**: desarrolladores que quieren agregar skills, verticales, o corregir contenido.

**Pre-lectura**: [arquitectura.md](arquitectura.md), [glosario-tecnico.md](glosario-tecnico.md).

---

## Filosofía de contribución

1. **`_shared/` es fuente de verdad**: nunca editar `<plugin>/skills/<shared>/SKILL.md` directamente. Editar en `_shared/` y resync.
2. **Skills propios viven en `<plugin>/skills/`**: con la convención de naming del vertical.
3. **References crecen orgánicamente**: cuando un skill cite algo complejo, mover a `references/`.
4. **Tests primero para skills de cálculo**: si tu skill calcula impuestos/totales, agrega fixtures.
5. **Lint passing siempre**: commits que rompen `lint-skills.sh` no entran.
6. **CHANGELOG actualizado**: documentar cambios en `CHANGELOG.md` del plugin afectado.

---

## Estructura esperada de un skill

```
<skill-name>/
├── SKILL.md                    # Obligatorio
│   ├── frontmatter
│   │   ├── name (kebab-case)
│   │   ├── description (>80 chars, español MX + sinónimos inglés)
│   │   └── allowed-tools (opcional)
│   └── cuerpo Markdown estructurado
└── references/                 # Opcional
    ├── <referencia-1>.md
    └── <referencia-2>.md
```

### Estructura recomendada del cuerpo

```markdown
# Nombre del skill

[1-2 párrafos: qué hace y por qué importa]

## Cuándo usar este skill
[Triggers explícitos]

## Cuándo NO usar
[Disambiguación]

## Conocimiento base obligatorio
[Reglas/catálogos/normas que el skill aplica]

## Reglas/Validaciones críticas
[Checks que evitan errores silenciosos]

## Flujo
[Paso a paso de cómo opera]

## Casos edge
[Mínimo 3-5 con cómo manejarlos]

## Salida esperada
[Estructura del output]

## Integración con otros skills
[Skills relacionados]

## ⚠ Datos que requieren verificación vigente
[Lo que necesita validación de fuente oficial actual]
```

---

## Agregar un nuevo skill compartido

### 1. Decidir si es shared o vertical

**Shared** si: aplica a múltiples verticales (CFDI, IVA, RFC, WA, LFPDPPP, MXN).
**Vertical** si: solo aplica a un sector específico.

### 2. Crear directorio en `_shared/`

```bash
cd ~/plugins-mx
mkdir -p _shared/mi-skill-nuevo
```

### 3. Crear `SKILL.md` siguiendo plantilla

```yaml
---
name: mi-skill-nuevo
description: [Descripción detallada en español MX + sinónimos inglés + cuándo NO usar. Mínimo 80 caracteres, idealmente 200-400.]
allowed-tools: Read, Write, Edit
---

# Título del skill

[Contenido siguiendo estructura recomendada]
```

### 4. Validar con lint

```bash
./scripts/lint-skills.sh
```

### 5. Actualizar `plugin.json` de cada vertical que lo use

Agregar `"skills/mi-skill-nuevo"` al array de `"skills"` en el plugin.json del vertical.

### 6. Sincronizar

```bash
./scripts/sync-shared.sh
```

### 7. Agregar a `CHANGELOG.md`

```markdown
## [Unreleased]
### Added
- New shared skill `mi-skill-nuevo`: [descripción]
```

### 8. Crear eval y fixture (recomendado)

```bash
# Eval
touch evals/_shared/mi-skill-nuevo.eval.json
# Llenar con 10+ should_trigger y 10+ should_not_trigger

# Fixture (si aplica)
mkdir -p tests/fixtures/mi-skill-nuevo
touch tests/fixtures/mi-skill-nuevo/case-01-feliz.json
```

---

## Agregar un skill propio a un vertical

### 1. Crear directorio en `<vertical>/skills/`

```bash
cd ~/plugins-mx
mkdir -p freelancers-mx/skills/mi-skill-propio
```

### 2. Crear `SKILL.md`

Mismo formato que skill compartido pero con contenido específico del vertical.

### 3. Actualizar `<vertical>/plugin.json`

```json
{
  "skills": [
    "skills/mi-skill-propio",
    ...
  ]
}
```

### 4. Lint + commit

```bash
./scripts/lint-skills.sh
git add freelancers-mx/skills/mi-skill-propio/
git commit -m "feat(freelancers-mx): add skill mi-skill-propio"
```

**Nota**: skills propios NO se tocan por `sync-shared.sh` (el script solo sincroniza los del `plugin.json` que están en `_shared/`).

---

## Agregar un vertical nuevo

### 1. Decidir nombre y scope

Convención: `<dominio>-mx` o `<dominio>-latam`. Ej. `salon-mx`, `veterinaria-mx`, `wedding-planner-mx`.

### 2. Crear estructura base

```bash
cd ~/plugins-mx
mkdir -p salon-mx/.claude-plugin salon-mx/skills salon-mx/commands
```

### 3. Crear `plugin.json`

```json
{
  "name": "salon-mx",
  "displayName": "Salon MX",
  "description": "[Descripción 1-2 párrafos]",
  "version": "0.1.0",
  "author": { "name": "...", "email": "..." },
  "keywords": ["salon", "estetica", "mexico", ...],
  "skills": [
    "skills/<skill-propio-1>",
    "skills/<skill-propio-2>",
    "skills/cfdi-emision",
    "skills/iva-retenciones-mx",
    "skills/rfc-validacion",
    "skills/whatsapp-business-mx",
    "skills/compliance-lfpdppp",
    "skills/mxn-formato"
  ],
  "commands": [
    "commands/<command-1>.md",
    ...
  ],
  "compatibility": {
    "claudeCode": ">=1.0.0",
    "requires": ["core-mexico"]
  }
}
```

### 4. Crear skills propios (3-5 típicamente)

Siguiendo plantilla.

### 5. Crear commands

Archivos `.md` en `commands/`.

### 6. Crear README

```markdown
# salon-mx

[Descripción]

## Skills propios
| Skill | Propósito |
...

## Commands
- `/salon:<command>` — ...

## Usuario objetivo
...

## Filosofía
...
```

### 7. Crear `.mcp.json` con servidores mockeables

### 8. Sincronizar `_shared/`

```bash
./scripts/sync-shared.sh salon-mx
```

### 9. Validar lint

```bash
./scripts/lint-skills.sh
```

### 10. Actualizar `marketplace.json`

Mover el nuevo plugin de `comingSoon` a `plugins`.

### 11. Crear CHANGELOG.md propio del vertical

### 12. Crear eval set y fixtures iniciales

### 13. Commit

```bash
git add .
git commit -m "feat(salon-mx): scaffold initial vertical"
```

---

## Modificar un skill compartido

### El flujo correcto

1. Editar `_shared/<skill>/SKILL.md` (NUNCA `<plugin>/skills/<skill>/`)
2. Actualizar references si cambió el contenido relevante
3. Actualizar eval si cambió el dominio del skill (triggering)
4. Actualizar fixtures si cambió el output esperado
5. Correr `sync-shared.sh`
6. Lint
7. Commit con mensaje `fix(_shared): <skill> ajuste de <qué>`

### Qué NO hacer

- Editar `<plugin>/skills/<shared>/SKILL.md` directamente: pierde cambios al siguiente sync
- Borrar references sin actualizar SKILL.md: deja referencias rotas
- Cambiar `name:` del skill: rompe `plugin.json` de los verticales que lo declaran

---

## Marcar datos que requieren verificación vigente

Si tu skill cita un dato del SAT, INAI, Meta, PROFECO que puede actualizarse, agrega o expande la sección:

```markdown
## ⚠ Datos que requieren verificación vigente

1. **[Nombre del dato]**: [explicación del riesgo]. Validar contra [fuente oficial].
2. ...

**Antes de exponer a cliente**: [pasos específicos].
```

Esto cumple el principio de "honestidad antes de profesionalismo": el usuario que ve el ⚠ sabe qué validar antes de confiar.

---

## Estilo de descripción para triggering

### Lo que funciona

- **Específico**: `"Emite CFDI 4.0 conforme reglas vigentes del SAT en México. Cubre tipos I/E/T/N/P..."`
- **Con sinónimos del usuario real**: `"Usar cuando el usuario diga facturar, timbrar, emitir CFDI, comprobante fiscal, refacturar, cancelar factura"`
- **Inglés también**: `"...generate invoice, issue tax invoice..."`
- **Con "NO usar para"**: `"NO usar para facturas de Argentina/Colombia/España ni para órdenes de compra/cotizaciones (esas no se timbran)"`

### Lo que NO funciona

- Genérico: `"Skill para facturas"`
- Sin contraejemplos: `"Skill para CFDI"` (puede triggear cuando no debe)
- Solo en inglés en proyecto MX: `"Generate invoices"`
- Demasiado corto: <80 caracteres no pasa el lint y no triggea bien

---

## Calibración de descriptions

### Workflow manual

1. Toma el eval del skill: `evals/<vertical>/<skill>.eval.json`
2. Por cada prompt con `should_trigger: true`, prueba en una sesión con el plugin cargado
3. Anota: triggeó el skill correcto? Sí/No
4. Por cada prompt con `should_trigger: false`, prueba
5. Anota: triggeó algún skill? Cuál?
6. Calcula accuracy = (true positives + true negatives) / total
7. Si <85%, ajusta el `description:` para resolver los failures
8. Repite

### Workflow automatizado (con skill-creator)

```bash
cd ~/plugins-mx/<path-al-skill-creator>
python -m scripts.run_loop \
  --eval-set ../plugins-mx/evals/freelancers-mx/cotizacion-mxn.eval.json \
  --skill-path ../plugins-mx/freelancers-mx/skills/cotizacion-mxn \
  --model claude-opus-4-7 \
  --max-iterations 5 \
  --verbose
```

Esto itera automáticamente proponiendo descriptions mejoradas y midiendo accuracy contra el eval.

---

## Cuándo crear un agent vs skill

| Característica | Skill | Agent |
|---|---|---|
| Contexto | Compartido con Claude principal | Aislado |
| Cuándo carga | Por trigger automático | Por invocación explícita |
| Útil para | Conocimiento/capacidad reutilizable | Tarea costosa, ruidosa, paralelizable |
| Ejemplo | `cfdi-emision` | `validador-cfdi-batch` que valida 500 CFDIs |

**Crear agent si**:
- La tarea consumirá muchos tokens
- Producirá output ruidoso (logs, debugging) que no quieres en contexto principal
- Es paralelo a múltiples instancias
- Requiere herramientas restringidas que el contexto principal no necesita

---

## Commits y versionado

### Mensajes de commit (convencional)

- `feat(<scope>): <desc>` — nueva funcionalidad
- `fix(<scope>): <desc>` — corrección de bug
- `docs(<scope>): <desc>` — documentación
- `refactor(<scope>): <desc>` — refactor sin cambio de comportamiento
- `chore(<scope>): <desc>` — tooling, scripts
- `test(<scope>): <desc>` — tests/fixtures

Donde `<scope>` es: `freelancers-mx`, `_shared`, `agencia-marketing-mx`, etc.

### Versionado semver

Cada plugin tiene su propio `version` en `plugin.json`:
- **major (1.0.0)**: cambio breaking (descripcion, schema, comportamiento esperado cambia)
- **minor (0.x.0)**: nuevo skill, nuevo command, nueva integración
- **patch (0.0.x)**: bugfix, mejora descripción, actualización catálogo

Cambios en `_shared/` que rompen contratos → bump minor de TODOS los plugins que lo usen.

### Tags git

```bash
git tag freelancers-mx-v0.2.0
git push origin freelancers-mx-v0.2.0
```

Convención: `<plugin-name>-v<version>`.

---

## Validación pre-commit (recomendado configurar)

`.git/hooks/pre-commit`:
```bash
#!/usr/bin/env bash
./scripts/lint-skills.sh || exit 1
```

Bloquea commits con skills mal formateados.

---

## Cómo agregar un nuevo idioma/región (futuro)

Si querer extender a `colombia-mx` o similar:

1. Considerar si vale la pena fork o `_shared/<region>/`
2. Si fork: nuevo monorepo `plugins-co` con su propia base
3. Si shared: `_shared/co/cfdi-equivalente-co/` o similar

Por ahora: out of scope (foco en México).

---

## Ver también

- [arquitectura.md](arquitectura.md) — diseño del monorepo
- [versionado.md](versionado.md) — política de versiones
- [estado-real.md](estado-real.md) — qué se considera producción-grade
