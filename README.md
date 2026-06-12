# Plugins MX — Monorepo de Skills, MCPs, Workflows y Plugins para México

Monorepo de **plugins de Claude Code**, **MCP servers** y **skills standalone** para operación diaria de PyMEs y profesionistas en México. Cubre fiscal (CFDI 4.0, SAT, IMSS, INFONAVIT), pagos (TDC, OXXO, SPEI, transferencia), marketplaces (ML, Shopify, Amazon MX), municipales (CDMX, EdoMex, MTY), inmobiliaria, salud veterinaria, eventos, restaurantes, salones y más.

## Estado a 2026-06-11

| Capa | Cantidad | Notas |
|---|---|---|
| **Plugins verticales** | 11 | core-mexico + 10 verticales |
| **MCP servers** | 25 | Mock-first, 872 tests verdes |
| **Workflows multinivel** | 7 | Agents + comandos slash |
| **Skills lint-passing** | 120 | 6 `_shared/` + 114 verticales |
| **Comandos slash** | 52+ | Distribuidos en plugins |
| **Evals (.eval.json)** | 25 | Calibración de triggering |
| **Fixtures de prueba** | 38 | Casos determinísticos |
| **Scripts ejecutables** | 13 | lint, sync, hooks, crons, validadores |
| **Documentos** | 23 | Arquitectura, roadmap, vertical guides |

⚠ **Score honesto promedio**: 4.7/9 (scaffolding denso, lint-passing, no producción). Para llegar a 7.5/9 falta validación experta (capa 3) — ver `docs/estado-real.md` y `docs/plan-afinacion.md`.

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

## Plugins verticales (11)

| Plugin | Skills propios | Comandos | Casos de uso |
|---|---|---|---|
| **`core-mexico`** | — (hereda 6 `_shared/`) | 6 | Base obligatoria: CFDI, WA, RFC, fiscal |
| **`freelancers-mx`** | 5 | 8 | Cotización, propuesta, cobranza, onboarding, ISR provisional, declaración anual |
| **`agencia-marketing-mx`** | 5 | 4 | Reportes Meta Ads, copy MX, CM, brief creativo, optimización |
| **`colegios-mx`** | 4 | 4 | Cobranza colegiaturas, comunicación padres WA, constancias SEP, CFDI D10 |
| **`talleres-mx`** | 4 | 4 | Diagnóstico + cotización, autorización WA, garantía PROFECO, orden de trabajo |
| **`ecommerce-mx`** | 5 | 5 | ML listings + pricing, Shopify MX, inventario multicanal, paqueterías, cierre ventas |
| **`salon-mx`** | 5 | 4 | Agenda + no-shows, tarifario, comisiones estilistas, membresías, loyalty |
| **`veterinaria-mx`** | 5 | 4 | Expediente clínico, vacunación, urgencias 24h, tarifario vet, recordatorios pet |
| **`wedding-mx`** | 5 | 4 | Cotización boda, timeline D-365→D+30, proveedores, onboarding novios, contrato |
| **`restaurante-mx`** | 5 | 4 | Ingeniería menú BCG, inventario merma, propinas (Art. 346 LFT), delivery aggregators, CFDI global |
| **`inmobiliaria-mx`** | 5 | 4 | Contrato arrendamiento, screening inquilinos, comparables zona, ficha inmueble, comisiones |

---

## MCP servers (25)

### Mock + API REST real

| MCP | Tools | Estado |
|---|---|---|
| `mp_banxico` | TCs DOF, UMA, INPC, TIIE | ✅ producción |
| `mp_facturama_extendido` | Timbrar, cancelar, búsqueda CFDI | ✅ producción |
| `mp_mercado_pago` | Pagos, refunds, webhook HMAC | ✅ producción |
| `mp_conekta` | Órdenes, charges, refunds, suscripciones | ✅ producción |
| `mp_mercado_libre` | Listings, órdenes, mensajes, reputación | ✅ producción |
| `mp_shopify_mx` | Products, inventory, orders, fulfillment | ✅ producción |
| `mp_bitso` | Ticker, balance, ledger, fundings | ✅ producción + ISR calc |
| `mp_curp_renapo` | Validación CURP + RENAPO | ✅ producción |
| `mp_banxico_cep` | CLABE + CEP SPEI | ✅ producción |
| `mp_trustly_mx` | Open banking pagos | ✅ producción |
| `mp_clip_terminal` | POS Clip MX | ✅ producción |
| `mp_cabify_business` | Movilidad B2B | ✅ producción |

### Mock + HTTP público parcial / Playwright stub

| MCP | Tools | Estado real |
|---|---|---|
| `mp_sat_portal` | Padrón, 69-B EFOS, 69, CSF, Buzón, CFDI verifica | 4/11 públicos reales, 7 mock |
| `mp_amazon_mx_seller` | Listings, inventory, orders, fees | Mock (LWA+AWSSig V4 no impl) |
| `mp_aspel_contpaqi` | Pólizas, balanza, P&L, Balance General | Mock + parser CSV exports |
| `mp_softrestaurant` | Corte Z, ventas, platillos, meseros | Mock + parser CSV exports |
| `mp_bancos_mx` | Estado cuenta, movimientos, verificar pago | Mock (Playwright real pendiente) |
| `mp_imss_patronal` | IDSE alta/baja, cédula, EMCR, SBC | Mock |
| `mp_infonavit_patronal` | Créditos, EMIS, descuentos | Mock |
| `mp_cdmx_municipal` | Predial, tenencia, multas, hoy no circula | Mock |
| `mp_edomex_municipal` | Predial municipal + tenencia EdoMex | Mock |
| `mp_monterrey_municipal` | Predial AMM + multas NL + aire | Mock |
| `mp_inmuebles24` | Buscar, detalle, comparables, publicar | Mock |
| `mp_vivanuncios` | Multi-categoría (autos/inmuebles/empleos) | Mock |
| `mp_buro_credito_personal` | Score, reporte, alertas — **compliance integrada** | Mock + autorización obligatoria |

Detalles en `mcp-servers/README.md`.

---

## Workflows multinivel (7)

| # | Workflow | Plugin | Comando |
|---|---|---|---|
| 1 | `cfdi-emision-completa` | core-mexico | `/core:emitir-y-notificar` |
| 2 | `pago-conciliacion` | core-mexico | `/core:conciliar-pago` |
| 3 | `cobranza-multinivel` | freelancers-mx | `/freelancers:cobranza-mensual` |
| 4 | `cierre-fiscal-mensual` | core-mexico | `/freelancers:cierre-fiscal` |
| 5 | `due-diligence-cliente` | core-mexico | `/core:due-diligence` |
| 6 | `sync-multicanal` | ecommerce-mx | `/ecommerce:sync-inventario` |
| 7 | `pf-anual-completa` | core-mexico | `/freelancers:declaracion-anual` |

Cada workflow coordina 3-6 MCPs + skills + bitácora trazable.

---

## Hooks + crons activos

### Hooks de git
- `pre-commit`: lint-skills.sh + validación JSON + tests MCP (vía `scripts/pre-commit.sh`)

### Crons configurados (macOS launchd + Linux crontab)
- **Diario L-V 10:00** — `refresh-banxico-tcs.sh` (TCs DOF USD/EUR/GBP/CAD/JPY)
- **Lunes 09:00** — `refresh-sat-listas-69.sh` (69-B EFOS + 69 incumplidos)

Configurar con `bash scripts/install-hooks.sh` (git hooks) + cargar plist macOS o `crontab.linux`.

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
- `[~ Elias 2026-06-11]` en progreso
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

- **Autor**: Elias (elias@cipreholding.com)
- **Licencia**: Proprietary (uso interno + clientes implementación)
- **Repositorio**: https://github.com/elimorals/Skills_MX
