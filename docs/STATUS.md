# STATUS — Estado del proyecto plugins-mx

> **Documento vivo.** Cada sesión que cierre un módulo, sub-módulo o entrega debe actualizar este archivo.
> Última actualización: **2026-06-11**
> Próxima revisión sugerida: al cierre de cada sesión productiva.

---

## Cómo usar este documento

1. **Antes de empezar una sesión**: lee la sección "Próximo item" + el spec correspondiente en `docs/specs/`.
2. **Al cerrar un módulo**: marca el checkbox + agrega fecha + commit hash + 1 línea de aprendizaje.
3. **Al final de sesión**: actualiza "Última actualización" + verifica counters.
4. **Si descubres trabajo nuevo no listado**: agrégalo a la sección correspondiente con `[ ] [NUEVO desc-2026-MM-DD]`.

**Convención de check**:
- `[ ]` pendiente
- `[~]` en progreso (con quién y desde cuándo)
- `[x]` hecho (con fecha + commit hash + nota corta)
- `[!]` bloqueado (con razón)
- `[-]` descartado (con razón)

---

## Resumen de progreso global

| Capa | Hecho | Faltante | % completado |
|---|---|---|---|
| MCP servers | 25 | 6 críticos + 10 secundarios | ~70% |
| Plugins verticales | 11 | 15 TOP del research | ~42% |
| Workflows | 7 | 5-7 | ~58% |
| Hooks | 1 | 13 | ~7% |
| Crons | 2 | 28 | ~7% |
| Webhooks | 0 receiver | 12 handlers | 0% |
| Skills nuevos del research | 0 | 24 | 0% |
| Evals | 25 | 135-360 objetivo | ~7-19% |
| Fixtures | 38 | 50-100 objetivo | ~38-76% |
| Documentación | 24 | +12 | ~67% |
| Áreas no cubiertas | 0/10 | 10 | 0% |

**Esfuerzo restante estimado**: 7,780-10,740 horas.

---

## Próximo item recomendado

`[ ]` **Tier 1 — MVP comercializable (4 meses)**:
- Spec detallado de **webhook receiver** (`docs/specs/01-webhook-receiver.md`)
- Spec detallado de **SAT Playwright real** (`docs/specs/02-sat-portal-playwright-real.md`)
- Spec detallado de **vertical pf-anual-mx** (`docs/specs/05-vertical-pf-anual-mx.md`)

Después de specs: codificar los 3 (en este orden).

---

## 1. MCP servers (25/31+)

### ✅ Construidos (25)

#### Tier S — Producción crítica
- [x] `mp_banxico` — TCs DOF, UMA, INPC, TIIE — 60 tests — 2026-04 — commit `527bacc`
- [x] `mp_facturama_extendido` — Timbrado CFDI — 88 tests — 2026-04
- [x] `mp_mercado_pago` — Pasarela + webhook HMAC — 75 tests — 2026-04
- [x] `mp_mercado_libre` — Marketplace ML — 63 tests — 2026-04
- [x] `mp_curp_renapo` — Validación CURP — 58 tests — 2026-04
- [x] `mp_banxico_cep` — CLABE + CEP SPEI — 53 tests — 2026-04 — commit `527bacc`
- [x] `mp_sat_portal` — Padrón, 69-B, CFDI verifica (mock + HTTP público real) — 61 tests — 2026-06-11 — commit `c69e94f`

#### Tier A — Pasarelas alternativas + escritura
- [x] `mp_conekta` — Pasarela alternativa — 57 tests — 2026-06-11 — commit `c68de8b`
- [x] `mp_aspel_contpaqi` — Contable (parser CSV) — 51 tests — 2026-06-11 — commit `53cbea5`
- [x] `mp_shopify_mx` — Shopify wrapper MX — 33 tests — 2026-06-11 — commit `9c97bd8`
- [x] `mp_bitso` — Cripto-fiat MX — 35 tests — 2026-06-11 — commit `9c97bd8`

#### Tier B — Playwright stub (mock-first)
- [x] `mp_bancos_mx` — Portales bancarios (stub) — 15 tests — 2026-06-11 — commit `5e995ca`
- [x] `mp_imss_patronal` — IDSE (stub) — 18 tests — 2026-06-11 — commit `5e995ca`
- [x] `mp_infonavit_patronal` — Portal patronal (stub) — 11 tests — 2026-06-11 — commit `cdf357b`
- [x] `mp_cdmx_municipal` — CDMX (stub) — 10 tests — 2026-06-11 — commit `cdf357b`
- [x] `mp_edomex_municipal` — EdoMex (stub) — 8 tests — 2026-06-11 — commit `cdf357b`
- [x] `mp_monterrey_municipal` — AMM/NL (stub) — 8 tests — 2026-06-11 — commit `013494a`
- [x] `mp_inmuebles24` — Búsqueda inmuebles (stub) — 11 tests — 2026-06-11 — commit `013494a`
- [x] `mp_vivanuncios` — Multi-categoría (stub) — 9 tests — 2026-06-11 — commit `013494a`
- [x] `mp_buro_credito_personal` — Buró (compliance) — 15 tests — 2026-06-11 — commit `013494a`

#### Tier B — REST + parsers
- [x] `mp_trustly_mx` — Open banking — 13 tests — 2026-06-11 — commit `ef31cda`
- [x] `mp_clip_terminal` — POS Clip — 13 tests — 2026-06-11 — commit `ef31cda`
- [x] `mp_cabify_business` — Movilidad B2B — 13 tests — 2026-06-11 — commit `ef31cda`
- [x] `mp_amazon_mx_seller` — Amazon SP-API (LWA+AWSSig no impl) — 14 tests — 2026-06-11 — commit `ef31cda`
- [x] `mp_softrestaurant` — POS restaurantero (parser CSV) — 21 tests — 2026-06-11 — commit `ef31cda`

**Subtotal**: 872 tests verdes (cero regresiones).

### ❌ Pendientes (6 críticos + 10 secundarios)

#### Tier A Faltantes
- [ ] `mp_rappi_partners` — 80-120h — Aggregator delivery — clonar patrón mp_mercado_libre
- [ ] `mp_didi_food_partners` — 80-120h — clonar patrón
- [ ] `mp_uber_eats_partners` — 80-120h — clonar patrón

#### Playwright real (path completo)
- [ ] `mp_sat_portal` Playwright real — 100-200h — **REQUIERE SPEC** → `docs/specs/02-sat-portal-playwright-real.md`
- [ ] `mp_bancos_mx` Playwright real BBVA — 60-100h — **REQUIERE SPEC** → `docs/specs/03-bancos-mx-playwright-real.md`
- [ ] `mp_bancos_mx` Playwright real Banamex — 60-100h
- [ ] `mp_bancos_mx` Playwright real Santander — 60-100h
- [ ] `mp_bancos_mx` Playwright real Banorte — 60-100h
- [ ] `mp_imss_patronal` Playwright real con e.firma — 100-150h
- [ ] `mp_infonavit_patronal` Playwright real — 60-100h

#### Bonus del research
- [ ] `mp_didi_partners` (movilidad — distinto a DiDi Food)
- [ ] `mp_clabe_validador_oficial` (CNBV reverso CLABE)

---

## 2. Plugins verticales (11/26 del research)

### ✅ Construidos (11)

| Plugin | Skills propios | Comandos | Estado |
|---|---|---|---|
| [x] `core-mexico` | 6 `_shared/` | 6 | Producción base |
| [x] `freelancers-mx` | 5 | 8 | Scaffolding denso |
| [x] `agencia-marketing-mx` | 5 | 4 | Scaffolding |
| [x] `colegios-mx` | 4 | 4 | Scaffolding (riesgo regulatorio alto) |
| [x] `talleres-mx` | 4 | 4 | Scaffolding |
| [x] `ecommerce-mx` | 5 | 5 | Scaffolding — 2026-06-11 |
| [x] `salon-mx` | 5 | 4 | Scaffolding — 2026-06-11 |
| [x] `veterinaria-mx` | 5 | 4 | Scaffolding — 2026-06-11 |
| [x] `wedding-mx` | 5 | 4 | Scaffolding — 2026-06-11 |
| [x] `restaurante-mx` | 5 | 4 | Scaffolding — 2026-06-11 |
| [x] `inmobiliaria-mx` | 5 | 4 | Scaffolding — 2026-06-11 |

### ❌ Pendientes (TOP 15 del research, score >= 7.5)

#### Tier 1 (score >= 9.0) — REQUIEREN SPEC
- [ ] `pf-anual-mx` — score 9.5/10 — 5M declarantes — **REQUIERE SPEC** → `docs/specs/05-vertical-pf-anual-mx.md`
- [ ] `arrendador-residencial-mx` — score 9.3/10 — 2M arrendadores — **REQUIERE SPEC** → `docs/specs/06-vertical-arrendador-residencial-mx.md`
- [ ] `tramites-vehiculares-mx` — score 9.0/10 — 40M vehículos

#### Tier 2 (score 8.0-8.9)
- [ ] `conductor-plataforma-mx` — 8.8/10 — 1M conductores Uber/DiDi
- [ ] `tienda-omnicanal-mx` — 8.5/10 — 500k tiendas (puede ser extensión de ecommerce-mx)
- [ ] `consultorio-especialista-mx` — 8.3/10 — clonar veterinaria-mx pattern
- [ ] `clinica-salud-mx` — 8.3/10
- [ ] `airbnb-host-mx` — 8.2/10
- [ ] `notarias-mx` — 8.0/10

#### Tier 3 (score 7.5-7.9)
- [ ] `despacho-contable-mx` — 7.9/10
- [ ] `psicoterapia-mx` — 7.8/10
- [ ] `servicios-publicos-mx` — 7.8/10 — CFE, agua, predial
- [ ] `migracion-extranjeros-mx` — 7.5/10
- [ ] `gmm-asegurado-mx` — 7.5/10
- [ ] `paciente-mx` — 7.5/10
- [ ] `geriatria-cuidado-mayor-mx` — 7.5/10
- [ ] `laboratorio-clinico-mx` — 7.3/10

---

## 3. Workflows (7/12+)

### ✅ Construidos (7)
- [x] `workflow-cfdi-emision-completa` — 2026-06-11
- [x] `workflow-pago-conciliacion` — 2026-06-11
- [x] `workflow-cobranza-multinivel` — 2026-06-11
- [x] `workflow-cierre-fiscal-mensual` — 2026-06-11
- [x] `workflow-due-diligence-cliente` — 2026-06-11
- [x] `workflow-sync-multicanal` (ecommerce-mx) — 2026-06-11
- [x] `workflow-pf-anual-completa` — 2026-06-11

### ❌ Pendientes
- [ ] `emitir-cfdi-tras-pago` (webhook handler) — 20-40h — Spec 01 lo cubre
- [ ] `monitoreo-diario-vehicular` — 30-50h
- [ ] `respuesta-crisis-cm` — 20-40h
- [ ] `conciliacion-bancaria-mensual` — 40-60h
- [ ] `verificar-conciliacion-5dia` (cron-driven) — 20-30h
- [ ] `dashboard-cartera-semanal` — 15-25h
- [ ] `procesar-wa-pendientes` — 30-50h
- [ ] `pago-provisional-validator` — 15-25h

---

## 4. Hooks (1/14)

### ✅ Construidos (1)
- [x] `pre-commit` (git) — lint + JSON + tests MCP — 2026-06-11 — commit `00c178a`

### ❌ Pendientes — REQUIEREN SPEC GENERAL
→ `docs/specs/04-hooks-runtime-claude-code.md`

#### Hooks Claude Code (runtime)
- [ ] `backup-cfdi-automatico` (PostToolUse)
- [ ] `validar-ficha-cliente` (Write validation)
- [ ] `pre-timbrado-validation` (PreToolUse)
- [ ] `bitacora-mcp-calls` (Post MCP)
- [ ] `alert-cancelaciones-frecuentes` (Post CFDIs)
- [ ] `dashboard-cobranza-pendiente` (SessionStart)
- [ ] `alerta-pago-provisional` (SessionStart)
- [ ] `cfdi-vencimientos` (SessionStart)
- [ ] `actualizar-tc-banxico` (SessionStart)
- [ ] `validar-cfdi-payload` (PreToolUse)
- [ ] `confirmar-envio-masivo-whatsapp` (PreToolUse)
- [ ] `sincronizar-shared-pre-commit` (Stop)
- [ ] `backup-sesion` (Stop)

---

## 5. Crons (2/30+)

### ✅ Construidos (2)
- [x] `refresh-banxico-tcs.sh` — diario L-V 10:00 — 2026-06-11
- [x] `refresh-sat-listas-69.sh` — lunes 09:00 — 2026-06-11

### ❌ Pendientes — patrón establecido, no requieren spec
#### Universales
- [ ] `check-multas-vehiculares` — diario 08:00
- [ ] `cobranza-recurrente` — día 1 mes 09:00
- [ ] `verificar-cobros` — día 5 mes 10:00
- [ ] `pre-cierre-fiscal` — día 14 mes 09:00
- [ ] `alerta-pago-provisional` — día 15 mes 10:00
- [ ] `ultima-alerta-deadline` — día 17 mes 08:00
- [ ] `dashboard-semanal` — lunes 09:00
- [ ] `backup-semanal` — viernes 18:00
- [ ] `check-wa-pendientes` — */30min L-V 9-18

#### Específicos por vertical (~20)
- [ ] (lista detallada en sección 9.2 del plan original)

---

## 6. Webhooks (0/12) — REQUIERE SPEC

→ `docs/specs/01-webhook-receiver.md` (cubre receiver + handlers)

- [ ] Webhook receiver HTTP público (FastAPI/Cloudflare Workers)
- [ ] Handler Stripe `payment_intent.succeeded`
- [ ] Handler Mercado Pago `payment.created`
- [ ] Handler Conekta `charge.paid`
- [ ] Handler Facturama `cfdi.timbrado`
- [ ] Handler Meta WhatsApp `messages`
- [ ] Handler GitHub `push`
- [ ] Handler Calendly `invitee.created`
- [ ] Handler Typeform `form_response`
- [ ] Handler Mercado Libre `orders`
- [ ] Handler Banxico CEP
- [ ] Handler IMSS Buzón

---

## 7. Skills nuevos del research (0/24)

→ Cada uno irá al vertical correspondiente. Patrón clonable, no requieren spec individual.

- [ ] `gestor-efirma-vencimientos` (core-mexico)
- [ ] `validador-auditorias-sat-pendientes` (freelancers-mx)
- [ ] `optimizador-deducciones-personales` (freelancers-mx)
- [ ] `simulador-pre-pagos-hipotecarios` (inmobiliaria-mx)
- [ ] `comparador-subrogaciones-bancarias`
- [ ] `detector-saldos-a-favor-csf` (freelancers-mx)
- [ ] `seguimiento-tramites-migratorios` (migracion-extranjeros-mx)
- [ ] `validador-traduccion-documentos`
- [ ] `comparador-seguros-automotrices` (gmm-asegurado-mx)
- [ ] `detector-consumo-anomalo-cfe-agua` (servicios-publicos-mx)
- [ ] `optimizador-horarios-hoy-no-circula` (tramites-vehiculares-mx)
- [ ] `generador-constancias-curp` (core-mexico)
- [ ] `tracking-medicamentos-vencimiento` (geriatria-mx)
- [ ] `pricing-dinamico-airbnb` (airbnb-host-mx)
- [ ] `calculador-ish-por-estado` (airbnb-host-mx)
- [ ] `reporte-retenciones-no-acreditadas` (freelancers-mx)
- [ ] `detector-captura-duplicada-cfdis` (core-mexico)
- [ ] `complemento-inseduc-cfdi-d10` (colegios-mx — parcial existe)
- [ ] `validador-requisitos-deducibilidad-colegiaturas` (colegios-mx)
- [ ] `gestor-deposito-en-garantia` (inmobiliaria-mx)
- [ ] `comparador-renta-zona-dinamica` (inmobiliaria-mx — parcial existe)
- [ ] `scoring-inquilinos-ia` (inmobiliaria-mx — parcial existe)
- [ ] `optimizador-rutas-conductores` (conductor-plataforma-mx)
- [ ] `calculadora-isr-cripto-detallada` (cripto-fiscal-mx nuevo)

---

## 8. Evals (25/160-385)

- [x] 25 archivos `.eval.json` cubren skills críticos — 2026-06-11

### ❌ Pendientes (~135-360)
Patrón establecido. Acumular según se construyan skills/MCPs nuevos.

---

## 9. Documentación (24/35+)

### ✅ Construida
- [x] `docs/INDEX.md`
- [x] `docs/arquitectura.md`
- [x] `docs/roadmap.md`
- [x] `docs/plan-afinacion.md`
- [x] `docs/estado-real.md`
- [x] `docs/seguridad.md`
- [x] `docs/versionado.md`
- [x] `docs/glosario-fiscal-mx.md`
- [x] `docs/glosario-tecnico.md`
- [x] `docs/compliance-checklist.md`
- [x] `docs/metricas.md`
- [x] `docs/flujos-operativos.md`
- [x] `docs/troubleshooting.md`
- [x] `docs/faq.md`
- [x] `docs/guia-instalacion.md`
- [x] `docs/guia-desarrollo.md`
- [x] `docs/integracion-pac.md`
- [x] `docs/integracion-whatsapp.md`
- [x] `docs/integracion-pagos.md`
- [x] `docs/guia-vertical-freelancers.md`
- [x] `docs/guia-vertical-agencia.md`
- [x] `docs/guia-vertical-colegios.md`
- [x] `docs/guia-vertical-talleres.md`
- [x] `docs/gap-analysis-2026-06.md` — 2026-06-11
- [x] `docs/STATUS.md` (este archivo) — 2026-06-11

### ❌ Pendientes
- [ ] `docs/guia-vertical-ecommerce.md`
- [ ] `docs/guia-vertical-salon.md`
- [ ] `docs/guia-vertical-veterinaria.md`
- [ ] `docs/guia-vertical-wedding.md`
- [ ] `docs/guia-vertical-restaurante.md`
- [ ] `docs/guia-vertical-inmobiliaria.md`
- [ ] `docs/casos-uso-documentados.md` — KPIs y testimonios por vertical
- [ ] `docs/manual-operativo-template.md` — plantilla para usuarios finales
- [ ] `docs/adrs/` — Architecture Decision Records históricos
- [ ] `docs/troubleshooting-mcps.md` — específico por MCP
- [ ] `docs/matriz-vertical-x-mcp.md` — compatibilidad
- [ ] `docs/pricing-implementacion.md` — público

---

## 10. Specs detallados (0/6+) — NUEVO BLOQUE

→ `docs/specs/` directory

- [ ] `docs/specs/_template.md` — plantilla
- [ ] `docs/specs/01-webhook-receiver.md`
- [ ] `docs/specs/02-sat-portal-playwright-real.md`
- [ ] `docs/specs/03-bancos-mx-playwright-real.md`
- [ ] `docs/specs/04-hooks-runtime-claude-code.md`
- [ ] `docs/specs/05-vertical-pf-anual-mx.md`
- [ ] `docs/specs/06-vertical-arrendador-residencial-mx.md`

---

## 11. Áreas no cubiertas (0/10)

Del research, requieren scaffold de plugin nuevo:

- [ ] Gestión pólizas seguros (auto/GMM/vida) — score 7.5
- [ ] Auditoría fiscal automatizada — score 8.0
- [ ] Optimización trámites burocráticos aggregator — score 7.5
- [ ] Telemedicina + recetas digitales — score 7.2 (requiere COFEPRIS)
- [ ] Gestor cripto multi-exchange + fiscal — score 6.8
- [ ] Marketplace B2B servicios — score 7.0 (producto completo)
- [ ] Community management automatizado PyMEs — score 7.3
- [ ] Nómina simplificada ISR/IMSS/INFONAVIT — score 7.4
- [ ] Reporte rentabilidad por cliente/producto — score 7.2
- [ ] Contratos templates por estado — score 7.0

---

## Convenciones para actualizar este archivo

### Al cerrar un módulo
1. Cambiar `[ ]` → `[x]`
2. Agregar fecha cierre + commit hash
3. Si descubriste algo no documentado: agregar bullet con `[NUEVO]`
4. Actualizar counters de "Resumen de progreso global" si aplica
5. Mover el próximo item recomendado si lo concluiste

### Al empezar a trabajar en algo
1. Cambiar `[ ]` → `[~ Elias 2026-06-11]`
2. Si requiere spec y no existe: crear primero el spec en `docs/specs/`

### Al bloquear algo
1. Cambiar `[ ]` o `[~]` → `[! razón corta]`
2. Documentar el bloqueo en `docs/troubleshooting.md` si es técnico

### Cada N sesiones (sugerido: 5)
1. Recalcular counters globales
2. Revisar si el "Próximo item recomendado" sigue siendo correcto
3. Actualizar `docs/gap-analysis-*.md` si hay cambios estructurales

---

## Ver también

- [gap-analysis-2026-06.md](gap-analysis-2026-06.md) — análisis detallado del gap
- [roadmap.md](roadmap.md) — visión a 12 meses
- [plan-afinacion.md](plan-afinacion.md) — táctico por vertical
- [arquitectura.md](arquitectura.md) — modelo general
- `docs/specs/` — specs detallados de items novedosos
