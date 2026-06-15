# Gap analysis — junio 2026 (reconciliado 2026-06-12)

**Propósito**: identificar exactamente qué falta por construir comparando el estado actual del monorepo contra los documentos de planeación original (`plugins-mx-research-problemas-no-resueltos.md` y `plugins-mx-planeacion-mcps-agentica.md`).

**Audiencia**: stakeholders, contribuyentes, planeación de roadmap.

**Pre-lectura**: [analisis-profundo-2026-06.md](analisis-profundo-2026-06.md), [estado-real.md](estado-real.md), [roadmap.md](roadmap.md), [plan-afinacion.md](plan-afinacion.md).

> ⚠ **Reconciliación 2026-06-12**: este documento subestimaba el filesystem real. Datos corregidos contra `find`/`ls` directos. Detalle en [analisis-profundo-2026-06.md §3](analisis-profundo-2026-06.md).

---

## TL;DR (actualizado 2026-06-12)

Tenemos **40 MCPs, 35 plugins, 23 workflows declarados (0 ejecutables), 275 skills, 181 evals, 38 fixtures, 15 specs, 15 hooks runtime + 1 git, webhook receiver V1 + 12 handlers**.

Los planes originales describen un universo de **TOP 20 verticales + 65+ totales del research + 21 MCPs base + 10 áreas Playwright + 8 workflows ejecutables + 15+ hooks + 30+ crons + 12 webhooks**.

**Esfuerzo restante para MVP comercializable (Tier 1)**: 1,000-1,500h dev + $30-65k MXN consultorías (4 meses).

**Esfuerzo total para cubrir todo el universo del research**: 8,000-12,000h adicionales (8-15 meses con equipo 3-4 personas).

**Gaps críticos descubiertos 2026-06-12**:
1. **23 workflows como markdown, 0 ejecutables como código** (conversión: 200-300h).
2. **Playwright real en SAT y bancos = esqueletos**, no scraping real (300-500h conjunto).
3. **0 validaciones expertas firmadas** (bloqueador no-codificable: $26-64k MXN consultorías + partners).

**Lo no-codificable** (capa 3): validación experta con contador, abogado mercantilista, abogado defensa consumidor, abogado educativo, partners del sector. Sin esto los skills críticos no son producción-grade.

---

## 1. MCPs pendientes

### Construidos (40/21+ planeados) ✅ por encima del plan

Tier S (7): banxico, facturama_extendido, mercado_pago, mercado_libre, curp_renapo, banxico_cep, sat_portal.
Tier A (4): conekta, aspel_contpaqi, shopify_mx, bitso.
Tier B Playwright stub (9): bancos_mx, imss_patronal, infonavit_patronal, cdmx/edomex/monterrey/guadalajara/merida/puebla/queretaro/tijuana municipal, inmuebles24, vivanuncios, buro_credito_personal.
Tier B REST + parsers (5): trustly_mx, clip_terminal, cabify_business, amazon_mx_seller, softrestaurant.
Delivery aggregators (3): rappi_partners, didi_food_partners, uber_eats_partners.
Servicios + identidad extras (12): cfe_facturacion, telmex_facturacion, clabe_validador_oficial, paypal_mx, klap, kueski, didi_partners, 5 municipales adicionales.

### Faltantes críticos

| # | MCP | Sección plan | Esfuerzo | Impacto |
|---|---|---|---|---|
| 1 | `mp_rappi_partners` | 4.5 | 80-120h | Alto (restaurante-mx, dark-kitchen) |
| 2 | `mp_didi_food_partners` | 4.6 | 80-120h | Alto (idem) |
| 3 | `mp_uber_eats_partners` | 4.7 | 80-120h | Alto (idem) |
| 4 | `mp_bancos_mx` (Playwright real) | 6.2 | 60-100h × banco × 9 bancos | CRÍTICO conciliación bancaria |
| 5 | `mp_imss_idse` (Playwright real) | 6.8 | 100-150h | Para nómina vertical |
| 6 | `mp_sat_portal` (Playwright real) | 6.1 | 100-200h (sobre el mock actual) | Desbloquea descarga masiva real |

**Total esfuerzo MCPs faltantes**: ~800-1,200 horas.

⚠ Los Playwright reales requieren mantenimiento mensual (~4-8h/portal) ya que los portales cambian.

---

## 2. Verticales pendientes

### Estado actual reconciliado (35 scaffoldeados / ~65 del universo del research)

✅ **TOP del research scaffoldeados (15)**: pf-anual-mx, arrendador-residencial-mx, tramites-vehiculares-mx, conductor-plataforma-mx, tienda-omnicanal-mx, consultorio-especialista-mx, clinica-salud-mx, airbnb-host-mx, notarias-mx, despacho-contable-mx, psicoterapia-mx, servicios-publicos-mx, migracion-extranjeros-mx, gmm-asegurado-mx, paciente-mx.

✅ **Áreas no cubiertas scaffoldeadas (9, specs 07-15)**: telemedicina-mx, nomina-pymes-mx, cripto-fiscal-mx, educacion-particular-b2c-mx, donatarias-ongs-mx, importadores-mx, sucesion-empresa-familiar-mx, crowdfunding-itf-mx, energia-solar-pyme-mx.

✅ **Originales (11)**: core-mexico, freelancers-mx, agencia-marketing-mx, colegios-mx, talleres-mx, ecommerce-mx, salon-mx, veterinaria-mx, wedding-mx, restaurante-mx, inmobiliaria-mx.

### Verticales del research aún SIN scaffold (~10)

| Vertical | Score | Mercado |
|---|---|---|
| `geriatria-cuidado-mayor-mx` | 7.5/10 | ~15M mayores 65+ |
| `laboratorio-clinico-mx` | 7.3/10 | ~50k labs |
| `nutricion-mx` | 7.0/10 | ~30k nutricionistas |
| `tutor-individual-mx` | 7.0/10 | ~200k tutores |
| `centro-capacitacion-mx` | 7.0/10 | ~5k bootcamps |
| `mantenimiento-hogar-mx` | 7.0/10 | universal |
| `compraventa-inmueble-personal-mx` | 7.2/10 | ~700k transacciones/año |
| `repartidores-delivery-mx` | 7.0/10 | ~300k repartidores |
| `agentes-inmobiliarios-b2b-mx` | 7.0/10 | nicho |
| `marketplace-b2b-servicios` | 7.0/10 | producto completo |

**Esfuerzo restante para scaffoldear los ~10 faltantes**: 2,000-4,000h (200-400h/vertical).

### Esfuerzo crítico real: afinación + validación experta

**El bloqueador NO es scaffolding nuevo** — son los 35 existentes que están en 4.7/9 promedio (`estado-real.md`). Llevarlos a producción-grade (≥7.5/9):

- 300-400h dogfooding + iteración por vertical
- 1 partner del sector validando (revenue share o consultoría)
- 1 experto regulado por vertical de riesgo alto (contador, abogado)

**Total para llevar 4 verticales a producción** (sugerido `plan-afinacion.md`): ~1,000-1,600h.

**Total para los 35 scaffoldeados a producción**: ~10,000-14,000h.

---

## 3. Workflows pendientes

### Estado real reconciliado 2026-06-12

**Declarados como markdown**: 23.
**Ejecutables como código (`Workflow.workflow()` / `phase()` / `parallel()`)**: **0**.

⚠ **Este es el gap más invisible del proyecto**. Tanto la versión previa de este documento como STATUS.md decían "7 workflows construidos" — pero `find . -type d -name "workflow-*"` devuelve cero. Los workflows son tablas markdown en `docs/specs/`, `docs/flujos-operativos.md` y el doc de planeación.

### Conversión markdown → código (prioridad)

| Workflow | Estado actual | Esfuerzo |
|---|---|---|
| `cierre-fiscal-mensual` | Markdown ✅ (planeación §7.1) | 30-40h |
| `pf-anual-completa` | Markdown ✅ | 30-40h |
| `cfdi-emision-completa` | Markdown ✅ | 25-35h |
| `due-diligence-cliente-nuevo` | Markdown ✅ (planeación §7.2) | 25-35h |
| `cobranza-multinivel` | Markdown ✅ | 25-35h |
| `pago-conciliacion` | Markdown ✅ | 20-30h |
| `sync-multicanal` (ecommerce) | Markdown ✅ | 25-35h |
| `conciliacion-bancaria-mensual` | Markdown parcial | 40-60h |

**Esfuerzo total conversión**: 200-300h.

### Workflows nuevos faltantes (markdown + código)

| Workflow | Esfuerzo total |
|---|---|
| `emitir-cfdi-tras-pago` (webhook handler) | 20-40h |
| `monitoreo-diario-vehicular` | 30-50h |
| `respuesta-crisis-cm` | 20-40h |
| `verificar-conciliacion-5dia` (cron) | 20-30h |
| `dashboard-cartera-semanal` (cron) | 15-25h |
| `procesar-wa-pendientes` (cron) | 30-50h |
| `pago-provisional-validator` | 15-25h |

**Total esfuerzo workflows**: 350-560 horas.

---

## 4. Hooks (reconciliado 2026-06-12) ✅ 100% V1

### Construidos (15 runtime + 1 git + `_lib.sh`)

**Git (1)**: `scripts/pre-commit.sh`.

**PreToolUse (5)**: `pre-timbrado-validation`, `confirmar-envio-masivo-wa`, `validar-cfdi-payload`, `validar-ficha-cliente`, `bitacora-mcp-calls`.

**PostToolUse (4)**: `backup-cfdi-automatico`, `alert-cancelaciones-frecuentes`, `actualizar-tc-banxico`, `sincronizar-shared-post-edit`.

**SessionStart (4)**: `contexto-inicial-sesion` (orquestador), `dashboard-cobranza-pendiente`, `alerta-pago-provisional`, `cfdi-vencimientos`.

**Stop (1)**: `cleanup-sesion`.

Smoke test: 18/18 invocaciones OK.

### V2 pendiente (opcional)

- Métricas de uso por hook
- Persistencia configurable de `hook-events.jsonl`
- Confirmación interactiva real (requiere integración Claude Code más profunda)

**Esfuerzo V2**: 40-60h.

---

## 5. Crons pendientes

### Construidos (2/30+)

- `refresh-banxico-tcs.sh` (cron #1)
- `refresh-sat-listas-69.sh` (cron #10)

### Planeados sección 9 del doc

**Universales (tabla 9.1)** — 8 faltantes:
- `0 8 * * *` Check multas vehiculares
- `0 9 1 * *` Cobranza recurrente
- `0 10 5 * *` Verificar cobros
- `0 9 14 * *` Pre-cierre fiscal
- `0 10 15 * *` Alerta pago provisional
- `0 8 17 * *` Última alerta deadline
- `0 9 * * 1` Dashboard semanal
- `0 18 * * 5` Backup semanal
- `*/30 9-18 * * 1-5` Check WhatsApp pendientes

**Específicos por vertical (tabla 9.2)** — ~20 crons:
- Por cada vertical: agenda recordatorios, monitor servicios, backup datos, etc.

**Total esfuerzo crons**: 50-100 horas.

---

## 6. Webhooks pendientes

### Estado actual

**0 webhook receivers** desplegados. Solo validación de firma HMAC implementada en `mp_mercado_pago.validate_webhook` y `mp_conekta.conekta_validate_webhook`.

### Planeados sección 10.3 del doc

12 webhook handlers:

1. Stripe `payment_intent.succeeded` → emitir CFDI
2. Mercado Pago `payment.created` → emitir CFDI
3. Facturama `cfdi.timbrado` → notificar cliente
4. Meta WhatsApp `messages` → dispatch múltiple
5. GitHub `push` → re-sync-shared
6. Calendly `invitee.created` → onboarding
7. Typeform `form_response` → onboarding
8. Mercado Libre `orders` → procesar orden
9. IMSS `Buzón` → alertar usuario
10. Banxico `CEP` → marcar cobrada
11. CONDUSEF `queja` → respuesta
12. Conekta `charge.paid` → emitir CFDI

**Total esfuerzo webhooks**: 100-150 horas (incluye deployment del receiver con HTTPS público).

---

## 7. Skills específicos del research no codificados

El research describe ~30 problemas operativos. ~24 NO tienen skill correspondiente todavía:

| # | Skill faltante | Vertical |
|---|---|---|
| 1 | Gestor e.firma vencimientos | core-mexico |
| 2 | Validador auditorías SAT pendientes | core-mexico / freelancers-mx |
| 3 | Optimizador deducciones personales | freelancers-mx |
| 4 | Simulador pre-pagos hipotecarios | inmobiliaria-mx |
| 5 | Comparador subrogaciones bancarias | (nuevo: finanzas-personales-mx) |
| 6 | Detector saldos a favor CSF | freelancers-mx |
| 7 | Seguimiento trámites migratorios | (nuevo: migracion-extranjeros-mx) |
| 8 | Validador traducción documentos | (nuevo) |
| 9 | Comparador seguros automotrices | (nuevo: gmm-asegurado-mx) |
| 10 | Detector consumo anómalo CFE/agua | (nuevo: servicios-publicos-mx) |
| 11 | Optimizador horarios hoy no circula | tramites-vehiculares-mx |
| 12 | Generador constancias CURP | core-mexico |
| 13 | Tracking medicamentos vencimiento | (nuevo: geriatria-mx) |
| 14 | Pricing dinámico Airbnb | (nuevo: airbnb-host-mx) |
| 15 | Calculador ISH por estado | airbnb-host-mx |
| 16 | Reporte retenciones no acreditadas | freelancers-mx |
| 17 | Detector captura duplicada CFDIs | core-mexico |
| 18 | Complemento InsEduc CFDI D10 | colegios-mx (ya existe parcial) |
| 19 | Validador requisitos deducibilidad colegiaturas | colegios-mx |
| 20 | Gestor depósito en garantía | inmobiliaria-mx |
| 21 | Comparador renta/zona dinámica | inmobiliaria-mx (ya existe parcial) |
| 22 | Scoring inquilinos con IA | inmobiliaria-mx (ya existe parcial) |
| 23 | Optimizador rutas conductores | conductor-plataforma-mx (nuevo) |
| 24 | Calculadora ISR cripto detallada | (nuevo: cripto-fiscal-mx) |

**Total esfuerzo skills**: 300-400 horas (12-16h por skill).

---

## 8. Evals y fixtures

### Estado actual

- **25 evals** (de 160-385 estimados para cobertura ≥80%)
- **38 fixtures** (de 50-100 objetivo)

### Gap

- **Evals faltantes**: 135-360 archivos (depende del scope objetivo)
- **Fixtures faltantes**: 12-62 casos

**Total esfuerzo**: 150-250 horas.

---

## 9. Documentación pendiente

### Construida (23 docs)

`arquitectura`, `roadmap`, `plan-afinacion`, `estado-real`, `seguridad`, `versionado`, `glosario-fiscal-mx`, `glosario-tecnico`, `troubleshooting`, `faq`, `compliance-checklist`, `metricas`, `flujos-operativos`, `guia-instalacion`, `guia-desarrollo`, `integracion-pac`, `integracion-whatsapp`, `integracion-pagos`, `guia-vertical-freelancers`, `guia-vertical-agencia`, `guia-vertical-colegios`, `guia-vertical-talleres`, INDEX.

### Planeada pero no escrita

- Guía vertical: `ecommerce`, `salon`, `veterinaria`, `wedding`, `restaurante`, `inmobiliaria` (6 verticales nuevos sin guía)
- Casos de uso documentados con números reales (KPIs por vertical)
- Manual operativo por vertical (para usuarios finales)
- ADRs (Architecture Decision Records) históricos
- Troubleshooting guide específico por MCP
- FAQ por vertical
- Plantillas de contrato comercial para clientes implementación
- Pricing listado público
- Sitio web marketing
- Guía partners de implementación
- Matriz compatibilidad vertical × MCP
- Roadmap público actualizado (este doc + actualización de `roadmap.md`)

**Total esfuerzo docs**: 100-150 horas.

---

## 10. Áreas del research SIN cobertura

10 problemas mencionados en el research que NO tienen ningún skill/MCP/vertical:

| # | Problema | Score | Mercado | Esfuerzo |
|---|---|---|---|---|
| 1 | Gestión pólizas de seguros (auto, GMM, vida) | 7.5/10 | 7M pólizas | 200-300h |
| 2 | Auditoría fiscal automatizada (anomaly detection) | 8.0/10 | nicho | 150-200h |
| 3 | Optimización trámites burocráticos (federal+estatal+municipal aggregator) | 7.5/10 | universal | 250-350h |
| 4 | Telemedicina + recetas digitales | 7.2/10 | 3M usuarios | 200-300h |
| 5 | Gestor de cripto + reporte fiscal (multi-exchange) | 6.8/10 | 4M crypto-users MX | 180-250h |
| 6 | Marketplace B2B servicios | 7.0/10 | universal | 500-800h (producto) |
| 7 | CM automatizado PyMEs (multi-red social) | 7.3/10 | 5M PyMEs | 120-180h |
| 8 | Nómina simplificada con cálculos ISR/IMSS/INFONAVIT | 7.4/10 | 5.5M PyMEs con empleados | 250-400h |
| 9 | Reporte rentabilidad por cliente/producto | 7.2/10 | universal PyME | 80-120h |
| 10 | Contratos templates (arrendamiento, prestación, compraventa) por estado | 7.0/10 | universal | 100-150h |

**Total esfuerzo áreas no cubiertas**: 2,030-3,050 horas.

---

## Resumen ejecutivo del gap (reconciliado 2026-06-12)

| Categoría | Hecho (real) | Planeado | Faltante | Esfuerzo |
|---|---|---|---|---|
| MCPs | **40** | 21+ | path real Playwright SAT + bancos | 300-500h |
| Verticales scaffoldeados | **35** | 20+ TOP + 10 áreas | ~10 del research | 2,000-4,000h scaffolding |
| Verticales en producción-grade | **0** | 4 (plan-afinacion) | 4 con score ≥7.5/9 | 1,000-1,600h + $26-64k MXN |
| Workflows declarados markdown | **23** | 8+ | 0 | ✅ |
| Workflows como código ejecutable | **0** | 8+ | 8 | 200-300h |
| Hooks runtime CC | **15** ✅ | 15+ | V2 opcional | 40-60h |
| Hook git | **1** ✅ | 1 | 0 | — |
| Crons | **2** | 30+ | 28 | 50-100h |
| Webhook receiver | **V1 + 12 handlers** | 12 + receiver | V2 deploy producción + retry queue | 80-120h |
| Skills (SKILL.md) | **275** | ~150 esperados | ~50 del universo del research | 600-1,000h |
| Specs detallados | **15** ✅ | ~10 esperados | 0 | — |
| Evals | **181** | 160-385 | 0-200 (cubre rango bajo) | 100-200h |
| Docs | **25** | ~35 | ~10 (incluye guías por vertical nuevo) | 80-120h |
| Validaciones expertas firmadas | **0** | 4+ verticales | TODOS los críticos | $26-64k MXN + tiempo humano |
| **TOTAL Tier 1 (MVP comercializable 4 meses)** | | | | **~1,000-1,500h + $30-65k MXN** |
| **TOTAL hasta cubrir universo del research** | | | | **~8,000-12,000h adicionales** |

**Equivalente Tier 1**: 4 meses con dedicación part-time + consultorías clave.

**Equivalente total**: 8-15 meses con equipo 3-4 personas.

**Monetario total**: $4M-6M MXN @ $500/h desarrollo + $30-100k MXN consultorías expertas.

---

## Prioridades recomendadas

### Tier 1 — MVP comercializable Q3 2026 (4 meses)

Objetivo: 2-3 verticales en producción real con clientes pagados.

1. **MCPs críticos** que desbloquean lo demás:
   - `mp_sat_portal` Playwright path real (descarga masiva CFDIs reales)
   - `mp_bancos_mx` BBVA + Banamex Playwright real
   - **Esfuerzo**: 200-300h

2. **2 verticales TOP del research**:
   - `pf-anual-mx` (score 9.5/10, 5M usuarios)
   - `arrendador-residencial-mx` (score 9.3/10, 2M usuarios)
   - **Esfuerzo**: 600-1,000h

3. **Webhook receiver + 5 handlers**: Stripe, MP, Conekta, Facturama, Meta WA
   - **Esfuerzo**: 150-200h

4. **Validación experta** de 3 skills críticos:
   - Contador para `freelance-tax-mx`, `pf-anual-completa`, `cfdi-colegiaturas-deducibles`
   - **Costo**: $15-30k MXN consultorías

**Total Tier 1**: ~1,000-1,500h dev + $15-30k MXN. **Resultado**: 2-3 verticales con clientes piloto pagados.

### Tier 2 — Expansión Q4 2026 (3 meses)

5. **MCPs Tier A faltantes**: Rappi, DiDi Food, UberEats
6. **3 verticales más**: `tramites-vehiculares-mx`, `tienda-omnicanal-mx`, `consultorio-especialista-mx`
7. **Hooks + crons completos** (15 hooks + 28 crons)

**Esfuerzo Tier 2**: ~1,500-2,000h.

### Tier 3 — Plataforma completa 2027

8. Resto de verticales (10+)
9. Webhook receiver con todos los handlers
10. Evals + fixtures completos
11. Documentación pública + sitio web

---

## Notas finales

**Lo que NO es codificable** (capa 3 — humanos externos):

- Validación fiscal con contador certificado (~$3-8k MXN por vertical)
- Revisión legal contratos por abogado mercantilista (~$5-12k MXN)
- Aprobación templates WhatsApp por Meta real
- Partners del sector (vet, salonero, dueño taller, directora colegio) para feedback
- Casos de éxito documentados con clientes reales (mínimo 6 meses operando)

Sin esta capa 3, los skills siguen siendo **scaffolding 4.7/9 promedio** — no producción-grade.

---

## Ver también

- [estado-real.md](estado-real.md) — auditoría honesta de scoring por skill
- [plan-afinacion.md](plan-afinacion.md) — roadmap táctico 36 semanas
- [roadmap.md](roadmap.md) — visión 12 meses
- `/Users/elias/Downloads/plugins-mx-research-problemas-no-resueltos.md` — research original
- `/Users/elias/Downloads/plugins-mx-planeacion-mcps-agentica.md` — planeación detallada
