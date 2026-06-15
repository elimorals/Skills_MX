# Análisis profundo del proyecto `plugins-mx` — 2026-06-12

**Propósito**: documentar a profundidad la arquitectura del monorepo, cómo se comunican sus módulos, la realidad del filesystem vs lo reportado, los gaps reales contra la planeación original (`plugins-mx-research-problemas-no-resueltos.md` + `plugins-mx-planeacion-mcps-agentica.md`) y la recomendación de continuación.

**Audiencia**: stakeholders, contribuyentes, planeación de roadmap, futuras sesiones que retomen contexto.

**Pre-lectura recomendada**: [arquitectura.md](arquitectura.md), [estado-real.md](estado-real.md), [STATUS.md](STATUS.md), [gap-analysis-2026-06.md](gap-analysis-2026-06.md).

**Última actualización**: 2026-06-12

---

## 0. TL;DR

El proyecto creció más de lo que cualquier documento reporta. Realidad medida contra filesystem:

| Métrica | README.md (declarado) | STATUS.md (declarado) | **Filesystem real** |
|---|---|---|---|
| Plugins verticales | 11 | 27 | **35** (core + 34 verticales) |
| MCP servers | 25 | 40 | **40** ✅ |
| Skills (`SKILL.md`) | 120 | 220 | **275** |
| `_shared/` skills base | 6 | 6 | **6** ✅ |
| Specs detallados | — | 15 | **15** + `_template.md` ✅ |
| Hooks runtime CC | — | 14 | **15** + `_lib.sh` |
| Tests MCP (archivos `test_*.py`) | 872 (cuenta agregada) | — | **92 archivos** |
| Evals (`.eval.json`) | 25 | 181 | **181** ✅ |
| Workflows (carpetas físicas con código) | 7 | 23 | **0** (sólo markdown) |
| Webhook receiver | — | V1 | V1 con FastAPI + handlers + validators + idempotency + audit ✅ |

**Tres hallazgos críticos**:

1. **README está congelado en 2026-06-11**. STATUS.md tampoco refleja los 8 verticales nuevos (specs 07-15) ya scaffoldeados. **Antes de cualquier roadmap nuevo, hay que reconciliar la documentación con el filesystem** o las decisiones se toman sobre cifras irreales.

2. **Workflows como markdown ≠ código ejecutable.** Los 23 "workflows" del STATUS son **plantillas declarativas en `docs/`**, no `Workflow.workflow()` ejecutables. Esto es un gap silencioso que ningún reporte captura — y bloquea la operación real de `cierre-fiscal-mensual`, `due-diligence-cliente`, `pf-anual-completa`.

3. **181 evals para 275 skills = ratio 0.66 por skill.** El objetivo del plan (cobertura ≥80% accuracy) requiere 160-385 evals — estás dentro del rango bajo, pero faltan los críticos: `freelance-tax-mx`, `cfdi-colegiaturas-deducibles`, `pf-anual-mx`.

---

## 1. Arquitectura de capas

El monorepo aplica una arquitectura estricta de 6 capas donde **las capas superiores pueden invocar las inferiores, NUNCA al revés** (regla cardinal en `docs/arquitectura.md` y `plugins-mx-planeacion-mcps-agentica.md §1`).

```
┌─────────────────────────────────────────────────────────────────────┐
│  CAPA 6 — Workflows (orquestación multi-agente)                     │
│  Composición de skills + agents para procesos complejos             │
│  Hoy: 23 declarados en markdown / 0 implementados como código       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│  CAPA 5 — Agents (subagents aislados)                               │
│  Tareas costosas/ruidosas/paralelas en contexto separado            │
│  Hoy: 18 plugins con agents/                                        │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│  CAPA 4 — Skills (conocimiento + lógica)                            │
│  Cuerpo SKILL.md + references/ + scripts/                           │
│  Hoy: 275 SKILL.md (6 _shared + 269 verticales)                     │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│  CAPA 3 — Commands + Hooks + Crons (triggers)                       │
│  Disparadores user-initiated (/comando) o automáticos               │
│  Hoy: 37 commands/, 15 hooks runtime + 1 git, 2 crons plist         │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│  CAPA 2 — MCPs (conectores externos)                                │
│  Tier S, A, B — cada uno con auth + cache + bitácora                │
│  Hoy: 40 MCPs (Python+FastMCP) con 92 archivos de tests             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│  CAPA 1 — Servicios externos (APIs, portales web, sandboxes)        │
│  SAT, Banxico, Facturama, ML, MP, Conekta, IMSS, INFONAVIT,         │
│  CFE, Telmex, municipales, marketplaces, exchanges, etc.            │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  CAPA TRANSVERSAL — Persistencia (filesystem)                       │
│  clientes/, cfdi/, cobranza/, fiscal/, cache/, audit-log/           │
└─────────────────────────────────────────────────────────────────────┘
```

### Reglas de dependencia entre capas

- Workflows → invocan agents, skills, MCPs, commands.
- Agents → invocan skills, MCPs.
- Skills → invocan MCPs y scripts locales (no agents directamente).
- Hooks/Crons → disparan workflows o skills, nunca agents directamente.
- Commands → entry points del usuario que invocan skills o workflows.
- MCPs → hojas: sólo hablan con servicios externos.

### Por qué esta separación importa

- **Composabilidad**: cualquier vertical (incluyendo los 8 nuevos como `nomina-pymes-mx` o `crowdfunding-itf-mx`) puede reusar `mp_facturama_extendido` sin acoplarse a freelancers-mx.
- **Testabilidad**: los MCPs corren mock-first sin credenciales, lo que permitió alcanzar 92 archivos de test sin haber timbrado un solo CFDI real en producción.
- **Aislamiento de fallos**: si SAT cambia su portal, sólo `mp_sat_portal` se rompe — los skills que lo consumen siguen siendo válidos en concepto.
- **Auditoría**: cada capa puede loguear independientemente (`audit-log/mp-*/*.jsonl`, hooks `hook-events.jsonl`).

---

## 2. Comunicación entre módulos — flujos reales

### Flujo A: Emisión CFDI tras pago Mercado Pago (workflow disparado por webhook)

```
[Usuario freelancer]
   ↓ /freelancers:cobranza @cliente
[Skill cobranza-seguimiento (_shared/)]
   ↓ invoca
[MCP mp_mercado_pago.create_preference]
   ↓ devuelve init_point URL
[Skill whatsapp-business-mx]
   ↓ envía template "utility_cobranza_link" con init_point
[Cliente paga en Mercado Pago]
   ↓ POST /webhooks/mp con body + x-signature
[webhooks/app/main.py FastAPI]
   ↓ routes/ enruta a handler
[webhooks/app/validators/mp.py]
   ↓ valida HMAC con mp_mercado_pago.validate_webhook
[webhooks/app/idempotency.py]
   ↓ dedupe por (source=mp, event_id) en SQLite
[webhooks/app/handlers/mp.py]
   ↓ dispara workflow "emitir-cfdi-tras-pago" (HOY: markdown — no ejecutable)
[Skill cfdi-emision (_shared/)]
   ↓ invoca para multimoneda
[MCP mp_banxico.get_tc_dof]   ← cache 24h
   ↓ devuelve TC
[Skill cfdi-emision]
   ↓ valida payload localmente (RFC, CP, total = subt + imp − ret)
   ↓ invoca
[MCP mp_facturama_extendido.timbrar_cfdi]
   ↓ devuelve UUID + XML + PDF
[webhooks/app/audit.py]
   ↓ JSONL append-only con hashed event_id
[Skill whatsapp-business-mx]
   ↓ envía CFDI al cliente
```

**Punto de quiebre actual**: el handler de webhook no puede invocar el workflow porque éste vive como markdown. La integración real está pendiente (`webhooks/README.md` sección V2: "Integración real con workflows del monorepo").

### Flujo B: Cierre fiscal mensual (cron-driven, multi-MCP, multi-paralelo)

Declarado en `plugins-mx-planeacion-mcps-agentica.md §7.1`:

```
cron('0 9 14 * *')  // Día 14 del mes 9am
   ↓
[Workflow cierre-fiscal-mensual]  ← HOY: markdown declarativo
   ↓ phase('Recopilación')
parallel([
  agent('CFDIs emitidos del mes', mcp: mp_sat_portal),   ← Playwright stub, no real
  agent('CFDIs recibidos del mes', mcp: mp_sat_portal),
  agent('Estado cuenta bancario', mcp: mp_bancos_mx),    ← Playwright stub, no real
  agent('TCs DOF del mes', mcp: mp_banxico)              ← REAL ✅
])
   ↓ phase('Análisis paralelo')
parallel([
  agent('Cruce ingresos/depósitos'),
  agent('Cruce gastos/retiros'),
  agent('Retenciones no acreditadas'),
  agent('Gastos sin CFDI'),
  agent('Depósitos efectivo > $15k')
])
   ↓ phase('Cálculo')
agent('Pago provisional', skill: freelance-tax-mx)       ← Score 4.4/9 — sin contador
   ↓ phase('Output')
agent('Reporte fiscal/YYYY-MM.md')
agent('Alertas WhatsApp')
agent('Recordatorio día 17')
```

**Puntos de quiebre actuales**:
1. Workflow no ejecutable (markdown).
2. `mp_sat_portal` y `mp_bancos_mx` son Playwright **stub** — falta scraping real.
3. `freelance-tax-mx` no tiene validación de contador → riesgo regulatorio alto.

### Flujo C: Hook PreToolUse pre-timbrado (defensa preventiva)

Disparado por `.claude/settings.json` cuando una skill intenta invocar `mp_facturama_extendido.timbrar_cfdi`:

```
[Skill quiere timbrar]
   ↓ PreToolUse hook
[scripts/hooks/pre-timbrado-validation.sh]
   ↓ lee payload del tool call
   ↓ valida 8 reglas (RFC, CP, fecha ±72h, total, ObjetoImp, Exportacion, etc.)
   ↓ si falla → BLOQUEA (exit code != 0)
   ↓ si pasa → continúa al MCP
[MCP mp_facturama_extendido]
   ↓ timbra
[PostToolUse hook backup-cfdi-automatico.sh]
   ↓ guarda XML+PDF en backup-cfdi/YYYY-MM/
```

**Ventaja clave**: el hook es la última línea de defensa antes de enviar payload incorrecto a Facturama, lo que evitaría rechazo del PAC o peor, un CFDI mal timbrado en producción.

### Flujo D: SessionStart orquestador (carga contexto inicial)

```
[Claude Code arranca sesión]
   ↓ SessionStart hook
[scripts/hooks/contexto-inicial-sesion.sh]
   ↓ invoca sub-hooks paralelamente
[dashboard-cobranza-pendiente.sh]   ← lista facturas vencidas
[alerta-pago-provisional.sh]        ← días restantes hasta día 17 del mes
[cfdi-vencimientos.sh]              ← REPs próximos a vencer
   ↓ emite a stdout como persisted-output si > 16KB
[Hook output llega como system-reminder al modelo]
```

Esto es lo que ves al inicio de cada sesión: el bloque "plugins-mx — contexto inicial" + persisted-output con resumen del estado del proyecto.

### Flujo E: Conciliación SPEI con CEP (multi-step, bitácora)

```
[Skill emite CFDI tipo I PPD]
   ↓ guarda en cfdi/YYYY-MM/UUID.json con status="pendiente_cobro"
[Cliente paga vía SPEI]
   ↓ envía clave_rastreo por WhatsApp
[Skill conciliacion-bancaria]
   ↓ invoca
[MCP mp_banxico_cep.generar_cep]
   ↓ Playwright o form-POST contra Banxico CEP portal
   ↓ devuelve CEP confirmado
[Skill marca status="cobrado" en cfdi/YYYY-MM/UUID.json]
   ↓ dispara
[Workflow emitir-rep]  ← markdown
   ↓ invoca cfdi-emision con TipoComprobante=P
[MCP mp_facturama_extendido.timbrar_con_pagos20]
   ↓ emite CFDI tipo P (REP)
[Audit log]
```

---

## 3. Estado real del filesystem (medido 2026-06-12)

### 3.1 Plugins verticales (35 directorios)

**Originales del README (11)**:
core-mexico, freelancers-mx, agencia-marketing-mx, colegios-mx, talleres-mx, ecommerce-mx, salon-mx, veterinaria-mx, wedding-mx, restaurante-mx, inmobiliaria-mx.

**Nuevos del research scaffoldeados (24)**:
- **TOP del research (score ≥ 8.0)**: `pf-anual-mx`, `arrendador-residencial-mx`, `tramites-vehiculares-mx`, `conductor-plataforma-mx`, `tienda-omnicanal-mx`, `consultorio-especialista-mx`, `clinica-salud-mx`, `airbnb-host-mx`, `notarias-mx`.
- **Tier 2 (score 7.5-7.9)**: `despacho-contable-mx`, `psicoterapia-mx`, `servicios-publicos-mx`, `migracion-extranjeros-mx`, `gmm-asegurado-mx`, `paciente-mx`.
- **Specs 07-15 (áreas no cubiertas del research)**: `telemedicina-mx`, `nomina-pymes-mx`, `cripto-fiscal-mx`, `educacion-particular-b2c-mx`, `donatarias-ongs-mx`, `importadores-mx`, `sucesion-empresa-familiar-mx`, `crowdfunding-itf-mx`, `energia-solar-pyme-mx`.

### 3.2 MCP servers (40 directorios)

**Tier S — Producción crítica (7)**:
`mp_banxico`, `mp_facturama_extendido`, `mp_mercado_pago`, `mp_mercado_libre`, `mp_curp_renapo`, `mp_banxico_cep`, `mp_sat_portal`.

**Tier A — Pasarelas alternativas + escritura (4)**:
`mp_conekta`, `mp_aspel_contpaqi`, `mp_shopify_mx`, `mp_bitso`.

**Tier B — Playwright stub mock-first (9)**:
`mp_bancos_mx`, `mp_imss_patronal`, `mp_infonavit_patronal`, `mp_cdmx_municipal`, `mp_edomex_municipal`, `mp_monterrey_municipal`, `mp_inmuebles24`, `mp_vivanuncios`, `mp_buro_credito_personal`.

**Tier B — REST + parsers (5)**:
`mp_trustly_mx`, `mp_clip_terminal`, `mp_cabify_business`, `mp_amazon_mx_seller`, `mp_softrestaurant`.

**Delivery aggregators (3)**: `mp_rappi_partners`, `mp_didi_food_partners`, `mp_uber_eats_partners`.

**Nuevos no listados en planeación original (12)**: `mp_cfe_facturacion`, `mp_clabe_validador_oficial`, `mp_didi_partners`, `mp_guadalajara_municipal`, `mp_klap` (POS), `mp_kueski` (crédito), `mp_merida_municipal`, `mp_paypal_mx`, `mp_puebla_municipal`, `mp_queretaro_municipal`, `mp_telmex_facturacion`, `mp_tijuana_municipal`.

### 3.3 Skills (275 archivos `SKILL.md`)

- **6 en `_shared/`** (fuente de verdad): `cfdi-emision`, `iva-retenciones-mx`, `rfc-validacion`, `whatsapp-business-mx`, `compliance-lfpdppp`, `mxn-formato`.
- **269 en plugins verticales** distribuidos por dominio.

### 3.4 Specs detallados (15 + template)

Todos con estado `DRAFT` o `IMPLEMENTED`:

| # | Spec | Tipo |
|---|---|---|
| 01 | webhook-receiver | Infraestructura |
| 02 | sat-portal-playwright-real | MCP crítico |
| 03 | bancos-mx-playwright-real | MCP crítico |
| 04 | hooks-runtime-claude-code | Triggers |
| 05 | vertical-pf-anual-mx | Vertical 9.5/10 |
| 06 | vertical-arrendador-residencial-mx | Vertical 9.3/10 |
| 07 | vertical-telemedicina-mx | Área no cubierta |
| 08 | vertical-nomina-pymes-mx | Área no cubierta |
| 09 | vertical-cripto-fiscal-mx | Área no cubierta |
| 10 | vertical-educacion-particular-b2c-mx | Área no cubierta |
| 11 | vertical-donatarias-ongs-mx | Área no cubierta |
| 12 | vertical-importadores-mx | Área no cubierta |
| 13 | vertical-sucesion-empresa-familiar-mx | Área no cubierta |
| 14 | vertical-crowdfunding-itf-mx | Área no cubierta |
| 15 | vertical-energia-solar-pyme-mx | Área no cubierta |

### 3.5 Capa de triggers (Capa 3)

- **15 hooks runtime** en `scripts/hooks/` + `_lib.sh` compartida:
  - PreToolUse (4): `pre-timbrado-validation`, `confirmar-envio-masivo-wa`, `validar-cfdi-payload`, `validar-ficha-cliente`, `bitacora-mcp-calls`.
  - PostToolUse (3): `backup-cfdi-automatico`, `alert-cancelaciones-frecuentes`, `actualizar-tc-banxico`, `sincronizar-shared-post-edit`.
  - SessionStart (4): `contexto-inicial-sesion`, `dashboard-cobranza-pendiente`, `alerta-pago-provisional`, `cfdi-vencimientos`.
  - Stop (1): `cleanup-sesion`.
  - Test (1): `test-all-hooks.sh`.
- **1 hook git**: `scripts/pre-commit.sh` (lint + JSON + tests MCP).
- **2 crons activos**: `refresh-banxico-tcs.sh` (diario L-V 10:00) + `refresh-sat-listas-69.sh` (lunes 09:00). Configurados como launchd plist macOS + `crontab.linux`.
- **37 directorios `commands/`** distribuidos en plugins.

### 3.6 Webhook receiver (FastAPI)

`webhooks/app/`:
- `main.py` — entry point FastAPI.
- `routes/` — endpoints por proveedor.
- `handlers/` — 12 handlers (Stripe, MP, Conekta, Facturama, Meta WhatsApp, GitHub, Calendly, Typeform, ML, Banxico CEP, IMSS, CONDUSEF).
- `validators/` — HMAC + Bearer + IP allowlist.
- `idempotency.py` — SQLite + memoria, dedupe por `(source, event_id)`.
- `audit.py` — JSONL append-only con hashed event_ids.
- `config.py`, `__init__.py`.
- `tests/` — 29/29 pasando.

### 3.7 Workflows (0 ejecutables / 23 declarados en markdown)

**Esto es el gap más invisible del proyecto**. Tanto STATUS.md como gap-analysis dicen "23 workflows construidos" pero `find . -type d -name "workflow-*"` devuelve **cero directorios físicos**. Los workflows existen únicamente como pseudo-código en `docs/specs/`, `docs/flujos-operativos.md` y `plugins-mx-planeacion-mcps-agentica.md §7`.

Para ser ejecutables deberían ser scripts pasados al skill `Workflow` o a `Workflow.workflow()` con la sintaxis:

```js
export const meta = { name: 'cierre-fiscal-mensual', ... }
phase('Recopilación')
const cfdis = await parallel([
  () => agent('Descargar CFDIs emitidos', {mcp: 'mp_sat_portal'}),
  () => agent('Descargar CFDIs recibidos', {mcp: 'mp_sat_portal'}),
  // ...
])
```

Hoy son tablas markdown describiendo lo anterior — útiles para diseño, inútiles para ejecución.

---

## 4. Auditoría honesta de scoring (`docs/estado-real.md`)

Score promedio del monorepo: **4.7/9** según el checklist de 9 puntos para producción-grade.

### Distribución por riesgo regulatorio

| Nivel | Verticales/skills | Acción mínima antes de producción |
|---|---|---|
| **Bajo** | `mxn-formato`, `rfc-validacion`, `copy-mexicano`, `briefing-creativo` | Iterar con dogfooding; partner opcional |
| **Medio** | `cotizacion-mxn`, `propuesta-comercial`, `reporte-mensual`, `comunicacion-padres-wa`, `diagnostico-cotizacion`, `orden-trabajo` | Revisión legal de contratos; dogfooding |
| **Alto** | `cfdi-emision`, `iva-retenciones-mx`, `cobranza-colegiaturas`, `constancias-academicas`, `garantia-servicio` | **Partner del sector obligatorio + validación de fuentes vigentes** |
| **🚨 Muy alto** | `freelance-tax-mx` (4.4/9), `cfdi-colegiaturas-deducibles` (4.0/9) | **Contador certificado + sandbox PAC real + casos de prueba auditados ANTES de cualquier uso** |

### Lo que NO es codificable (capa 3 — humanos externos)

| Bloqueador | Costo aproximado | Bloquea |
|---|---|---|
| Contador certificado vigente RMF 2026 | $3-8k MXN c/u | `freelance-tax-mx`, `pf-anual-mx`, `cfdi-colegiaturas-deducibles`, `cripto-fiscal-mx`, `nomina-pymes-mx` |
| Abogado mercantilista | $5-12k MXN | `propuesta-comercial`, `contrato-arrendamiento-mx`, contratos `wedding-mx` |
| Abogado defensa consumidor (PROFECO) | $5-10k MXN | `talleres-mx garantia-servicio` |
| Abogado educativo | $3-8k MXN | `colegios-mx`, `educacion-particular-b2c-mx` |
| Abogado fiscal cripto | $5-10k MXN | `cripto-fiscal-mx`, `crowdfunding-itf-mx` |
| Templates WhatsApp aprobados por Meta real | gratuito (requiere cuenta Business activa) | TODOS los verticales con WA |
| Partner del sector × 6-8 verticales prioritarios | revenue share 30-40% | Cada vertical TOP del research |

Sin esta capa 3, los skills siguen siendo scaffolding 4.7/9 promedio — no producción-grade.

---

## 5. Gap cuantificado vs los 2 documentos de Downloads

### 5.1 vs `plugins-mx-research-problemas-no-resueltos.md`

El research mapea **65+ verticales/problemas operativos** en MX. Estado:

- **Scaffoldeados**: 35 (incluye Top 20 + áreas no cubiertas specs 07-15).
- **Pendientes**: ~30 (geriatría, laboratorio clínico, nutrición, tutor individual, centros capacitación, mantenimiento hogar, compraventa inmueble personal, IMSS asegurado, INE, becas, universidades privadas, repartidores delivery, agentes inmobiliarios B2B, agricultura/pesca primario, turismo, microdrama, etc.).

**Esfuerzo restante para cubrir todo el universo**: 8,000-12,000h adicionales (sólo scaffolding; sin validación experta).

### 5.2 vs `plugins-mx-planeacion-mcps-agentica.md`

| Componente | Plan | Real | Gap | Esfuerzo |
|---|---|---|---|---|
| MCPs (Tier S+A+B) | 21 base + extras | 40 | -19 ✅ (sobre el plan) | — |
| Playwright real | 10 áreas | 0 (sólo esqueletos SAT + bancos) | 10 | 800-1,500h |
| Workflows ejecutables | 8+ | 0 (sólo markdown) | 8 | 200-300h |
| Hooks runtime | 15+ | 15 ✅ | 0 | — |
| Crons activos | 30+ | 2 + esqueletos | 28 | 50-100h |
| Webhook handlers | 12 | 12 ✅ | 0 | V2 deploy: 80-120h |
| Capa de validación experta | Capa 3 | 0 firmados | TODOS los verticales TOP | $26-64k MXN consultorías |

**Esfuerzo total restante para MVP comercializable**: ~1,000-1,500h dev + $30-65k MXN consultorías + 1 partner por vertical TOP.

---

## 6. Patrones de comunicación que SÍ funcionan bien hoy

1. **Mock-first**: cada MCP corre sin credenciales devolviendo `simulated: true`. Esto permitió alcanzar 92 archivos de test y dogfooding interno sin riesgo.
2. **Cache con TTL por tipo de dato**: TCs Banxico 24h, padrón SAT 90d, listados de monedas 90d, invalidación en operaciones de write.
3. **Bitácora append-only JSONL** con hash de identificadores sensibles (RFC, CURP, email).
4. **Idempotencia en webhooks** vía `(source, event_id)` en SQLite + memoria.
5. **Hooks pre-acción**: `pre-timbrado-validation` previene CFDIs malformados antes de salir a Facturama.
6. **Sincronización `_shared/`**: una sola fuente de verdad para skills compartidos; `sync-shared.sh` propaga antes de cada release.

## 7. Patrones que NO funcionan / generan deuda

1. **Workflows como markdown.** Útiles para diseño, inútiles para ejecución. Resultado: el día que un cron quiera disparar `cierre-fiscal-mensual`, no hay nada que ejecutar.
2. **Documentación de cuentas desincronizada con filesystem.** README quedó congelado, STATUS no captura los plugins nuevos. Las decisiones se toman sobre cifras irreales.
3. **Playwright como "esqueleto" sin scraping real.** `mp_sat_portal` y `mp_bancos_mx` tienen base + drivers + tests pero no extraen datos reales. Bloquea `pf-anual-mx`, `arrendador-residencial-mx`, conciliación bancaria mensual.
4. **Skills críticos sin validación humana.** `freelance-tax-mx` (4.4/9) puede tener tarifa Art. 96 LISR desactualizada → riesgo real de multa al usuario.
5. **Webhook receiver sin deploy producción.** V1 funciona local; sin HTTPS pública no recibe webhooks reales.

---

## 8. Recomendación de continuación (8 semanas próximas)

| Semana | Tarea | Bloqueador / motivo | Esfuerzo |
|---|---|---|---|
| 1 | Reconciliar README + STATUS + gap-analysis con realidad filesystem + commit | Sin esto, todo el resto se planea sobre números erróneos | 2-4h |
| 1-3 | Implementar Playwright real `mp_sat_portal` (selectores + e.firma loader) | Bloquea `pf-anual-mx`, descarga masiva CFDIs, Buzón | 100-200h |
| 2-4 | Conseguir contador certificado para validar `freelance-tax-mx` + `pf-anual-mx` | Bloqueador "calendar-time" — empezar ya, llega antes de marzo 2027 | $3-8k MXN + 4-6h |
| 3-5 | Implementar 2 workflows como código real: `cierre-fiscal-mensual` + `pf-anual-completa` | Sin esto los workflows declarados no se pueden ejecutar | 50-80h |
| 4-6 | Webhook receiver V2 producción (Cloudflare Workers o Railway) + retry queue async | Sin HTTPS pública no llegan webhooks reales | 80-120h |
| 6-8 | Dogfooding `pf-anual-mx` con declaración personal real | Caso ideal antes de temporada anual 2027 | 20-40h |

### Lo que NO recomiendo seguir haciendo

- Scaffoldear más verticales (ya tienes 35 — más del 50% del universo del research).
- Construir MCPs nuevos Tier B sin que un vertical real los consuma.
- Sumar evals genéricos — generar los críticos: `freelance-tax-mx`, `pf-anual-mx`, `cfdi-emision`.
- Más specs para áreas sin scaffold previo (ya hay 15; suficiente runway).

### Métrica de avance honesta

| Métrica | Hoy | 8 semanas | 6 meses |
|---|---|---|---|
| Verticales con score ≥ 7.5/9 | 0 | 1 (`pf-anual-mx` dogfooding propio) | 2-3 (con partners) |
| Playwright real funcionando | 0 áreas | 1 (SAT básico) | 3-4 (SAT + 2 bancos) |
| Workflows ejecutables | 0 | 2 | 4-5 |
| Webhook receiver producción | local | HTTPS público + 5 handlers reales | 12 handlers activos |
| Validaciones expertas firmadas | 0 | 1 (contador) | 3-4 (contador + 2 abogados + 1 partner) |

---

## 9. Conclusión

El proyecto está en un estado **muy avanzado en superficie** (35 plugins, 40 MCPs, 275 skills, 181 evals) pero **inmaduro en profundidad** (0 workflows ejecutables, Playwright en esqueletos, 0 validaciones expertas firmadas, scaffolding promedio 4.7/9).

El bottleneck **no es código** — es:
1. Reconciliar realidad documentada (4h).
2. Convertir scaffolds en producción-grade UNO por vertical (300-400h cada uno + 1 partner).
3. Activar capa 3 (validaciones humanas).

Si las próximas 8 semanas siguen el orden recomendado, al final tendrías:
- 1 vertical real validado (`pf-anual-mx`) con tu propia declaración pasando contador certificado.
- Backend real (Playwright SAT + 2 workflows ejecutables + webhook producción).
- Documentación reconciliada como single source of truth.

Eso es un MVP comercializable antes de la temporada anual marzo-abril 2027, lo que abre la puerta a:
- Primeros clientes piloto pagados ($30-60k MXN implementación + $8-15k/mes retainer).
- Validación de hipótesis comercial del research.
- Tracción real para perseguir resto del Tier 1.

---

## Ver también

- [arquitectura.md](arquitectura.md) — modelo `_shared/` + verticales, criterios producción-grade
- [estado-real.md](estado-real.md) — auditoría honesta de scoring por skill
- [STATUS.md](STATUS.md) — checklist vivo del proyecto
- [gap-analysis-2026-06.md](gap-analysis-2026-06.md) — gap vs planeación original
- [plan-afinacion.md](plan-afinacion.md) — roadmap táctico 36 semanas vertical-por-vertical
- [roadmap.md](roadmap.md) — visión 12 meses
- `/Users/elias/Downloads/plugins-mx-research-problemas-no-resueltos.md` — research original (65+ verticales)
- `/Users/elias/Downloads/plugins-mx-planeacion-mcps-agentica.md` — planeación detallada (21 MCPs + capa agéntica)
