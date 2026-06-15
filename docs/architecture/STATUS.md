# STATUS — Estado del proyecto plugins-mx

> **Documento vivo.** Cada sesión que cierre un módulo, sub-módulo o entrega debe actualizar este archivo.
> Última actualización: **2026-06-15** (post-Sprint D — servicios públicos + fiscal vehicular)
> Próxima revisión sugerida: al cierre de cada sesión productiva.

> ⚠ **Nota 2026-06-12**: este documento estaba subestimando el filesystem real. Reconciliación completa hecha. Detalle de los hallazgos en [analisis-profundo-2026-06.md](analisis-profundo-2026-06.md).
>
> 🆕 **Nota 2026-06-15**: Sprint A/B/C/D ejecutado completo. 9 MCPs nuevos/extendidos (servicios públicos + fiscal vehicular). 114 tests nuevos. **62 MCPs totales**. Calibración SAF CDMX en vivo desbloquea 3 MCPs con 1 endpoint. Detalles en [SPRINT-D-RESUMEN-2026-06-15.md](SPRINT-D-RESUMEN-2026-06-15.md) y [discovery-portales-2026-06-15.md](discovery-portales-2026-06-15.md).

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

## Resumen de progreso global (post Sprint D — 2026-06-15)

### Sprint A/B/C/D (2026-06-14 → 2026-06-15)

| Bloque | Estado | Commit | Tests |
|---|---|---|---|
| Sprint A1 `mp_agua_mx` | ✅ Catálogo 17 organismos + SIAPA real | `8c676b0` | 24 |
| Sprint A2 `mp_cfe_facturacion` REAL | ✅ Playwright + human-in-loop + cookies | `8c676b0` | 17 |
| Sprint A3 `mp_tenencia_mx` | ✅ 20 estados + factor depreciación | `8c676b0` | 16 |
| Sprint B4 `scripts/discovery_predial_mensual.py` | ✅ Smoke OK | `e343068` | — |
| Sprint B5 `mp_catastro_estatal_mx` | ✅ 10 sistemas + patrón nacional confirmado | `e343068` | 6 |
| Sprint B6 `mp_ish_mx` | ✅ 32 estados | `e343068` | 10 |
| Sprint C7 `mp_verificacion_vehicular_mx` | ✅ 7 estados + SAF CDMX real | `8941abc` | 15 |
| Sprint C8 `mp_gas_natural_mx` | ✅ 5 distribuidores (mock-first) | `8941abc` | 4 |
| Sprint C9 `mp_telmex_facturacion` REAL | ✅ pago_sin_login Enterprise v3 | `8941abc` | 11 |
| Sprint D1 Predial top-7 muns (+8.6M hab) | ✅ | `00420f4` | 9 |
| Sprint D2 Agua +5 organismos (+2.25M usuarios) | ✅ | `564c576` | 7 |
| Sprint D3 Catastro +5 estados (patrón nacional) | ✅ | `2a51c80` | 7 |
| Sprint D4 `mp_multas_vehiculares_mx` (NUEVO) | ✅ ~22M vehículos | `93f2810` | 11 |
| 🎯 Calibración SAF CDMX en vivo | ✅ 3 MCPs reusan 1 endpoint | `41196eb` | (incluido en 15) |
| **TOTAL Sprint A/B/C/D** | ✅ | 9 MCPs nuevos/extendidos | **114** |

### Métricas globales reconciliadas 2026-06-15

| Capa | Hecho (filesystem real) | Faltante | % completado | Notas |
|---|---|---|---|---|
| **MCP servers** | **62** | path real bancos + IMSS + SAT post-login | ~95% scaffolding / ~50% Playwright real | 1,380 tests pasando |
| **Plugins verticales** | **35** (core + 34) | ~30 del research (geriatría, lab clínico, nutrición, tutor, etc.) | ~54% universo del research | Scaffolding promedio 4.7/9 |
| **Workflows declarados markdown** | **23** | conversión a código ejecutable | ~100% declarados | ⚠ |
| **Workflows como código ejecutable** | **0** | 8 prioritarios | **0%** | ⚠ Gap silencioso descubierto 2026-06-12 |
| **Hooks runtime CC** | **15** + `_lib.sh` | V2 (métricas, persistencia) | 100% V1 ✅ | PreToolUse 5 + PostToolUse 4 + SessionStart 4 + Stop 1 + test |
| **Hook git** | **1** (pre-commit) | 0 | 100% ✅ | |
| **Crons activos** | **2** (Banxico TCs + SAT listas) | ~28 del plan (cobranza, pre-cierre, etc.) | ~7% | |
| **Webhook receiver** | **V1 local + 12 handlers** | V2 producción + retry queue | ~75% | 29/29 tests pasando |
| **Skills (`SKILL.md`)** | **275** (6 `_shared/` + 269) | críticos sin partner (~50) | ~85% lint / ~52% producción | |
| **Specs detallados** | **15** + `_template.md` | 0 (cobertura completa) | 100% ✅ | 6 infra + 9 verticales |
| **Evals (`.eval.json`)** | **181** | críticos (`freelance-tax-mx`, `cfdi-colegiaturas-deducibles`, `pf-anual-mx`) | **66% del ratio objetivo** (160-385) | Ratio 0.66/skill, objetivo 0.8 |
| **Fixtures** | 38 | 50-100 objetivo | ~38-76% | |
| **Tests Python (archivos)** | **92** | de specs no implementados | ~70% | |
| **Documentación (docs/)** | **25** docs | actualización continua | ~80% | Incluye análisis profundo 2026-06-12 |
| **Validaciones expertas firmadas** | **0** | contador, abogado mercantil, abogado defensa consumidor, abogado educativo | **0%** | Bloqueador no-codificable |

**Esfuerzo restante hasta MVP comercializable (Tier 1)**: 1,000-1,500h dev + $30-65k MXN consultorías + 1 partner por vertical TOP.

**Esfuerzo total hasta cubrir universo del research**: 8,000-12,000h adicionales.

---

## Próximo item recomendado (8 semanas — 2026-06-12)

Plan reconciliado tras descubrir gaps invisibles (workflows-markdown, validaciones expertas faltantes). Ver [analisis-profundo-2026-06.md](analisis-profundo-2026-06.md) §8.

| Sem | Tarea | Bloqueador / motivo | Esfuerzo |
|---|---|---|---|
| 1 | `[~]` Reconciliar README + STATUS + gap-analysis con filesystem real + commit | Sin esto las decisiones se toman sobre cifras erróneas | 2-4h |
| 1-3 | `[ ]` Implementar Playwright real `mp_sat_portal` (selectores + e.firma loader) | Bloquea `pf-anual-mx`, descarga masiva CFDIs, Buzón Tributario | 100-200h |
| 2-4 | `[ ]` Conseguir contador certificado para validar `freelance-tax-mx` + `pf-anual-mx` | "Calendar-time" — arrancar ya antes de marzo 2027 | $3-8k MXN + 4-6h |
| 3-5 | `[ ]` Implementar 2 workflows como código real: `cierre-fiscal-mensual` + `pf-anual-completa` | Sin esto los workflows declarados no se pueden ejecutar | 50-80h |
| 4-6 | `[ ]` Webhook receiver V2 producción (Cloudflare Workers o Railway) + retry queue async | Sin HTTPS pública no llegan webhooks reales | 80-120h |
| 6-8 | `[ ]` Dogfooding `pf-anual-mx` con declaración personal real | Caso ideal antes de temporada anual 2027 | 20-40h |

### Lo que NO recomiendo seguir haciendo
- Scaffoldear más verticales (ya hay 35 — más del 50% del universo).
- Construir MCPs nuevos Tier B sin que un vertical real los consuma.
- Sumar evals genéricos — generar los críticos faltantes.

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
- [~] `mp_sat_portal` Playwright real — **ESQUELETO CODIFICADO 2026-06-12**: `efirma_loader.py` + `playwright_client.py` + 20 tests; falta scraping selectores reales (humano). Setup: `mcp-servers/mp_sat_portal/SETUP_PLAYWRIGHT_REAL.md`
- [~] `mp_bancos_mx` Playwright real 4 bancos — **ESQUELETO CODIFICADO 2026-06-12**: base class + 4 drivers (BBVA, Banamex, Santander, Banorte) + schema `Movimiento` + helper TOTP Banorte + 12 tests; falta `_real_login()` y scraping (humano). Setup: `mcp-servers/mp_bancos_mx/SETUP_PLAYWRIGHT_REAL.md`
- [ ] `mp_imss_patronal` Playwright real con e.firma — 100-150h
- [ ] `mp_infonavit_patronal` Playwright real — 60-100h

#### Bonus del research
- [ ] `mp_didi_partners` (movilidad — distinto a DiDi Food)
- [ ] `mp_clabe_validador_oficial` (CNBV reverso CLABE)

---

## 2. Plugins verticales (35 scaffoldeados — reconciliado 2026-06-12)

### ✅ Scaffoldeados — Originales (11)

| Plugin | Estado |
|---|---|
| [x] `core-mexico` | Producción base |
| [x] `freelancers-mx` | Scaffolding denso |
| [x] `agencia-marketing-mx` | Scaffolding |
| [x] `colegios-mx` | Scaffolding (riesgo regulatorio alto) |
| [x] `talleres-mx` | Scaffolding |
| [x] `ecommerce-mx` | Scaffolding |
| [x] `salon-mx` | Scaffolding |
| [x] `veterinaria-mx` | Scaffolding |
| [x] `wedding-mx` | Scaffolding |
| [x] `restaurante-mx` | Scaffolding |
| [x] `inmobiliaria-mx` | Scaffolding |

### ✅ Scaffoldeados — TOP del research (15)

| Plugin | Score | Estado afinación |
|---|---|---|
| [x] `pf-anual-mx` | 9.5/10 | Scaffold + spec 05 — pendiente: backend Playwright SAT + contador (humano) |
| [x] `arrendador-residencial-mx` | 9.3/10 | Scaffold + spec 06 — pendiente: validación legal CDMX (humano) |
| [x] `tramites-vehiculares-mx` | 9.0/10 | Scaffold |
| [x] `conductor-plataforma-mx` | 8.8/10 | Scaffold + agents |
| [x] `tienda-omnicanal-mx` | 8.5/10 | Scaffold |
| [x] `consultorio-especialista-mx` | 8.3/10 | Scaffold |
| [x] `clinica-salud-mx` | 8.3/10 | Scaffold |
| [x] `airbnb-host-mx` | 8.2/10 | Scaffold (sin agents — débil) |
| [x] `notarias-mx` | 8.0/10 | Scaffold |
| [x] `despacho-contable-mx` | 7.9/10 | Scaffold |
| [x] `psicoterapia-mx` | 7.8/10 | Scaffold |
| [x] `servicios-publicos-mx` | 7.8/10 | Scaffold (CFE, agua, predial) |
| [x] `migracion-extranjeros-mx` | 7.5/10 | Scaffold |
| [x] `gmm-asegurado-mx` | 7.5/10 | Scaffold |
| [x] `paciente-mx` | 7.5/10 | Scaffold |

### ✅ Scaffoldeados — Áreas no cubiertas (specs 07-15) (9)

| Plugin | Spec | Tema |
|---|---|---|
| [x] `telemedicina-mx` | 07 | COFEPRIS + NOM-004 |
| [x] `nomina-pymes-mx` | 08 | CFDI Nómina 4.0 + IMSS-SUA-IDSE |
| [x] `cripto-fiscal-mx` | 09 | Cripto + CARF 2026 |
| [x] `educacion-particular-b2c-mx` | 10 | Cursos online + CFDI D10/G03 |
| [x] `donatarias-ongs-mx` | 11 | Donatarias autorizadas + transparencia |
| [x] `importadores-mx` | 12 | Pedimentos + IVA + IMMEX |
| [x] `sucesion-empresa-familiar-mx` | 13 | Sucesión + donaciones + protocolo familiar |
| [x] `crowdfunding-itf-mx` | 14 | Ley Fintech + IFC + P2P |
| [x] `energia-solar-pyme-mx` | 15 | CFE bidireccional + net metering + GDMTH |

### ❌ Pendientes — del research, NO scaffoldeados

| Vertical | Score | Mercado MX |
|---|---|---|
| [ ] `geriatria-cuidado-mayor-mx` | 7.5/10 | ~15M mayores 65+ |
| [ ] `laboratorio-clinico-mx` | 7.3/10 | ~50k labs |
| [ ] `nutricion-mx` | 7.0/10 | ~30k nutricionistas |
| [ ] `tutor-individual-mx` | 7.0/10 | ~200k tutores |
| [ ] `centro-capacitacion-mx` | 7.0/10 | ~5k bootcamps |
| [ ] `mantenimiento-hogar-mx` | 7.0/10 | universal |
| [ ] `compraventa-inmueble-mx` | 7.2/10 | ~700k transacciones/año |
| [ ] Otros (repartidores delivery, IMSS asegurado, INE, universidades, agentes inmobiliarios B2B, etc.) | 6.0-7.5 | varios |

**Score honesto vs producción**: ningún vertical scaffoldeado pasa de 4.7/9 promedio sin validación experta. Ver [estado-real.md](estado-real.md).

---

## 3. Workflows (23 declarados markdown / 0 ejecutables como código)

⚠ **Gap silencioso descubierto 2026-06-12**: los workflows existen como **plantillas markdown declarativas**, no como scripts ejecutables del skill `Workflow` con `phase()` / `parallel()` / `pipeline()`. Ningún cron puede dispararlos hoy.

### Declarados como markdown (23)

- [~] `workflow-cfdi-emision-completa` — markdown, falta código
- [~] `workflow-pago-conciliacion` — markdown
- [~] `workflow-cobranza-multinivel` — markdown
- [~] `workflow-cierre-fiscal-mensual` — markdown
- [~] `workflow-due-diligence-cliente` — markdown
- [~] `workflow-sync-multicanal` (ecommerce-mx) — markdown
- [~] `workflow-pf-anual-completa` — markdown
- [~] +16 más (cobranza-renta, telemedicina-consulta, donativo-anual, importacion-pedimento, sucesion-protocolo, crowdfunding-aporte, solar-conexion-cfe, etc.)

### ❌ Pendientes — código real

Prioritarios para 8 semanas próximas:
- [ ] `cierre-fiscal-mensual` como código Workflow — 30-40h
- [ ] `pf-anual-completa` como código Workflow — 30-40h

Resto del plan:
- [ ] `emitir-cfdi-tras-pago` (webhook handler) — 20-40h
- [ ] `monitoreo-diario-vehicular` — 30-50h
- [ ] `respuesta-crisis-cm` — 20-40h
- [ ] `conciliacion-bancaria-mensual` — 40-60h
- [ ] `verificar-conciliacion-5dia` (cron-driven) — 20-30h
- [ ] `dashboard-cartera-semanal` — 15-25h
- [ ] `procesar-wa-pendientes` — 30-50h
- [ ] `pago-provisional-validator` — 15-25h

**Esfuerzo conversión total**: ~200-300h.

---

## 4. Hooks (14/14) ✅

→ Spec: `docs/specs/04-hooks-runtime-claude-code.md`
→ Código: `scripts/hooks/` + `.claude/settings.json`
→ Smoke test: 18/18 invocaciones OK

### ✅ Construidos
- [x] `pre-commit` (git) — lint + JSON + tests MCP — 2026-06-11 — commit `00c178a`
- [x] `pre-timbrado-validation` (PreToolUse, bloquea) — 2026-06-12
- [x] `confirmar-envio-masivo-wa` (PreToolUse, warn) — 2026-06-12
- [x] `validar-cfdi-payload` (PreToolUse, bloquea si JSON roto) — 2026-06-12
- [x] `validar-ficha-cliente` (PreToolUse Write/Edit, warn) — 2026-06-12
- [x] `bitacora-mcp-calls` (PreToolUse mp_*, log) — 2026-06-12
- [x] `backup-cfdi-automatico` (PostToolUse timbrado) — 2026-06-12
- [x] `alert-cancelaciones-frecuentes` (PostToolUse cancelación) — 2026-06-12
- [x] `actualizar-tc-banxico` (PostToolUse banxico) — 2026-06-12
- [x] `sincronizar-shared-post-edit` (PostToolUse Edit/Write) — 2026-06-12
- [x] `contexto-inicial-sesion` (SessionStart orquestador) — 2026-06-12
- [x] `dashboard-cobranza-pendiente` (SessionStart sub-hook) — 2026-06-12
- [x] `alerta-pago-provisional` (SessionStart sub-hook) — 2026-06-12
- [x] `cfdi-vencimientos` (SessionStart sub-hook) — 2026-06-12
- [x] `cleanup-sesion` (Stop) — 2026-06-12

### V2 pendiente
- [ ] Métricas de uso por hook (cuántas veces dispara cada uno)
- [ ] Persistencia configurable de hook-events.jsonl
- [ ] Confirmación interactiva real (requiere integración Claude Code más profunda)

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

## 6. Webhooks (12/12 handlers + receiver) — V1 ✅

→ Spec: `docs/specs/01-webhook-receiver.md`
→ Código: `webhooks/`
→ Tests: 29/29 passing

- [x] Webhook receiver HTTP (FastAPI) — `2026-06-11` MVP completo
- [x] Handler Stripe (payment_intent.succeeded, charge.refunded, invoice.payment_succeeded)
- [x] Handler Mercado Pago (payment, merchant_order, subscription)
- [x] Handler Conekta (charge.paid, charge.refunded, order.paid, subscription.*)
- [x] Handler Facturama (cfdi.stamped, cfdi.cancelled)
- [x] Handler Meta WhatsApp (messages, message_template_status_update)
- [x] Handler GitHub (push con detección _shared/, pull_request)
- [x] Handler Calendly (invitee.created/canceled)
- [x] Handler Typeform (form_response)
- [x] Handler Mercado Libre (orders_v2, payments, questions, items)
- [x] Handler Banxico CEP (manual trigger)
- [x] Handler IMSS Buzón (manual trigger)
- [x] Handler CONDUSEF (manual trigger)
- [x] Validadores HMAC: Stripe, MP, Conekta, GitHub, Meta WhatsApp
- [x] Validadores genéricos: Bearer, IP allowlist
- [x] Idempotencia (memory + SQLite, deduplicación por source+event_id)
- [x] Audit log JSONL append-only con hashed event_ids
- [x] Endpoint admin `/webhooks/recent` con API key

### V2 pendiente (V1 commiteado)
- [ ] Retry queue async (handlers actuales son síncronos best-effort)
- [ ] Deployment Cloudflare Workers / Railway / Fly.io
- [ ] Integración real con workflows del monorepo (cola/MCP/CLI)
- [ ] Firma HMAC oficial Calendly + Typeform (actualmente Bearer)
- [ ] Rate limiting + dead letter queue

### Humano requerido para activar producción
Ver `webhooks/README.md` sección "Pasos que requieren intervención humana":
1. Obtener webhook secrets de cada panel (Stripe, MP, Conekta, etc.)
2. Configurar URL HTTPS pública (Cloudflare Workers / Railway / VPS)
3. Registrar URL en cada panel + suscribir eventos
4. Setear env vars en producción
5. Decidir mecanismo de integración con workflows (V2)

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

## 8. Evals (181/160-385)

- [x] 181 archivos `.eval.json` — **ratio 0.66 evals/skill** (objetivo 0.8 = 220+)

### ❌ Críticos faltantes (alta prioridad)

| Skill | Riesgo | Por qué crítico |
|---|---|---|
| [ ] `freelance-tax-mx` | 🚨 Muy alto | Cálculo ISR PFAE/RESICO — error → multa SAT al usuario |
| [ ] `cfdi-colegiaturas-deducibles` | Alto | Topes Art. 151 LISR — datos pueden estar desactualizados |
| [ ] `pf-anual-completa` (workflow) | 🚨 Muy alto | Declaración anual |
| [ ] `cfdi-emision` | Alto | CFDI 4.0 obligatorio — error → CFDI rechazado por SAT |

### ❌ Resto (~30-200 según scope)
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

## 11. Áreas no cubiertas — scaffoldeadas via specs 07-15 (9/9 ✅)

Reconciliado 2026-06-12: todas las áreas no cubiertas YA están scaffoldeadas. Falta afinación + validación experta.

- [x] `telemedicina-mx` — spec 07 (COFEPRIS + NOM-004)
- [x] `nomina-pymes-mx` — spec 08 (CFDI Nómina 4.0 + IMSS-SUA-IDSE)
- [x] `cripto-fiscal-mx` — spec 09 (cripto + CARF 2026)
- [x] `educacion-particular-b2c-mx` — spec 10 (cursos online)
- [x] `donatarias-ongs-mx` — spec 11 (donatarias autorizadas)
- [x] `importadores-mx` — spec 12 (pedimentos + IMMEX)
- [x] `sucesion-empresa-familiar-mx` — spec 13 (protocolo familiar)
- [x] `crowdfunding-itf-mx` — spec 14 (Ley Fintech)
- [x] `energia-solar-pyme-mx` — spec 15 (CFE bidireccional + GDMTH)

### Áreas restantes del research aún SIN scaffold

- [ ] Geriatría + cuidado adultos mayores — score 7.5
- [ ] Laboratorio clínico — score 7.3
- [ ] Nutrición privada — score 7.0
- [ ] Tutor individual — score 7.0
- [ ] Centros capacitación — score 7.0
- [ ] Mantenimiento hogar — score 7.0
- [ ] Compraventa inmueble personal — score 7.2
- [ ] Marketplace B2B servicios — score 7.0 (producto completo)
- [ ] Repartidores delivery — score 7.0
- [ ] Agentes inmobiliarios B2B — score 7.0

---

## Convenciones para actualizar este archivo

### Al cerrar un módulo
1. Cambiar `[ ]` → `[x]`
2. Agregar fecha cierre + commit hash
3. Si descubriste algo no documentado: agregar bullet con `[NUEVO]`
4. Actualizar counters de "Resumen de progreso global" si aplica
5. Mover el próximo item recomendado si lo concluiste

### Al empezar a trabajar en algo
1. Cambiar `[ ]` → `[~ Elías 2026-06-11]`
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
