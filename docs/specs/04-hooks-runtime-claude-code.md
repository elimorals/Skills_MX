---
spec: "hooks-runtime-claude-code"
estado: "DRAFT"
creado: "2026-06-11"
autor: "Elias"
ultima_actualizacion: "2026-06-11"
esfuerzo_estimado_horas: [40, 80]
prioridad: "tier-1"
---

# Spec 04 — Hooks runtime de Claude Code (PreToolUse, PostToolUse, SessionStart, Stop)

## 1. Propósito

Implementar **13 hooks de Claude Code** que se disparan en eventos del runtime (no de git). Estos hooks ejecutan acciones automáticas durante una sesión:

- **PreToolUse**: validar antes de tool call (ej. validar payload CFDI antes de timbrar)
- **PostToolUse**: registrar después de tool call (ej. backup CFDI tras timbrado)
- **SessionStart**: contexto inicial cada sesión (ej. mostrar cobranza pendiente, alertas pago provisional)
- **Stop**: cleanup al terminar (ej. sincronizar `_shared/`, backup sesión)

Sin estos hooks el usuario tiene que **recordar** invocar comandos manualmente (riesgo: olvidar pagar provisional el día 17, olvidar backup CFDIs, mandar WhatsApp masivo sin confirmar, etc.).

## 2. Contexto y por qué es novedoso

- **Lo que existe**: `scripts/pre-commit.sh` (git hook) — distinto a hooks de Claude Code runtime.
- **Por qué es novedoso**: ningún hook de Claude Code (`PreToolUse`, `PostToolUse`, `SessionStart`, `Stop`) está configurado en el repo. Los hooks de Claude Code viven en `settings.json` (proyecto o usuario) y son **shell commands** que Claude ejecuta automáticamente.
- **Referencia plan original**: sección 8 "Hooks".

## 3. Alcance

**Dentro:**
- 13 hooks (lista en sección 5 del plan original)
- Configuración en `settings.json` del proyecto
- Cada hook = script bash o python ejecutable en `scripts/hooks/`
- Documentación setup en `docs/hooks-setup.md`
- Compatibilidad con `bash scripts/install-hooks.sh` (extender)

**Fuera (decisión deliberada):**
- Hooks que requieran credenciales reales en runtime (riesgo seguridad)
- Hooks que bloqueen la conversación > 5s (UX rota)
- Hooks que escriban a SAT real (riesgo)
- Configuración global de Claude Code (solo proyecto)

## 4. Inputs / outputs / schemas

### Configuración en `.claude/settings.json`

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mp_facturama_extendido__timbrar_cfdi",
        "hooks": [
          {
            "type": "command",
            "command": "bash scripts/hooks/pre-timbrado-validation.sh"
          }
        ]
      },
      {
        "matcher": "mp_meta_whatsapp__send_message_batch",
        "hooks": [
          {
            "type": "command",
            "command": "bash scripts/hooks/confirmar-envio-masivo-wa.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "mp_facturama_extendido__timbrar_cfdi",
        "hooks": [
          {
            "type": "command",
            "command": "bash scripts/hooks/backup-cfdi-automatico.sh"
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash scripts/hooks/contexto-inicial-sesion.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash scripts/hooks/cleanup-sesion.sh"
          }
        ]
      }
    ]
  }
}
```

### Output esperado de un hook (stdout)

```
✓ pre-timbrado-validation: payload válido
  - subtotal: $10,000.00
  - IVA 16%: $1,600.00
  - retenciones: $1,066.67 (IVA 2/3) + $1,000 (ISR 10%)
  - total: $9,533.33
  - RFC receptor: encontrado en padrón ACTIVO
  - sin alertas 69-B
```

Si el hook falla (exit code != 0), Claude **bloquea** la tool call.

## 5. Tools / hooks expuestos

### PreToolUse (5 hooks)
1. `pre-timbrado-validation.sh` — valida payload CFDI antes de timbrar (rfc, totales, método/forma consistente)
2. `confirmar-envio-masivo-wa.sh` — pide confirmación si batch WhatsApp > 50 destinatarios
3. `validar-cfdi-payload.sh` — valida JSON antes de cualquier construcción CFDI
4. `validar-ficha-cliente.sh` — al escribir ficha cliente, valida RFC, datos mínimos
5. `bitacora-mcp-calls.sh` — log estructurado de cada llamada MCP

### PostToolUse (4 hooks)
6. `backup-cfdi-automatico.sh` — tras timbrar, copia XML + PDF a backup
7. `alert-cancelaciones-frecuentes.sh` — si > 3 cancelaciones en 24h, alerta
8. `actualizar-tc-banxico.sh` — tras consulta banxico, refresca cache local
9. `sincronizar-shared-pre-commit.sh` — tras edit en `_shared/`, sincroniza a verticales

### SessionStart (3 hooks)
10. `dashboard-cobranza-pendiente.sh` — muestra cartera vencida al inicio
11. `alerta-pago-provisional.sh` — si hoy es día 14-17 del mes, recordar
12. `cfdi-vencimientos.sh` — alertar PPDs sin REP > 30 días

### Stop (1 hook)
13. `backup-sesion.sh` — backup de bitácora + cache al terminar sesión

## 6. Casos edge

| Caso | Comportamiento |
|---|---|
| Hook tarda > 5s | Claude continúa, log warning |
| Hook exit != 0 en PreToolUse | Bloquea tool call con mensaje del hook |
| Hook stdout vacío | OK silencioso (no es error) |
| Variable env no setada (ej. BANXICO_TOKEN) | Hook degrade gracefully con mock |
| 2 hooks PreToolUse mismo matcher | Ejecutan en orden, primer fallo bloquea |
| Usuario quiere saltarse hook | `CLAUDE_SKIP_HOOKS=1` env var |
| Hook llama a MCP que no existe | Log error pero no bloquea (no fatal) |

## 7. Dependencias

- **Librerías**: ninguna nueva (todo bash + jq + curl)
- **MCPs**: `mp_facturama_extendido`, `mp_banxico`, `mp_sat_portal` (algunos hooks consultan)
- **Filesystem**: `~/.cache/plugins-mx/` + `~/.local/share/plugins-mx/`
- **Setup**: requiere `.claude/settings.json` (no `.local.json` — debe commitearse)

## 8. Criterios de aceptación

- [ ] 13 scripts en `scripts/hooks/` ejecutables
- [ ] `.claude/settings.json` con configuración para los 13
- [ ] `scripts/install-hooks.sh` extendido para configurar settings.json
- [ ] Cada hook documentado en `docs/hooks-setup.md`
- [ ] Hooks ejecutan en < 3s típicamente
- [ ] Hooks degraded gracefully sin credenciales
- [ ] `CLAUDE_SKIP_HOOKS=1` deshabilita todos
- [ ] Tests manuales: dispara cada hook al menos una vez

## 9. Esfuerzo estimado

- **Setup `.claude/settings.json` + install-hooks.sh extendido**: 5-10h
- **13 hooks × 2-4h cada uno**: 26-52h
- **Tests + docs**: 10-20h
- **TOTAL**: **40-80 horas** (1-2 semanas FT)

## 10. Riesgos + mitigaciones

| Riesgo | Prob | Impacto | Mitigación |
|---|---|---|---|
| Hook lento bloquea Claude | Media | Alto | Timeout 5s + tests de performance |
| Hook PreToolUse rompe flow productivo | Media | Alto | Modo `CLAUDE_SKIP_HOOKS=1` siempre disponible |
| Settings.json se commitea con secretos | Baja | Crítico | Solo paths a scripts, env vars en `.env` |
| Hook PostToolUse pierde datos por error | Baja | Medio | Idempotente — no asume orden |
| Conflicto con hooks de otros plugins instalados | Baja | Bajo | Matchers específicos a tools de plugins-mx |

## 11. Decisiones pendientes

- [ ] ¿Hooks en `.claude/settings.json` (project, commiteable) o `.claude/settings.local.json` (user)? **Recomendado: project para que todos los devs los tengan**
- [ ] ¿Lenguaje uniforme bash o mezcla bash/python según hook?
- [ ] ¿Cómo manejar hooks que requieren credenciales? (skip si no setadas)
- [ ] ¿Activarlos por default al instalar el repo, o opt-in?
- [ ] ¿Métricas de uso (cuántas veces dispara cada hook)?

## 12. Plan de implementación

### Fase 1: Foundation (5-10h)
1. Crear `scripts/hooks/` directorio
2. Plantilla `_template.sh` para hooks
3. Extender `scripts/install-hooks.sh` para configurar settings.json
4. Crear `.claude/settings.json` con estructura vacía + comentarios

### Fase 2: SessionStart hooks (10-15h)
1. `contexto-inicial-sesion.sh` (orquestador)
2. `dashboard-cobranza-pendiente.sh`
3. `alerta-pago-provisional.sh`
4. `cfdi-vencimientos.sh`

### Fase 3: PreToolUse hooks (15-25h)
1. `pre-timbrado-validation.sh`
2. `confirmar-envio-masivo-wa.sh`
3. `validar-cfdi-payload.sh`
4. `validar-ficha-cliente.sh`
5. `bitacora-mcp-calls.sh`

### Fase 4: PostToolUse hooks (10-20h)
1. `backup-cfdi-automatico.sh`
2. `alert-cancelaciones-frecuentes.sh`
3. `actualizar-tc-banxico.sh`
4. `sincronizar-shared-post-edit.sh`

### Fase 5: Stop hook + docs (5-15h)
1. `cleanup-sesion.sh` / `backup-sesion.sh`
2. `docs/hooks-setup.md`
3. Update README + STATUS.md

## 13. Links

- Plan original: sección 8
- Claude Code hooks docs: https://docs.claude.com/en/docs/claude-code/hooks
- Git pre-commit existente: `scripts/pre-commit.sh`
