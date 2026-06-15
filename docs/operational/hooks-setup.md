# Hooks runtime de Claude Code — setup

> Spec: `docs/specs/04-hooks-runtime-claude-code.md`

Este documento describe los **13 hooks de Claude Code** (no git hooks) configurados en este repo.

Los hooks viven en `.claude/settings.json` y se ejecutan **automáticamente** durante una sesión cuando Claude Code llama a tools que coinciden con un `matcher`.

## Instalación

```bash
bash scripts/install-hooks.sh
```

Esto:
1. Instala git pre-commit (lo que ya hacía)
2. Marca los 13 hooks runtime como ejecutables
3. Verifica con smoke test (18 invocaciones)

Para verificar:

```bash
bash scripts/install-hooks.sh --check
```

## Lista de hooks

### PreToolUse (5)

Disparan **antes** de que Claude ejecute la tool. Si exit code = 2 → **bloquea** la tool call.

| Hook | Matcher | Bloquea si |
|---|---|---|
| `pre-timbrado-validation.sh` | `mp_facturama_extendido__timbrar_cfdi` | RFC inválido, totales faltantes, PUE+99, PPD sin forma 99 |
| `confirmar-envio-masivo-wa.sh` | `mp_meta_whatsapp__send_message_batch` | (solo warn) destinatarios > 50 |
| `validar-cfdi-payload.sh` | `mp_facturama_extendido__.*` | tool_input vacío/JSON roto |
| `validar-ficha-cliente.sh` | `Write/Edit/MultiEdit` | (solo warn) ficha cliente sin campos mínimos |
| `bitacora-mcp-calls.sh` | `mp_.*` | nunca (solo log) |

### PostToolUse (4)

Disparan **después** de la tool. No pueden bloquear; solo registran.

| Hook | Matcher |
|---|---|
| `backup-cfdi-automatico.sh` | `mp_facturama_extendido__timbrar_cfdi` |
| `alert-cancelaciones-frecuentes.sh` | `mp_facturama_extendido__cancelar_cfdi` |
| `actualizar-tc-banxico.sh` | `mp_banxico__.*` |
| `sincronizar-shared-post-edit.sh` | `Edit/Write/MultiEdit` |

### SessionStart (4: 1 orquestador + 3 sub-hooks)

Disparan al inicio de cada sesión.

| Hook | Acción |
|---|---|
| `contexto-inicial-sesion.sh` | Orquesta los 3 sub-hooks |
| ↳ `dashboard-cobranza-pendiente.sh` | Muestra cartera vencida si existe tracker |
| ↳ `alerta-pago-provisional.sh` | Si día del mes ∈ [14,17] alerta pago provisional |
| ↳ `cfdi-vencimientos.sh` | Alerta PPDs sin REP > 30d si hay tracker |

### Stop (1)

Cleanup al cerrar sesión.

| Hook | Acción |
|---|---|
| `cleanup-sesion.sh` | Compacta hook log > 100MB |

## Escapes y debug

| Necesidad | Comando |
|---|---|
| Saltarse todos los hooks (1 sesión) | `export CLAUDE_SKIP_HOOKS=1` |
| Cambiar umbral batch WhatsApp | `export PLUGINS_MX_WA_BATCH_UMBRAL=100` |
| Cambiar umbral cancelaciones | `export PLUGINS_MX_CANCEL_UMBRAL=5` |
| Ver últimos eventos | `tail -f ~/.local/share/plugins-mx/hooks/hook-events.jsonl` |
| Ver bitácora MCP calls | `tail -f ~/.local/share/plugins-mx/hooks/bitacora-mcp.jsonl` |
| Smoke test manual | `bash scripts/hooks/test-all-hooks.sh` |

## Variables de entorno respetadas

| Variable | Default | Uso |
|---|---|---|
| `CLAUDE_SKIP_HOOKS` | `0` | `=1` desactiva todos los hooks |
| `PLUGINS_MX_CACHE_DIR` | `~/.cache/plugins-mx` | Cache local |
| `PLUGINS_MX_SHARE_DIR` | `~/.local/share/plugins-mx` | Logs / tracker / backup |
| `PLUGINS_MX_WA_BATCH_UMBRAL` | `50` | Umbral aviso envío masivo |
| `PLUGINS_MX_CANCEL_UMBRAL` | `3` | Umbral alerta cancelaciones 24h |

## Diseño

- Cada hook es un script bash (~10-80 líneas) standalone, dependencia común en `_lib.sh`
- jq se usa donde está disponible; si no, el hook hace skip silencioso (no rompe)
- Stdin: Claude pasa JSON con `{tool_name, tool_input, tool_result?, ...}`
- Stdout/Stderr: el usuario los ve; útiles para mensajes informativos/warnings
- Exit codes: `0` = OK, `2` = bloquea (solo PreToolUse), otro = warning

## Por qué `.claude/settings.json` (project) en lugar de `.local.json` (user)

- Los matchers refieren a tools específicos del repo (`mp_*`, `_shared/`, etc.)
- Otros devs/usuarios del repo se benefician de los mismos hooks
- No contiene secretos (rutas relativas + scripts del repo)

## Limitaciones conocidas

- Hooks lentos > 5s pueden hacer Claude time out. Todos los hooks de este repo son < 100ms.
- En modo "Claude no detecta jq", los hooks que dependen de jq hacen skip silencioso. Recomendado: `brew install jq`.
- Confirmación interactiva (e.g. envío masivo WA) no es posible desde un hook bash — solo se imprime warning para que Claude o el usuario decidan.
