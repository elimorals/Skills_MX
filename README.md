# Plugins MX — Monorepo de Skills, MCPs, Workflows y Plugins para México

Monorepo de **plugins de Claude Code**, **MCP servers** y **skills standalone** para operación diaria de PyMEs y profesionistas en México. Cubre fiscal (CFDI 4.0, SAT, IMSS, INFONAVIT), pagos (TDC, OXXO, SPEI, transferencia), marketplaces (ML, Shopify, Amazon MX), municipales (CDMX, EdoMex, MTY), inmobiliaria, salud veterinaria, eventos, restaurantes, salones y más.

## Estado a 2026-06-13 (post-discovery nacional)

| Capa | Cantidad real | Notas |
|---|---|---|
| **Plugins verticales** | **40** | core-mexico + 39 verticales (11 originales + 15 TOP research + 9 specs 07-15 + 5 nuevos) |
| **MCP servers** | **49** | 43 anteriores + **6 nuevos compliance/research 2026-06-14** (FASES 56-61): `mp_sep_profesional` (cédulas SEP), `mp_repse_stps` (Art. 15 LFT), `mp_isn_mx` (Impuesto Nómina 32 estados), `mp_donatarias_sat` (Anexo 14 RMF), `mp_cnbv_fintech` (Ley Fintech IFPE/IFC), `mp_dof_api` (Diario Oficial de la Federación) |
| **MCPs municipales individuales** | 8 (todos refactorizados a catálogo central) | cdmx, edomex, guadalajara, merida, monterrey, puebla, queretaro, tijuana |
| **Cliente Python standalone** | 1 (`clients/predial_mx_client/`) | Para apps externas (Django/FastAPI/scripts) que NO usan Claude Code |
| **Workflows ejecutables (`.workflow.js`)** | **24/23 ✅** | 23 originales + 1 producto (`cartera-predial-multi-municipio` para inmobiliaria-mx) |
| **Catálogo central municipios MX** | **243 muns (32 estados)** | `shared/catalogo_municipios_mx.py`. **68 validados con URL real**, **52 con selectores DOM verificados** |
| **Cobertura efectiva consultable** | **163 municipios** | 68 directos + 95 SACPI Michoacán = **27.1% pob nacional (35.2M hab)** |
| **Plataformas SaaS estatales** | 1 (SACPI MICH) | +95 muns extra via 1 URL. Investigadas y descartadas: Oaxaca SIOX, Puebla, Veracruz, EdoMex (Art. 115 Constitucional - predial es municipal puro) |
| **Tests pytest nuevos** | **52** (todos pasan) | 19 mp_predial_mx + 13 mp_sacpi + 8 mp_multas + 12 cliente standalone |
| **Cron mensual mantenimiento** | 1 (`scripts/crons/`) | launchd macOS día 5 de cada mes: health-check + discovery delta + auto-aplicar hallazgos |
| **Skills (SKILL.md)** | **307** | 6 `_shared/` + 301 distribuidos en 40 plugins (máx: freelancers-mx 15, inmobiliaria-mx 14, colegios-mx 12) |
| **Comandos slash** | **44 directorios `commands/`** | ~152 comandos totales |
| **Hooks runtime CC** | **19** | PreToolUse (5) + PostToolUse (4) + SessionStart (4) + Stop (1) + utilitarios |
| **Hook git** | **1** | pre-commit (lint + JSON + tests MCP) |
| **Crons activos** | **30+ scripts** | Banxico (diario L-V) + SAT 69 (lunes) + cobranza, cierre fiscal, vencimientos, dashboard, e.firma 90d, ISH airbnb, multas vehiculares, etc. |
| **Specs detallados** | **16 + `_template.md`** | docs/specs/ — 6 infraestructura/MCPs + 10 verticales (specs 07-15 cubiertos ✅) |
| **Evals (.eval.json)** | **281** | Ratio 0.92/skill (supera objetivo 0.8) — cobertura genérica + específica por vertical |
| **Fixtures de prueba** | **166** | Supera objetivo inicial 50-100 |
| **Webhook receiver** | **V1 local + 15 handlers** | FastAPI + validators + idempotency SQLite + audit JSONL; V2 deploy pendiente |
| **Scripts ejecutables** | **13+** | lint, sync, hooks, crons, validadores |
| **Documentación** | **31** docs (+ subdirs adrs/consultorias/dogfooding) | Arquitectura, roadmap, vertical guides, gap analysis, análisis profundo, audit 2026-06-13 |

⚠ **Score honesto promedio**: 4.7-5.5/9 (scaffolding denso, lint-passing, evals/fixtures abundantes, no validado en producción). Para llegar a 7.5/9 falta validación experta (capa 3) — ver `docs/estado-real.md`, `docs/plan-afinacion.md` y `docs/AUDIT-2026-06-13.md`.

✅ **Gap del 2026-06-12 cerrado**: los workflows ejecutables existen (16 `.workflow.js` con `phase()`/`parallel()`/`pipeline()`). Quedan ~7 plantillas markdown por convertir a código.

🆕 **Infra Playwright real (2026-06-13)**: helpers `shared/playwright_real.py` + `shared/playwright_municipal_generic.py` con context manager, fallback gracioso a mock, lazy import (no requiere playwright si no se usa). Implementaciones reales (paths públicos sin login):
- `mp_inmuebles24`: búsquedas, detalle, comparables
- `mp_cdmx_municipal`: predial, tenencia
- `mp_edomex/monterrey/guadalajara/merida/puebla/queretaro/tijuana_municipal`: predial + multas (esqueletos con selectores experimentales)

🆕 **REST real Amazon SP-API (2026-06-13)**: LWA token exchange + 6 endpoints reales (`mp_amazon_mx_seller`). Marketplace MX ID constante. Cache de access_token en memoria con auto-refresh.

🆕 **Catálogo central de municipios MX (2026-06-13, ampliado)**: `shared/catalogo_municipios_mx.py` con **32 estados + 209 municipios (88.3M habitantes / 68% pob. nacional)**. 23 validados con URL real verificada Playwright MCP, **10 con selectores DOM verificados**. Helpers `buscar_portal_predial(estado, municipio)` reemplazan el patrón "1 MCP por municipio".

🆕 **Suite de scripts de descubrimiento (2026-06-13)**:
- `scripts/descubrir-portal-municipal.py`: auto-discover Playwright que toma JSON de municipios y descubre URLs + stack + selectores. Paralelizable, idempotente, reanudable.
- `scripts/health-check-portales.py`: valida selectores contra portales reales.
- `scripts/municipios-pendientes-discover.json`: lista de 144 municipios listos para correr el discover.

🆕 **Patrones MCP municipal (`docs/PATRONES-MCP-MUNICIPAL.md`)**: 5 stacks documentados (ASP.NET WebForms, Angular Material, PHP, ASP clásico, IP+puerto) con templates de código por stack, handlers Playwright reusables, y "cómo agregar un municipio en 5 líneas".

🆕 **🎯 Plataformas SaaS gubernamentales — SACPI Michoacán (`shared/plataformas_saas_mx.py`)**: 1 URL + selector cubre **95 municipios MICH**. Hallazgo de mayor ROI: ratio 95:1 vs discovery individual. Próximas plataformas a investigar: Oaxaca (570 muns), Puebla (217), Veracruz (212).

🆕 **Discovery a escala completado (FASE 18)**: corrida real sobre 144 municipios en background — 7 nuevos validados automáticamente (García NL, Tepatitlán JAL, Altamira TAM, Valle de Santiago GTO, Monclova COAH, Jesús María AGS, Ciudad Hidalgo MICH). Output crudo: `hallazgos-144-2026-06-13.json`.

🆕 **Refactor a catálogo central (FASES 19-20-23)**: 7 MCPs municipales (`mp_edomex`, `mp_cdmx`, `mp_monterrey`, `mp_guadalajara`, `mp_merida`, `mp_puebla`, `mp_tijuana`) ya NO mantienen URLs hardcoded. Consultan el catálogo central — cuando el discovery encuentra una URL nueva, todos los MCPs se benefician automáticamente.

🆕 **Lista INEGI top500 (`scripts/municipios-inegi-top500.json`)**: 145 municipios prioritarios extra (10.8M habitantes) listos para correr discovery — extiende cobertura potencial a ~700 municipios.

📋 **Sesión completa documentada en `docs/SESION-COMPLETA-2026-06-13.md`**: índice maestro de las 24 fases ejecutadas + métricas + próximos pasos.

🆕 **20 workflows ejecutables (2026-06-13)**: +4 nuevos (`sync-multicanal` ecommerce-mx, `cobranza-renta-mensual` inmobiliaria-mx, `donativo-anual` donatarias-ongs-mx, `cripto-cierre-anual` cripto-fiscal-mx). Total `16 → 20`. Plantillas markdown pendientes: 7 → 3.

🆕 **APIs oficiales documentadas (`docs/apis-oficiales-mx.md`)**: rutas legales y técnicas para SAT (descarga masiva REST con e.firma), IMSS (IDSE SOAP), Open Banking MX (CNBV BBVA/Banorte sandbox), Buró de Crédito (API B2B). **No** se documentan bypass de CAPTCHA — son ilegales y no funcionan a mediano plazo.

### 🆕 Bloque post-FASE 23 (sesión continua 2026-06-13)

🆕 **3 MCPs unificados nuevos** (FASES 30-34):
- `mp_predial_mx` — 4 tools, consulta CUALQUIER municipio del catálogo via auto-routing (catálogo directo | SACPI | Mérida-dirección | Puebla-captcha). Reemplaza funcionalmente los 8 MCPs municipales (mantenidos por backward compat).
- `mp_sacpi_michoacan` — 3 tools, expone los 95 municipios MICH via SACPI como tool calls invocables.
- `mp_multas_mx` — 2 tools, multas vehiculares estatales de 8 estados (CDMX requiere CAPTCHA humano-en-loop).

🆕 **Cliente Python standalone (`clients/predial_mx_client/`)** (FASE 37): librería pura para Django/FastAPI/scripts/notebooks. API ergonómica con tipos `PredialResponse`, `MunicipioInfo`, excepciones `NoSoportadoError`/`PortalCaidoError`/`CaptchaRequeridoError`. Ejemplos integración en su `README.md`.

🆕 **52 tests pytest nuevos** (FASE 33), todos pasan:
- `mp_predial_mx/tests/` — 19 tests (consulta, listar, buscar, edge cases, no-leak bitácora)
- `mp_sacpi_michoacan/tests/` — 13 tests (catálogo, lookups, alias)
- `mp_multas_mx/tests/` — 8 tests (placas, CAPTCHA humano-en-loop, validación)
- `clients/predial_mx_client/tests/` — 12 tests (API standalone)

🆕 **Producto vendible: Workflow `cartera-predial-multi-municipio`** (FASE 26): consulta predial en paralelo de N propiedades en distintos municipios → dashboard XLSX con vencimientos/descuentos/ranking. Para arrendadores, despachos contables, inmobiliarias. Skill `dashboard-cartera-predial-xlsx` + comando `/inmobiliaria:cartera-predial`.

🆕 **🎯 Discovery NACIONAL completo** (FASES 38-41): corrida sobre **2,330 municipios INEGI** (todos los que faltaban). Output `hallazgos-nacional-2026-06-13.json` (951KB). **36 OK descubiertos → 34 válidos aplicados al catálogo** (HGO 4, NL 4, QRO 3, ZAC 3, AGS/COAH/GTO/JAL/EdoMex/PUE 2 c/u, +1 más estados). Tasa éxito 1.5% — confirma realidad estructural: 60%+ de muns MX no tienen portal interactivo (Art. 115 + presupuesto).

🆕 **API INEGI WSCatGeo descubierta** (FASE 38, mayor hallazgo arquitectural): `https://gaia.inegi.org.mx/wscatgeo/v2/mgem/agem/` devuelve los 2,478 municipios oficiales con nombres + códigos + población. Pública, estable, sin auth. Documentada como source-of-truth en `docs/apis-oficiales-mx.md`.

🆕 **Sprint Top 15 — Compliance & Research (FASES 56-61, 2026-06-14)**: 6 MCPs nuevos cubriendo 33.3% del Top 15 priorizado del research previo (`docs/TRAMITES-MX-NO-IMPLEMENTADOS-2026-06-14.md`). Hallazgo crítico: el **DOF es la columna vertebral del compliance horizontal** — autorizaciones ITF, sanciones, NOMs y modificaciones a RMF pasan por ahí primero. CNBV/SAT bloquean bots, snapshot curado + tools de decisión binaria (Art. 5 Ley Fintech, Art. 15 LFT, NOM-004, CFDI D04) cubren los casos B2B críticos. Roadmap del Sprint 2 en `docs/FASE-61-SPRINT-3-MCPS-2026-06-14.md`.

🆕 **Website comercial desplegado**: landing editorial-fiscal en `website/`, live en `https://skills-mexico.vercel.app/`. 3 productos vendibles (Cartera Predial · Compliance REPSE · ISN-as-a-Service), 0 dependencias, animaciones con `IntersectionObserver` + tilt 3D + magnetic buttons. SEO con JSON-LD Organization + ItemList.

🆕 **Cron mensual de mantenimiento** (FASE 28): `scripts/crons/mantenimiento-mensual-portales.sh` + `com.plugins-mx.mantenimiento-portales.plist` (launchd macOS día 5 a las 03:00). Pipeline: health-check de validados + discovery delta de pendientes + auto-aplicar hallazgos via `scripts/aplicar-hallazgos-al-catalogo.py` (detecta falsos positivos: username/searchword/wp-login/captcha responses). Auto-commit opcional con `MP_AUTO_COMMIT=1`.

🆕 **Exploración profunda Playwright MCP** (FASES 44-45): muestreo top 30 muns por población de `no_form_detectado` para validar hipótesis. **+1 municipio descubierto** (Ahome Sinaloa 449k hab, ASP.NET WebForms con 6 campos catastrales). Confirma retornos decrecientes: el discovery automático ya capturó ~95% de lo automatizable. Próximo gain requiere acuerdo formal con ayuntamientos o hardcoding manual.

🆕 **Validación MCPs a producción** (FASES 46-55): 17 MCPs ahora con path real validado (vs 10 antes), 14 con selectores DOM aplicados al código. Hallazgos:
- **Nuevo módulo `shared/sep_cedula.py`** — desbloquea `telemedicina-mx` (NOM-004 cédula profesional SEP **sin CAPTCHA**, totalmente automatizable)
- **URL Verifica CFDI SAT corregida** (`/default.aspx` → `/`) + selectores ASP.NET WebForms
- **URL Lista 69 SAT marcada caída** desde 2025 (SAT migró a minisitio DatosAbiertos)
- **CEP Banxico, RENAPO, Verifica CFDI, CFE Mi Espacio** documentados con CAPTCHA → humano-en-loop
- **Mercado Libre listings** (`li.ui-search-layout__item`) y **Inmuebles24 detalle** (selectores wildcard `[class*='...']`) aplicados a Playwright real
- **🎯 Producto Cartera Predial XLSX validado end-to-end**: 5 propiedades demo, auto-routing (CDMX directo + JAL + SACPI Michoacán + NL), `NoSoportadoError` gracioso para inválidos. **Vendible AHORA** a despachos contables/inmobiliarias.

📋 **Reportes técnicos generados esta sesión**:
- `docs/SESION-COMPLETA-2026-06-13.md` — índice maestro de 50+ fases
- `docs/COBERTURA-NACIONAL-2026-06-13.md` — reporte ejecutivo discovery nacional
- `docs/INVESTIGACION-SAAS-ESTATALES-2026-06-13.md` — por qué SACPI es excepción
- `docs/VALIDACION-PORTALES-2026-06-13.md` — validación con Playwright MCP
- **`docs/VALIDACION-MCPS-PRODUCCION-2026-06-13.md`** — auditoría exhaustiva Tier 1+2 MCPs
- `docs/SMOKE-TEST-DISCOVERY-2026-06-13.md` — QA del script discovery
- `docs/PATRONES-MCP-MUNICIPAL.md` — 5 stacks + templates
- `docs/AUDIT-2026-06-13.md` — auditoría inicial reconciliación

Activación:
```bash
# Sitios públicos sin login (búsquedas, predial, multas)
export MP_PLAYWRIGHT_PUBLIC=1
pip install playwright && playwright install chromium

# Amazon SP-API
export AMAZON_SP_REFRESH_TOKEN="Atzr|..." AMAZON_SP_CLIENT_ID="..." AMAZON_SP_CLIENT_SECRET="..."
```

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

## Plugins verticales (40)

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

### Verticales adicionales scaffoldeados (5)

| Plugin | Cobertura |
|---|---|
| **`agente-seguros-mx`** | Cotización pólizas, renovación, comisiones, CNSF |
| **`constructora-mx`** | REPSE mensual, IMSS construcción, ISN, contratistas |
| **`despacho-legal-mx`** | Litigios, honorarios, retenciones ISR profesionales, expediente legal |
| **`geriatria-cuidado-mayor-mx`** | Residencias asistidas, NOM-167, expediente geriátrico |
| **`laboratorio-clinico-mx`** | NOM-007, COFEPRIS, resultados, facturación seguros |

---

## MCP servers (49)

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

### 🆕 Compliance, validación profesional & monitoreo legal (6 nuevos · FASES 56-61)

| MCP | Categoría | Universo afectado | Tests |
|---|---|---|---|
| `mp_sep_profesional` | Validación cédula profesional federal SEP — desbloquea `telemedicina-mx` (NOM-004 + COFEPRIS 2024). Sin captcha. | Médicos, abogados, contadores, arquitectos, ingenieros | 17 ✓ |
| `mp_repse_stps` | Compliance Art. 15 LFT — subcontratación. `verificar_proveedor` decide compliance binario. Sin captcha funcional. | ~4M empresas B2B que contratan servicios especializados | 21 ✓ |
| `mp_isn_mx` | Impuesto sobre Nómina multi-estado — 32 entidades catalogadas (8 validadas Playwright), tasas 1.8%–3.0% | ~4M empresas formales con trabajadores | 24 ✓ |
| `mp_donatarias_sat` | Padrón donatarias autorizadas SAT (Anexo 14 RMF). Crítico para CFDI uso D04. Path real diferido (Akamai). | ~10k donatarias + donantes que deducen | 17 ✓ |
| `mp_cnbv_fintech` | Padrón ITF Ley Fintech (IFPE/IFC). `verificar_contraparte` empaqueta Art. 5 Ley Fintech. Catálogo curado DOF+SIPRES. | Ecosistema fintech, cripto, crowdfunding | 15 ✓ |
| `mp_dof_api` | Diario Oficial de la Federación — sumario diario, búsqueda full-text histórica, detalle de nota, monitor por keywords. 100% público. | Compliance horizontal: despachos legales/contables, áreas regulatorias | 22 ✓ |

**Total tests nuevos FASES 56-61**: 116 pasando. Cobertura Top 15 priorizado: **5/15 = 33.3%**.

Detalles en `mcp-servers/README.md` y `docs/FASE-61-SPRINT-3-MCPS-2026-06-14.md`.

---

## Workflows multinivel (16 ejecutables / ~7 plantillas markdown pendientes)

✅ **16 workflows ejecutables** en `.workflow.js` usando API del skill `Workflow` con `phase()` / `parallel()` / `pipeline()`:

### Ejecutables (`.workflow.js`)

| # | Workflow | Plugin | Disparador |
|---|---|---|---|
| 1 | `cfdi-emision-completa` | core-mexico | `/core:emitir-y-notificar` |
| 2 | `pago-conciliacion` | core-mexico | webhook + `/core:conciliar-pago` |
| 3 | `cierre-fiscal-mensual` | core-mexico | cron día 14 |
| 4 | `due-diligence-cliente` | core-mexico | `/core:due-diligence` |
| 5 | `emitir-cfdi-tras-pago` | core-mexico | webhook MP/Conekta/Stripe |
| 6 | `auditoria-fiscal-mensual` | core-mexico | cron día 1 |
| 7 | `validacion-cfdis-historico` | core-mexico | manual |
| 8 | `cobranza-multinivel` | freelancers-mx | `/freelancers:cobranza-mensual` |
| 9 | `migracion-rfc-a-otro-regimen` | freelancers-mx | manual |
| 10 | `pf-anual-completa` | pf-anual-mx | `/pf-anual:completa` |
| 11 | `dispersion-nomina` | nomina-pymes-mx | quincenal/mensual |
| 12 | `reporte-cliente-agencia` | agencia-marketing-mx | mensual |
| 13 | `respuesta-crisis-cm` | agencia-marketing-mx | manual |
| 14 | `comunicacion-padres-masiva` | colegios-mx | manual |
| 15 | `garantia-vehicular` | talleres-mx | post-servicio |
| 16 | `monitoreo-diario-vehicular` | tramites-vehiculares-mx | cron diario |

### Plantillas markdown pendientes de codificar (7)

`sync-multicanal` (ecommerce-mx), `cobranza-renta-mensual` (inmobiliaria-mx), `telemedicina-consulta` (telemedicina-mx), `donativo-anual` (donatarias-ongs-mx), `pedimento-importacion` (importadores-mx), `cripto-cierre-anual` (cripto-fiscal-mx), `energia-bidireccional-mensual` (energia-solar-pyme-mx).

**Esfuerzo para los 7 restantes**: ~25-40h cada uno (175-280h total).

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

Auditoría detallada en `docs/AUDIT-2026-06-13.md` y `docs/gap-analysis-2026-06.md`. Resumen ejecutivo actualizado:

| Categoría | Hecho | Planeado | Gap real |
|---|---|---|---|
| MCPs Tier S/A | 11 | 11 | ✅ Cubierto (Banxico, Facturama, MP, ML, CURP, CEP, Conekta, Aspel, Shopify, Bitso, SAT esqueleto) |
| MCPs Tier B Playwright | 9 esqueletos | 9 con scraping real | **5/9 bloqueados por CAPTCHA/MFA/e.firma** (bancos, IMSS, INFONAVIT, SAT, Buró). Factibles sin login: Inmuebles24, Vivanuncios, municipales (consulta pública con boleta) |
| MCPs Tier B REST stub | 5 mock | 5 con auth real | mp_clip (factible), mp_amazon_seller (LWA+SigV4 complejo), mp_trustly/cabify/softrestaurant (parcial) |
| MCPs delivery aggregators | 3 mock | 3 con auth real | Rappi/DiDi/UberEats — APIs restringidas a partners aprobados |
| Verticales scaffoldeados | 40 | 40 | ✅ Cubierto (incluye specs 07-15 + 5 extras no documentados antes) |
| Verticales con código profundo | ~10 | 40 | 30 verticales con scaffolding pero skills sin lógica profunda |
| Workflows ejecutables | 16 | 23 | 7 plantillas markdown pendientes de codificar (~175-280h) |
| Hooks runtime | 19 | 15+ | ✅ Superado |
| Crons | 30+ | 30+ | ✅ Cubierto |
| Webhooks | 15 handlers V1 local | 12+ V2 producción | V2 deploy HTTPS + retry queue async |
| Evals | 281 | 160-385 | ✅ En rango — afinación específica vertical |
| Fixtures | 166 | 50-100 | ✅ Superado |
| Validación experta | 0 | 4+ verticales | **No codificable** — contador, abogado, COFEPRIS, Meta |

**Esfuerzo total restante (recalculado 2026-06-13)**: ~3,500-5,000h (4-7 meses con equipo 3-4 personas). Bajó de 6,250-8,600h por: (a) workflows ejecutables descubiertos, (b) evals/fixtures ya cubiertos, (c) specs 07-15 ya escritos.

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
