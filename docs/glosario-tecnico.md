# Glosario técnico — términos del monorepo

**Propósito**: Diccionario de términos técnicos usados en plugins-mx (Claude Code, MCP, plugin architecture, etc.).

**Audiencia**: cualquiera que vaya a leer o contribuir al código.

**Pre-lectura**: ninguna.

---

## A

### Agent (subagent)
Pieza de funcionalidad que Claude Code despacha en un contexto independiente. Tiene su propio system prompt, herramientas restringidas, y ventana de contexto separada del Claude principal. Útil para tareas costosas, ruidosas, o que requieren especialización.

En este monorepo: archivos `.md` en `<plugin>/agents/` con frontmatter (`name`, `description`, `tools`).

### `allowed-tools`
Campo del frontmatter de un command o agent. Limita qué herramientas puede usar Claude al ejecutar. Reduce riesgo de operaciones no deseadas.

Ejemplo: `allowed-tools: Read, Write, Edit, Bash`.

### Anthropic
Empresa que hace Claude. Provee la API.

---

## B

### Bundled resource
Archivo dentro del directorio de un skill (`references/`, `scripts/`, `assets/`) que el skill puede leer cuando necesita contenido específico. No se carga automáticamente; el skill lo invoca.

---

## C

### `.claude-plugin/`
Directorio que identifica un directorio como plugin de Claude Code. Contiene `plugin.json` con el manifest.

### CLAUDE.md
Archivo en root del proyecto donde el usuario define instrucciones persistentes para Claude Code. En este monorepo: el del usuario en `/Users/elias/CLAUDE.md`.

### Claude Code
CLI oficial de Anthropic para desarrollo asistido por Claude. Lee plugins, skills, commands, hooks.

### Command (slash command)
Workflow disparado por sintaxis específica (ej. `/freelancers:cotizar`). Archivo `.md` en `<plugin>/commands/` con instrucciones para Claude.

### Compatibility
Campo del `plugin.json` que declara versión mínima de Claude Code y otros plugins requeridos.

### Compaction
Cuando la conversación se acerca al límite del contexto, el sistema resume mensajes antiguos. El skill no debe asumir que todo el historial está disponible.

---

## D

### Deferred tool
Herramienta que existe pero su schema completo no está cargado en contexto inicialmente. Para usarla, primero hay que cargarla con ToolSearch. Optimiza uso de tokens.

### Description (del skill)
Campo del frontmatter `description:`. Es **la pieza más importante del skill** porque determina si Claude lo invoca. Debe ser específico, con sinónimos del usuario real, y casos de "NO usar para".

### Dogfooding
Práctica de usar tu propio producto en tu operación real para encontrar fallos. En este monorepo: tú usando `freelancers-mx` con tus propios clientes antes de exponerlo.

---

## E

### Eval / Evaluation
Conjunto de prompts con resultado esperado. Sirve para medir si un skill triggea correctamente o produce el output esperado. En este monorepo: archivos en `evals/`.

### EXTREMELY-IMPORTANT
Marcador en system prompts que Claude debe atender prioritariamente. Usado en el skill `using-superpowers` para forzar invocación de skills.

---

## F

### Fixture
Caso de prueba con input + expected output guardado para regresión. En este monorepo: `tests/fixtures/<skill>/case-NN.json`.

### Frontmatter
Bloque YAML al inicio de un archivo Markdown delimitado por `---`. Contiene metadata (name, description, allowed-tools, etc.). Es lo que Claude lee para decidir invocar el archivo.

---

## H

### Hook
Comando shell que se ejecuta en respuesta a un evento (PreToolUse, PostToolUse, SessionStart, etc.). Definido en `.claude/hooks.json` o `<plugin>/hooks/hooks.json`. Útil para versionado automático, validación, logging.

---

## I

### Inline (vs subagent)
Cuando Claude ejecuta una tarea en el contexto principal vs en un subagent aislado. Inline preserva contexto compartido; subagent ahorra tokens del principal.

### Isolation mode
Para subagents que modifican archivos: `worktree` crea un git worktree temporal para evitar conflicto con cambios concurrentes.

---

## J

### JSON Schema
Estándar para definir estructura de objetos JSON. En este monorepo: usado en `schemas/` para definir outputs estructurados de skills.

---

## L

### Lint passing
Pasa la validación de `scripts/lint-skills.sh`. Significa frontmatter correcto (name, description con ≥80 chars). NO significa contenido correcto.

---

## M

### MCP (Model Context Protocol)
Protocolo de Anthropic para que LLMs interactúen con servicios externos. Cada MCP server expone tools que Claude puede llamar. En este monorepo: definidos en `<plugin>/.mcp.json`, todos disabled por default.

### Manifest
Archivo `plugin.json` que declara qué contiene el plugin (skills, commands, agents, MCP, etc.). Es el "package.json" del plugin.

### Marketplace
Mecanismo de Claude Code para distribuir plugins. En este monorepo: `marketplace.json` define un marketplace privado.

### Mock
Implementación falsa de un servicio externo. Devuelve respuestas plausibles sin llamar al servicio real. Usado para iteración sin credenciales.

### Monorepo
Repositorio único que contiene múltiples paquetes/plugins. En este monorepo: 5 plugins + `_shared/` + tooling.

---

## N

### Namespacing
Convención para evitar colisiones. Commands usan `plugin:command` (ej. `/freelancers:cotizar`). Skills no necesitan prefijo si su nombre es único.

---

## O

### Output style
Modo de respuesta de Claude (concise, explanatory, learning). Cambia tono y nivel de detalle.

---

## P

### Plugin
Paquete autocontenido para Claude Code. Estructura: `.claude-plugin/plugin.json` + `skills/` + `commands/` + opcional `agents/`, `hooks/`, `.mcp.json`.

### `plugin.json`
Manifest del plugin. Campos clave: `name`, `description`, `version`, `skills`, `commands`, `compatibility`.

### Producción-grade
Estado de un skill que pasa los 9 puntos del checklist en `docs/arquitectura.md`. Incluye validación experta del dominio. En este monorepo: ninguno está aquí todavía.

### Progressive disclosure
Patrón de loading de skills en 3 niveles: metadata siempre cargada → SKILL.md cuando triggea → references bajo demanda. Optimiza tokens.

---

## R

### Reference
Documento que un skill puede leer cuando necesita info específica. Vive en `<skill>/references/`. Útil para catálogos largos, plantillas extensas, casos edge detallados.

### `requires`
Campo del `plugin.json` que declara qué otros plugins necesita. **Nota**: Claude Code no tiene dependency resolution nativa; este campo es declarativo.

---

## S

### Scaffolding
Estructura inicial vacía o con contenido genérico, lista para iteración. Distinto de producción.

### Schema
Estructura definida de un objeto. En este monorepo: JSON Schemas en `schemas/`.

### SKILL.md
Archivo principal de un skill. Frontmatter YAML + cuerpo Markdown. Vive en `<skill>/SKILL.md`.

### Skill
Capacidad reusable que Claude carga cuando detecta relevancia. Existe en el contexto principal de Claude, no como subagent.

### Skill standalone
Skill instalable independientemente (sin estar bundleado en un plugin). Usado vía `skillkit` o subido directamente a Claude.ai.

### Slash command
Sinónimo de command. Disparado con `/name`.

### `sync-shared.sh`
Script de tooling que copia `_shared/` a cada plugin que lo declara. Mantiene consistencia.

### System reminder
Mensaje inyectado en el contexto por el sistema. Provee información actualizada (estado de archivos, tasks, etc.). No proviene del usuario.

---

## T

### Task / TaskCreate
Herramienta de Claude Code para trackear sub-tareas dentro de una sesión. Útil para trabajo de 3+ pasos.

### Tool
Función específica que Claude puede invocar. Pueden ser nativas (Read, Write, Bash) o de MCP server.

### Triggering
Capacidad de un skill de ser invocado correctamente cuando el usuario habla de su dominio. Determinada por el `description:` del frontmatter.

---

## V

### Vertical
Plugin específico para una industria/sector. En este monorepo: freelancers-mx, agencia-marketing-mx, colegios-mx, talleres-mx.

### Vigencia validada
Etiqueta en fixtures que indica si el `expected_output` ha sido verificado contra fuente oficial vigente. En este monorepo: la mayoría `null` (no verificado).

---

## W

### Worktree
Copia de trabajo de un repo git en otra carpeta. Permite trabajo paralelo sin conflicto.

---

## Y

### YAML frontmatter
Sintaxis al inicio de archivos `.md`:
```yaml
---
name: skill-name
description: ...
allowed-tools: Read, Write
---
```

---

## Z

### Zero-config
Plugin que funciona sin credenciales adicionales. En este monorepo: todos por default (uso de mocks).

---

## Ver también

- [glosario-fiscal-mx.md](glosario-fiscal-mx.md) — términos fiscales mexicanos
- [arquitectura.md](arquitectura.md) — diseño del monorepo
- [guia-desarrollo.md](guia-desarrollo.md) — cómo contribuir
