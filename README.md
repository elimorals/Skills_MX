# Plugins MX — Monorepo de Skills, MCPs, Workflows y Plugins para México

Monorepo de **plugins de Claude Code**, **MCP servers** y **skills standalone** para operación diaria de PyMEs y profesionistas en México. Cubre fiscal (CFDI 4.0, SAT, IMSS, INFONAVIT), pagos (TDC, OXXO, SPEI, transferencia), marketplaces (ML, Shopify, Amazon MX), municipales (CDMX, EdoMex, MTY), inmobiliaria, salud veterinaria, eventos, restaurantes, salones y más.

## Estado a 2026-06-12 (reconciliado con filesystem)

| Capa | Cantidad real | Notas |
|---|---|---|
| **Plugins verticales** | **35** | core-mexico + 34 verticales (11 originales + 24 nuevos: TOP del research + áreas no cubiertas specs 07-15) |
| **MCP servers** | **40** | Mock-first, 92 archivos de test, FastMCP + Python |
| **Workflows declarados** | **23 (markdown)** | ⚠ 0 implementados como código ejecutable — son plantillas en `docs/` |
| **Skills (SKILL.md)** | **275** | 6 `_shared/` + 269 distribuidos en verticales |
| **Comandos slash** | **37 directorios `commands/`** | Distribuidos en plugins |
| **Hooks runtime CC** | **15** | PreToolUse (5) + PostToolUse (4) + SessionStart (4) + Stop (1) + `_lib.sh` |
| **Hook git** | **1** | pre-commit (lint + JSON + tests MCP) |
| **Crons activos** | **2** | Banxico TCs (diario L-V) + SAT listas 69 (lunes) |
| **Specs detallados** | **15 + `_template.md`** | docs/specs/ — 6 infraestructura/MCPs + 9 verticales |
| **Evals (.eval.json)** | **181** | Ratio 0.66/skill (objetivo 0.8); faltan críticos: `freelance-tax-mx`, `cfdi-colegiaturas-deducibles`, `pf-anual-mx` |
| **Fixtures de prueba** | **38** | Objetivo 50-100 |
| **Webhook receiver** | **V1 local + 12 handlers** | FastAPI + validators + idempotency SQLite + audit JSONL; V2 deploy pendiente |
| **Scripts ejecutables** | **13+** | lint, sync, hooks, crons, validadores |
| **Documentación** | **25** docs | Arquitectura, roadmap, vertical guides, gap analysis, análisis profundo |

⚠ **Score honesto promedio**: 4.7/9 (scaffolding denso, lint-passing, no producción). Para llegar a 7.5/9 falta validación experta (capa 3) — ver `docs/estado-real.md` y `docs/plan-afinacion.md`.

⚠ **Gap silencioso descubierto 2026-06-12**: los 23 "workflows multinivel" reportados son **plantillas markdown declarativas en `docs/`**, no código ejecutable con `Workflow.workflow()` / `phase()` / `parallel()`. Convertirlos a código real es un Tier 1 pendiente (200-300h). Ver [docs/analisis-profundo-2026-06.md](docs/analisis-profundo-2026-06.md) §3.7 y §7.

---

## Filosofía

- **`_shared/`**: skills base reutilizables (fuente de verdad). Se sincronizan a cada plugin vertical pre-release con `scripts/sync-shared.sh`.
- **Plugins verticales**: paquetes autocontenidos por industria que combinan `_shared/` + skills específicos + comandos + MCPs + agents.
- **MCP servers**: integraciones a servicios mexicanos (SAT, Banxico, IMSS, Mercado Pago, Conekta, Clip, etc.). Todos mock-first — corren sin credenciales con respuestas plausibles marcadas `simulated: true`.
- **Workflows**: agents que coordinan múltiples MCPs + skills para procesos end-to-end (emisión CFDI completa, cierre fiscal, due-diligence, etc.).
- **Skills standalone**: cualquier skill se puede empaquetar como standalone (instalable vía `skillkit` o subida directa a Claude.ai).

---

## Estructura del monorepo

```
plugins-mx/
├── _shared/                      Skills base (fuente de verdad — 6 skills)
│   ├── cfdi-emision/             CFDI 4.0 emisión + complementos
│   ├── iva-retenciones-mx/       IVA + retenciones ISR/IVA por escenario
│   ├── rfc-validacion/           Validación RFC + 69-B + palabras inconvenientes
│   ├── whatsapp-business-mx/     Templates WA aprobables Meta
│   ├── compliance-lfpdppp/       Avisos privacidad + ARCO + INAI
│   └── mxn-formato/              MXN a letra + conversión TC DOF
│
├── core-mexico/                  Plugin base (DEPENDENCIA OBLIGATORIA)
├── freelancers-mx/               Vertical freelance / consultores
├── agencia-marketing-mx/         Vertical agencia digital
├── colegios-mx/                  Vertical colegios K-12
├── talleres-mx/                  Vertical talleres mecánicos
├── ecommerce-mx/                 Vertical ecommerce + marketplaces
├── salon-mx/                     Vertical salones, spas, barberías
├── veterinaria-mx/               Vertical clínicas veterinarias
├── wedding-mx/                   Vertical wedding planners
├── restaurante-mx/               Vertical restaurantes + dark kitchens
├── inmobiliaria-mx/              Vertical corredores inmobiliarios
│
├── mcp-servers/                  25 MCPs (Python + FastMCP)
│   ├── shared/                   Utilidades comunes (cache, bitácora, mock, errors)
│   ├── mp_banxico/               TCs DOF + UMA + INPC + TIIE
│   ├── mp_facturama_extendido/   CFDI 4.0 timbrado + cancelación
│   ├── mp_sat_portal/            Padrón SAT, 69-B EFOS, 69 incumplidos, verifica CFDI
│   ├── mp_mercado_pago/          Pagos + webhooks HMAC + refunds
│   ├── mp_conekta/               Pasarela alternativa MX
│   ├── mp_mercado_libre/         Listings ML + órdenes + mensajes
│   ├── mp_shopify_mx/            Wrapper específico MX sobre Shopify
│   ├── mp_amazon_mx_seller/      Amazon MX SP-API
│   ├── mp_bitso/                 Cripto-fiat MX + calculadora ISR
│   ├── mp_curp_renapo/           Validación CURP + RENAPO
│   ├── mp_banxico_cep/           CLABE + CEP SPEI
│   ├── mp_bancos_mx/             Bancos MX (BBVA, Banamex, Santander…) — Playwright stub
│   ├── mp_imss_patronal/         IDSE: altas/bajas, cédula, EMCR — Playwright stub
│   ├── mp_infonavit_patronal/    Créditos + EMIS — Playwright stub
│   ├── mp_cdmx_municipal/        Predial, tenencia, multas, hoy no circula
│   ├── mp_edomex_municipal/      Predial + tenencia + multas EdoMex
│   ├── mp_monterrey_municipal/   Predial AMM + multas NL + aire
│   ├── mp_inmuebles24/           Búsqueda + comparables zona + publicación
│   ├── mp_vivanuncios/           Multi-categoría (autos/inmuebles/empleos)
│   ├── mp_buro_credito_personal/ Score + reporte (con autorización obligatoria)
│   ├── mp_trustly_mx/            Open banking pagos directos
│   ├── mp_clip_terminal/         POS Clip MX
│   ├── mp_cabify_business/       Movilidad B2B + factura mensual
│   ├── mp_aspel_contpaqi/        Pólizas, balanza, P&L — parser CSV exports
│   └── mp_softrestaurant/        POS restaurantero — parser CSV
│
├── scripts/                      Tooling (13 scripts)
│   ├── lint-skills.sh            Valida frontmatter de cada SKILL.md
│   ├── sync-shared.sh            Sincroniza _shared/ a plugins
│   ├── new-skill.sh              Scaffolding skill nuevo
│   ├── run-fixtures.sh           Corre fixtures de regresión
│   ├── version-bump.sh           Bump semver
│   ├── install-hooks.sh          Instala git hooks
│   ├── pre-commit.sh             Hook: lint + JSON + tests MCP
│   ├── refresh-banxico-tcs.sh    Cron diario TCs DOF
│   ├── refresh-sat-listas-69.sh  Cron semanal listas 69-B
│   ├── validar_facturama_credenciales.py  Validador setup
│   ├── crons/                    launchd plists + crontab Linux
│   └── *.py                      Helpers Python (RFC, MXN, IVA, mock PAC)
│
├── evals/                        Calibración triggering (25 archivos)
├── tests/fixtures/               Casos determinísticos (38 archivos)
├── schemas/                      JSON Schemas validación output (8 archivos)
├── docs/                         Documentación (23 archivos)
├── .env.example                  Plantilla de credenciales
├── marketplace.json              Manifiesto marketplace privado
└── README.md
```

---

## Plugins verticales (35)

### Originales (11)

| Plugin | Casos de uso |
|---|---|
| **`core-mexico`** | Base obligatoria: CFDI, WA, RFC, fiscal (hereda 6 `_shared/`) |
| **`freelancers-mx`** | Cotización, propuesta, cobranza, onboarding, ISR provisional, declaración anual |
| **`agencia-marketing-mx`** | Reportes Meta Ads, copy MX, CM, brief creativo, optimización |
| **`colegios-mx`** | Cobranza colegiaturas, comunicación padres WA, constancias SEP, CFDI D10 |
| **`talleres-mx`** | Diagnóstico + cotización, autorización WA, garantía PROFECO, orden de trabajo |
| **`ecommerce-mx`** | ML listings + pricing, Shopify MX, inventario multicanal, paqueterías, cierre ventas |
| **`salon-mx`** | Agenda + no-shows, tarifario, comisiones estilistas, membresías, loyalty |
| **`veterinaria-mx`** | Expediente clínico, vacunación, urgencias 24h, tarifario vet, recordatorios pet |
| **`wedding-mx`** | Cotización boda, timeline D-365→D+30, proveedores, onboarding novios, contrato |
| **`restaurante-mx`** | Ingeniería menú BCG, inventario merma, propinas (Art. 346 LFT), delivery, CFDI global |
| **`inmobiliaria-mx`** | Contrato arrendamiento, screening inquilinos, comparables zona, ficha, comisiones |

### TOP del research scaffoldeados (15)

| Plugin | Score research | Mercado MX |
|---|---|---|
| **`pf-anual-mx`** | 9.5/10 | ~5M declarantes anuales |
| **`arrendador-residencial-mx`** | 9.3/10 | ~2M arrendadores 1-5 propiedades |
| **`tramites-vehiculares-mx`** | 9.0/10 | ~40M vehículos (multas/predial/tenencia/refrendo) |
| **`conductor-plataforma-mx`** | 8.8/10 | ~1M conductores Uber/DiDi (régimen 625) |
| **`tienda-omnicanal-mx`** | 8.5/10 | ~500k tiendas (sync ML + Shopify + Amazon) |
| **`consultorio-especialista-mx`** | 8.3/10 | ~70k especialistas privados |
| **`clinica-salud-mx`** | 8.3/10 | ~20k clínicas privadas |
| **`airbnb-host-mx`** | 8.2/10 | ~100k anfitriones (CFDI + ISH + régimen 625) |
| **`notarias-mx`** | 8.0/10 | ~5.5k notarios |
| **`despacho-contable-mx`** | 7.9/10 | ~10k despachos |
| **`psicoterapia-mx`** | 7.8/10 | ~40k psicólogos privados |
| **`servicios-publicos-mx`** | 7.8/10 | CFE + agua + gas + predial multi-municipio |
| **`migracion-extranjeros-mx`** | 7.5/10 | ~1.5M residentes extranjeros |
| **`gmm-asegurado-mx`** | 7.5/10 | ~7M pólizas GMM activas |
| **`paciente-mx`** | 7.5/10 | Expediente médico personal agregado |

### Áreas no cubiertas (specs 07-15) (9)

| Plugin | Spec |
|---|---|
| **`telemedicina-mx`** | spec 07 — telemedicina + COFEPRIS + NOM-004 |
| **`nomina-pymes-mx`** | spec 08 — CFDI Nómina 4.0 + IMSS-SUA-IDSE |
| **`cripto-fiscal-mx`** | spec 09 — cripto + CARF 2026 |
| **`educacion-particular-b2c-mx`** | spec 10 — cursos online + CFDI D10/G03 |
| **`donatarias-ongs-mx`** | spec 11 — donatarias autorizadas + transparencia |
| **`importadores-mx`** | spec 12 — pedimentos + IVA + IMMEX |
| **`sucesion-empresa-familiar-mx`** | spec 13 — sucesión + donaciones + protocolo familiar |
| **`crowdfunding-itf-mx`** | spec 14 — Ley Fintech + IFC + P2P |
| **`energia-solar-pyme-mx`** | spec 15 — CFE bidireccional + net metering + GDMTH |

---

## MCP servers (40)

### Tier S — Producción crítica (7)

| MCP | Tools | Estado |
|---|---|---|
| `mp_banxico` | TCs DOF, UMA, INPC, TIIE | ✅ REST real |
| `mp_facturama_extendido` | Timbrar, cancelar, búsqueda CFDI, complementos | ✅ REST real (sandbox + prod) |
| `mp_mercado_pago` | Pagos, refunds, webhook HMAC | ✅ REST real |
| `mp_mercado_libre` | Listings, órdenes, mensajes, reputación | ✅ REST real |
| `mp_curp_renapo` | Validación CURP estructural + RENAPO Playwright | ✅ Estructural real, RENAPO stub |
| `mp_banxico_cep` | CLABE + CEP SPEI | ✅ REST/form-POST |
| `mp_sat_portal` | Padrón, 69-B EFOS, 69, CSF, Buzón, CFDI verifica | ⚠ Esqueleto Playwright + 4/11 HTTP públicos reales |

### Tier A — Pasarelas alternativas + escritura (4)

| MCP | Tools | Estado |
|---|---|---|
| `mp_conekta` | Órdenes, charges, refunds, suscripciones | ✅ REST real |
| `mp_aspel_contpaqi` | Pólizas, balanza, P&L | Mock + parser CSV exports |
| `mp_shopify_mx` | Products, inventory, orders, fulfillment | ✅ REST real |
| `mp_bitso` | Ticker, balance, ledger, fundings + ISR calc | ✅ REST real |

### Tier B — Playwright stub mock-first (9)

| MCP | Tools | Estado |
|---|---|---|
| `mp_bancos_mx` | Estado cuenta, movimientos, verificar pago | ⚠ Esqueleto Playwright (BBVA/Banamex/Santander/Banorte) — falta scraping real |
| `mp_imss_patronal` | IDSE alta/baja, cédula, EMCR, SBC | Mock |
| `mp_infonavit_patronal` | Créditos, EMIS, descuentos | Mock |
| `mp_cdmx_municipal` | Predial, tenencia, multas, hoy no circula | Mock |
| `mp_edomex_municipal` | Predial municipal + tenencia EdoMex | Mock |
| `mp_monterrey_municipal` | Predial AMM + multas NL + aire | Mock |
| `mp_inmuebles24` | Buscar, detalle, comparables, publicar | Mock |
| `mp_vivanuncios` | Multi-categoría (autos/inmuebles/empleos) | Mock |
| `mp_buro_credito_personal` | Score, reporte, alertas — compliance integrada | Mock + autorización obligatoria |

### Tier B — REST + parsers (5)

| MCP | Tools | Estado |
|---|---|---|
| `mp_trustly_mx` | Open banking pagos directos | Mock + REST stub |
| `mp_clip_terminal` | POS Clip MX | Mock + REST stub |
| `mp_cabify_business` | Movilidad B2B + factura mensual | Mock + REST stub |
| `mp_amazon_mx_seller` | Listings, inventory, orders, fees | Mock (LWA+AWSSig V4 no impl) |
| `mp_softrestaurant` | Corte Z, ventas, platillos, meseros | Mock + parser CSV exports |

### Delivery aggregators (3)

| MCP | Estado |
|---|---|
| `mp_rappi_partners` | Mock (clonado de patrón mp_mercado_libre) |
| `mp_didi_food_partners` | Mock |
| `mp_uber_eats_partners` | Mock |

### Municipales + servicios extendidos (12 nuevos)

| MCP | Categoría |
|---|---|
| `mp_cfe_facturacion` | Servicios públicos — recibos CFE + facturación |
| `mp_telmex_facturacion` | Servicios públicos — Telmex |
| `mp_clabe_validador_oficial` | Identidad bancaria — CNBV reverso CLABE |
| `mp_paypal_mx` | Pasarela alternativa |
| `mp_klap` | POS alterno |
| `mp_kueski` | Crédito al consumo (Buy-Now-Pay-Later) |
| `mp_didi_partners` | Movilidad (≠ DiDi Food) |
| `mp_guadalajara_municipal` | Predial + multas GDL |
| `mp_merida_municipal` | Predial + multas Mérida |
| `mp_puebla_municipal` | Predial + multas Puebla |
| `mp_queretaro_municipal` | Predial + multas Querétaro |
| `mp_tijuana_municipal` | Predial + multas Tijuana |

Detalles en `mcp-servers/README.md`.

---

## Workflows multinivel (23 declarados / 0 ejecutables)

⚠ **Gap descubierto 2026-06-12**: los workflows existen como **plantillas markdown declarativas** en `docs/specs/`, `docs/flujos-operativos.md` y `plugins-mx-planeacion-mcps-agentica.md §7`. Para ser ejecutables deberían ser scripts del skill `Workflow` con sintaxis `phase()` / `parallel()` / `pipeline()`. Ver [docs/analisis-profundo-2026-06.md](docs/analisis-profundo-2026-06.md) §3.7.

### Workflows declarados

| # | Workflow | Plugin/spec | Comando declarado |
|---|---|---|---|
| 1 | `cfdi-emision-completa` | core-mexico | `/core:emitir-y-notificar` |
| 2 | `pago-conciliacion` | core-mexico | `/core:conciliar-pago` |
| 3 | `cobranza-multinivel` | freelancers-mx | `/freelancers:cobranza-mensual` |
| 4 | `cierre-fiscal-mensual` | core-mexico | `/freelancers:cierre-fiscal` |
| 5 | `due-diligence-cliente-nuevo` | core-mexico | `/core:due-diligence` |
| 6 | `sync-multicanal` | ecommerce-mx | `/ecommerce:sync-inventario` |
| 7 | `pf-anual-completa` | pf-anual-mx | `/pf-anual:completa` |
| 8 | `monitoreo-diario-vehicular` | tramites-vehiculares-mx | cron-driven |
| 9 | `respuesta-crisis-cm` | agencia-marketing-mx | manual |
| 10 | `conciliacion-bancaria-mensual` | freelancers-mx | cron día 14 |
| 11-23 | Variantes por vertical (cobranza-renta, telemedicina-consulta, donativo-anual, etc.) | Específicos | — |

**Esfuerzo para convertir todos a código ejecutable**: ~200-300h (25-40h por workflow × 8 prioritarios).

---

## Hooks + crons activos

### Hooks git (1)
- `pre-commit`: lint-skills.sh + validación JSON + tests MCP (vía `scripts/pre-commit.sh`)

### Hooks runtime Claude Code (15)

Configurados en `.claude/settings.json` + scripts en `scripts/hooks/`:

| Tipo | Hooks |
|---|---|
| **PreToolUse** (5) | `pre-timbrado-validation`, `confirmar-envio-masivo-wa`, `validar-cfdi-payload`, `validar-ficha-cliente`, `bitacora-mcp-calls` |
| **PostToolUse** (4) | `backup-cfdi-automatico`, `alert-cancelaciones-frecuentes`, `actualizar-tc-banxico`, `sincronizar-shared-post-edit` |
| **SessionStart** (4) | `contexto-inicial-sesion` (orquestador), `dashboard-cobranza-pendiente`, `alerta-pago-provisional`, `cfdi-vencimientos` |
| **Stop** (1) | `cleanup-sesion` |
| **Shared lib** | `_lib.sh` |
| **Test** | `test-all-hooks.sh` (18/18 invocaciones OK) |

### Crons configurados (macOS launchd + Linux crontab)
- **Diario L-V 10:00** — `refresh-banxico-tcs.sh` (TCs DOF USD/EUR/GBP/CAD/JPY)
- **Lunes 09:00** — `refresh-sat-listas-69.sh` (69-B EFOS + 69 incumplidos)
- ⚠ **Pendientes**: ~28 crons del plan (cobranza-recurrente, pre-cierre-fiscal, dashboard-semanal, etc.)

Configurar con `bash scripts/install-hooks.sh` (git hooks) + cargar plist macOS o `crontab.linux`.

### Webhook receiver (V1 local)
- FastAPI app en `webhooks/app/`
- 12 handlers: Stripe, MP, Conekta, Facturama, Meta WhatsApp, GitHub, Calendly, Typeform, ML, Banxico CEP, IMSS, CONDUSEF
- Validators HMAC + Bearer + IP allowlist
- Idempotencia SQLite + memoria
- Audit log JSONL append-only
- Tests: 29/29 pasando
- ⚠ **V2 pendiente**: deploy producción HTTPS público + retry queue async

---

## Instalación

### Como plugins de Claude Code

```bash
/plugin marketplace add elias/plugins-mx
/plugin install core-mexico      # obligatorio
/plugin install freelancers-mx   # ejemplo de vertical
```

### Como skills standalone

```bash
skillkit install cfdi-emision    # desde _shared/
```

### Para desarrollo

```bash
# Clonar
git clone https://github.com/elimorals/Skills_MX
cd Skills_MX

# Setup MCP servers
cd mcp-servers
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"

# Correr tests
.venv/bin/python -m pytest -q

# Lint skills
cd ..
bash scripts/lint-skills.sh

# Instalar hooks git
bash scripts/install-hooks.sh

# Crear `.env` para credenciales reales (opcional — mock por default)
cp .env.example .env
nano .env
```

### Validar credenciales Facturama (si las tienes)

```bash
python scripts/validar_facturama_credenciales.py
```

---

## Metodología de desarrollo

El proyecto sigue **spec-first para items novedosos** y **pattern-based para variantes**.

### Spec-first (items novedosos)

Cuando lo siguiente NO tiene patrón previo en el repo, crea spec en `docs/specs/` ANTES de codificar:

- Primer webhook receiver
- Primer hook runtime Claude Code
- Primer Playwright real con e.firma
- Vertical con score >= 9.0 del research
- Áreas no cubiertas (telemedicina, nómina, seguros, etc.)

Plantilla: `docs/specs/_template.md`. Specs vivos: `docs/specs/README.md`.

### Pattern-based (variantes)

Cuando hay patrón establecido, clonar y ajustar:

- Otro MCP Tier B con API REST → clonar `mp_conekta`
- Otro vertical scaffold → clonar `salon-mx` o `talleres-mx`
- Otro workflow variante → clonar `workflow-cobranza-multinivel`
- Otro skill en vertical existente → seguir convenciones del directorio

### Checklist vivo de progreso

Cada sesión que cierre un módulo debe actualizar `docs/STATUS.md`:
- Cambiar `[ ]` → `[x]` con fecha + commit hash
- Si descubres trabajo nuevo no listado: agregar como `[NUEVO desc-YYYY-MM-DD]`
- Mover "Próximo item recomendado" si lo concluiste

Convención de checks:
- `[ ]` pendiente
- `[~ Elías 2026-06-11]` en progreso
- `[x]` hecho (fecha + commit + nota corta)
- `[!]` bloqueado (con razón)
- `[-]` descartado (con razón)

### Ciclo completo

```
1. Leer docs/STATUS.md → identificar próximo item
2. Si item novedoso → crear/leer spec en docs/specs/
3. Codificar siguiendo el spec (o el patrón si aplica)
4. Tests verde + lint passing
5. Commit + push
6. Actualizar docs/STATUS.md con [x] + commit hash
7. Si descubriste algo nuevo: agregar al STATUS o crear spec nuevo
```

---

## Convenciones técnicas

- **`description:` del frontmatter SKILL.md**: español MX + sinónimos inglés para triggering robusto
- **Skills < 500 líneas**: referencias largas → `references/` directory
- **Toda integración** abstraída detrás de interfaces mockeables (`shared.mock.is_mock_mode()`)
- **Cumplimiento LFPDPPP** por defecto en skills que tocan datos personales
- **Compliance integrada al nivel de schema** (ej. `mp_buro_credito_personal` exige `autorizacion_token` Pydantic)
- **Bitácora append-only JSONL** con hash de identificadores sensibles (RFC, CURP, email)
- **Tests MCP** isolados (cache + audit en tmp_path)
- **Pre-commit obligatorio** bloquea commits con `.env`, secrets en diff, JSON inválido, tests rotos

---

## Qué falta construir (gap vs planeación original)

Auditoría detallada en `docs/gap-analysis-2026-06.md` (próximamente). Resumen ejecutivo:

| Categoría | Hecho | Planeado | Gap |
|---|---|---|---|
| MCPs Tier S/A/B | 25 | 21+ | Faltan partners delivery (Rappi/DiDi/UberEats), Playwright bancos reales |
| Verticales | 11 | TOP 20 del research | 9+ verticales TOP scores >7.5 (pf-anual-mx, arrendador-residencial-mx, tramites-vehiculares-mx…) |
| Workflows | 7 | 8+ | 1 webhook handler (emitir-cfdi-tras-pago) + 5-7 secundarios |
| Hooks | 1 (pre-commit) | 15+ | 13+ hooks específicos (backup-cfdi, validar-ficha-cliente, alerta-pago-provisional…) |
| Crons | 2 | 30+ | 27-28 crons específicos por vertical |
| Webhooks | 0 receiver | 12 | Receiver completo + handlers |
| Evals | 25 | 160-385 | 135-360 evals por afinación triggering |
| Validación experta | 0 | 4+ verticales | Contador, abogado, partners — no codificable |

**Esfuerzo total restante**: ~6,250-8,600 horas (8-11 meses con equipo 3-4 personas).

**Lo NO codificable** (capa 3, requiere humanos externos):
- Validación fiscal con contador certificado (vigencia tarifas RMF 2026)
- Revisión legal contratos por abogado mercantilista
- Aprobación templates WhatsApp por Meta real
- Partners del sector validando outputs (vet, salonero, dueño taller, directora colegio)

---

## Distribución

- **Repositorio**: https://github.com/elimorals/Skills_MX
- **Marketplace privado**: `marketplace.json` configurable
- **Skills standalone**: empaquetables individualmente con `skillkit`

---

## Documentación

Empieza por `docs/INDEX.md`. Documentos clave:

| Documento | Propósito |
|---|---|
| `docs/arquitectura.md` | Modelo `_shared/` + verticales + criterios 9 puntos producción |
| `docs/estado-real.md` | Auditoría honesta de scoring por skill (4.7/9 promedio) |
| `docs/plan-afinacion.md` | Roadmap 36 semanas vertical-por-vertical |
| `docs/roadmap.md` | Visión 12 meses + nuevos verticales |
| `docs/integracion-pac.md` | Cómo conectar Facturama sandbox/producción |
| `docs/integracion-whatsapp.md` | Cómo conectar Meta WhatsApp Business |
| `docs/integracion-pagos.md` | Stripe + Mercado Pago + Conekta |
| `docs/compliance-checklist.md` | LFPDPPP, SAT, PROFECO, IMSS |
| `docs/seguridad.md` | Credenciales, secrets, datos en tránsito |
| `docs/glosario-fiscal-mx.md` | CFDI, regímenes, retenciones, RMF |
| `docs/guia-vertical-*.md` | Guías operativas por vertical |

---

## Compliance y advertencias

⚠ **No usar en producción real** sin validación experta del sector:
- Skills fiscales (`freelance-tax-mx`, `cfdi-colegiaturas-deducibles`, `pf-anual-completa`): contador certificado debe validar tarifas vigentes 2026.
- Contratos generados (`propuesta-comercial`, `contrato-arrendamiento-mx`, `contrato-boda-pf-pm`): abogado mercantilista debe revisar.
- Templates WhatsApp (`whatsapp-business-mx`): pasar por aprobación Meta real antes de envío masivo.
- `mp_buro_credito_personal`: consulta sin autorización del titular es DELITO (Art. 32 LFPDPPP + LRSIC). Schema Pydantic exige `autorizacion_token` válido.
- Operaciones de escritura SAT (`sat_actualizar_obligaciones`): doblemente bloqueadas — requieren `PLUGINS_MX_SAT_PERMITIR_ESCRITURA=1` + path real no implementado por seguridad.

---

## Licencia y autor

- **Autor**: Elías Rashid Morales Mendoza (elimoralsmendox@gmail.com)
- **Licencia**: Proprietary (uso interno + clientes implementación)
- **Repositorio**: https://github.com/elimorals/Skills_MX
