# Gap analysis — junio 2026

**Propósito**: identificar exactamente qué falta por construir comparando el estado actual del monorepo contra los documentos de planeación original (`plugins-mx-research-problemas-no-resueltos.md` y `plugins-mx-planeacion-mcps-agentica.md`).

**Audiencia**: stakeholders, contribuyentes, planeación de roadmap.

**Pre-lectura**: [estado-real.md](estado-real.md), [roadmap.md](roadmap.md), [plan-afinacion.md](plan-afinacion.md).

---

## TL;DR

Tenemos **25 MCPs, 11 plugins, 7 workflows, 120 skills, 25 evals, 38 fixtures**. Los planes originales describen un universo de **TOP 20 verticales + 30+ skills específicos del research + 12 webhooks + 15+ hooks + 30+ crons**.

**Esfuerzo restante estimado**: 6,250-8,600 horas (8-11 meses con equipo 3-4 personas, o $3.1M-4.3M MXN @ $500/h).

**Lo no-codificable** (capa 3): validación experta con contador, abogado mercantilista, abogado defensa consumidor, abogado educativo, partners del sector. Sin esto los skills críticos no son producción-grade.

---

## 1. MCPs pendientes

### Construidos (25/21+ planeados)

Por encima del plan original (incluye bonus: `mp_clip_terminal`, `mp_trustly_mx`, `mp_cabify_business`, `mp_vivanuncios`).

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

### Estado actual (11/20 TOP del research)

✅ Hechos: core-mexico, freelancers-mx, agencia-marketing-mx, colegios-mx, talleres-mx, ecommerce-mx, salon-mx, veterinaria-mx, wedding-mx, restaurante-mx, inmobiliaria-mx.

### TOP 20 del research que NO existen

| # | Vertical | Score | Mercado MX |
|---|---|---|---|
| 1 | `pf-anual-mx` | 9.5/10 | ~5M declarantes anuales |
| 2 | `arrendador-residencial-mx` | 9.3/10 | ~2M arrendadores |
| 3 | `tramites-vehiculares-mx` | 9.0/10 | ~40M vehículos |
| 4 | `conductor-plataforma-mx` | 8.8/10 | ~1M conductores Uber/DiDi |
| 5 | `tienda-omnicanal-mx` | 8.5/10 | ~500k tiendas |
| 6 | `consultorio-especialista-mx` | 8.3/10 | ~300k consultorios |
| 7 | `airbnb-host-mx` | 8.2/10 | ~50k hosts |
| 8 | `notarias-mx` | 8.0/10 | ~3,500 notarías |
| 9 | `servicios-publicos-mx` | 7.8/10 | ~30M cuentas CFE+agua |
| 10 | `despacho-contable-mx` | 7.9/10 | ~50k despachos |
| 11 | `psicoterapia-mx` | 7.8/10 | ~50k terapeutas |
| 12 | `migracion-extranjeros-mx` | 7.5/10 | ~1.5M migrantes |
| 13 | `gmm-asegurado-mx` | 7.5/10 | ~10M asegurados |
| 14 | `paciente-mx` | 7.5/10 | (todos) |
| 15 | `geriatria-cuidado-mayor-mx` | 7.5/10 | ~15M mayores 65+ |
| 16 | `laboratorio-clinico-mx` | 7.3/10 | ~50k labs |
| 17 | `nutricion-mx` | 7.0/10 | ~30k nutricionistas |
| 18 | `centro-capacitacion-mx` | 7.0/10 | ~5k bootcamps |
| 19 | `tutor-individual-mx` | 7.0/10 | ~200k tutores |
| 20 | `clinica-salud-mx` | 8.3/10 | ~20k clínicas (incluye PME) |

**Esfuerzo por vertical**: 200-400h (scaffolding) + 100-200h (afinación con partner del sector) = 300-600h cada uno.

**Total esfuerzo verticales TOP 20 faltantes (15)**: 4,000-5,000 horas (~10-15 meses con un dev full-time).

---

## 3. Workflows pendientes

### Construidos (7/8+)

`cfdi-emision-completa`, `pago-conciliacion`, `cobranza-multinivel`, `cierre-fiscal-mensual`, `sync-multicanal`, `due-diligence-cliente`, `pf-anual-completa`.

### Faltantes

| Workflow | Spec | Esfuerzo |
|---|---|---|
| `emitir-cfdi-tras-pago` (webhook handler) | Sección 8.1 | 20-40h |
| `monitoreo-diario-vehicular` | 7.6 | 30-50h |
| `respuesta-crisis-cm` | 7.7 | 20-40h |
| `conciliacion-bancaria-mensual` | 7.2 | 40-60h |
| `verificar-conciliacion-5dia` | Cron 9.1 | 20-30h |
| `dashboard-cartera-semanal` | Cron 9.1 | 15-25h |
| `procesar-wa-pendientes` | Cron 9.1 | 30-50h |
| `pago-provisional-validator` | Implícito | 15-25h |

**Total esfuerzo workflows**: 210-360 horas.

---

## 4. Hooks pendientes

### Construidos (1/15+)

`scripts/pre-commit.sh` — lint + JSON + tests MCP.

### Planeados sección 8 del doc de planeación

1. `backup-cfdi-automatico` (PostToolUse)
2. `validar-ficha-cliente` (Write validation)
3. `pre-timbrado-validation` (PreToolUse)
4. `bitacora-mcp-calls` (Post MCP)
5. `alert-cancelaciones-frecuentes` (Post CFDIs)
6. `dashboard-cobranza-pendiente` (SessionStart)
7. `alerta-pago-provisional` (SessionStart)
8. `cfdi-vencimientos` (SessionStart)
9. `actualizar-tc-banxico` (SessionStart)
10. `validar-cfdi-payload` (PreToolUse)
11. `confirmar-envio-masivo-whatsapp` (PreToolUse)
12. `sincronizar-shared-pre-commit` (Stop)
13. `backup-sesion` (Stop)

**Total esfuerzo hooks**: 40-80 horas (4-6h por hook).

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

## Resumen ejecutivo del gap

| Categoría | Hecho | Planeado | Faltante | Esfuerzo |
|---|---|---|---|---|
| MCPs | 25 | 21+ | 6 críticos | 800-1,200h |
| Verticales TOP | 11 | 20+ | 15+ | 4,000-5,000h |
| Workflows | 7 | 8+ | 5-7 | 210-360h |
| Hooks | 1 | 15+ | 13 | 40-80h |
| Crons | 2 | 30+ | 27-28 | 50-100h |
| Webhooks | 0 | 12 | 12 | 100-150h |
| Skills nuevos | 120 | +24 | 24 | 300-400h |
| Evals | 25 | 160-385 | 135-360 | 150-250h |
| Docs | 23 | ~35 | 12 | 100-150h |
| Áreas no cubiertas | 0 | 10 | 10 | 2,030-3,050h |
| **TOTAL** | | | | **~7,780-10,740h** |

**Equivalente**: 8-11 meses con equipo 3-4 personas.

**Monetario**: $3.9M-5.4M MXN @ $500/h desarrollo.

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
