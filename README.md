# Plugins MX

Plugins de Claude Code, skills y MCP servers para operar una PyME o profesión en México: CFDI 4.0, SAT, nómina e IMSS, pagos, marketplaces, trámites estatales y municipales, y 40 verticales por industria.

| | |
|---|---|
| **Plugins verticales** | 40, cada uno con sus skills, comandos, agentes y MCPs |
| **Skills** | 342 (6 base en `_shared/` sincronizadas a cada plugin) |
| **MCP servers** | 83 en Python + FastMCP, 417 tools |
| **Workflows ejecutables** | 26 (`*.workflow.js`) |
| **Hooks de Claude Code** | 19 (validación de timbrado, bitácora, alertas) |
| **Webhook receiver** | FastAPI con 13 handlers (Stripe, Mercado Pago, Conekta, Facturama, WhatsApp…) |
| **Calidad** | 1,900 tests, 285 evals de triggering, casos golden de cálculo fiscal, CI en cada PR |

---

## Contenido

1. [Estado de los MCPs](#estado-de-los-mcps)
2. [Inicio rápido](#inicio-rápido)
3. [Cómo está organizado](#cómo-está-organizado)
4. [Plugins verticales](#plugins-verticales)
5. [MCP servers](#mcp-servers)
6. [Configuración y credenciales](#configuración-y-credenciales)
7. [Solver de CAPTCHA (opt-in)](#solver-de-captcha-opt-in)
8. [Calidad y pruebas](#calidad-y-pruebas)
9. [Seguridad y cumplimiento](#seguridad-y-cumplimiento)
10. [Pendientes](#pendientes)
11. [Documentación](#documentación)
12. [Licencia](#licencia)

---

## Estado de los MCPs

Cada MCP declara en su README una sección **"Estado real"** con lo que se validó en vivo, cuándo y contra qué URL. La tabla de abajo se genera de esas secciones; no se edita a mano.

<!-- estado-mcps:inicio -->
### Estado a 2026-10-14 (oleada 1: mock → real)

Generado por `scripts/generar-estado-mcps.py` desde la sección "Estado real" de cada README. 83 MCPs, 417 tools.

| Categoría | MCPs |
|---|---|
| Real, validado en vivo | 24 |
| Real sin validar (requiere credenciales) | 13 |
| Entrega a humano (CAPTCHA o login) | 17 |
| Sin API pública | 6 |
| Cálculo normativo verificado | 10 |
| Bloqueado | 2 |
| Sin verificar | 11 |
<!-- estado-mcps:fin -->

**Qué significa cada categoría:**

| Categoría | Significado |
|---|---|
| Real, validado en vivo | Consulta el portal o API oficial y se probó en vivo; la evidencia está en su README |
| Real sin validar | Cliente escrito contra la documentación oficial; falta una credencial para probarlo |
| Entrega a humano | El portal exige CAPTCHA o login: el tool devuelve URL, pasos y campos prellenados |
| Sin API pública | El proveedor no ofrece API; el tool responde un error explícito con la alternativa |
| Cálculo normativo | Cálculo local con tasas y reglas citadas a su fuente (LFT, LISR, LFD, leyes estatales) |
| Bloqueado / sin verificar | Portal caído o sin fuente pública / aún sin la revisión de la oleada 1 |

El detalle por MCP (estado, nota y tools) está en [`mcp-servers/CATALOGO.md`](mcp-servers/CATALOGO.md).

**Regla común:** ningún MCP devuelve datos simulados haciéndolos pasar por reales. Sin credenciales responde datos de ejemplo marcados `simulated: true`; con credenciales, cualquier error del proveedor se propaga como error tipado (`AuthError`, `UpstreamError`, `NotFoundError`…). `PLUGINS_MX_MOCK=1` fuerza el modo de ejemplo.

---

## Inicio rápido

### Instalar plugins en Claude Code

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX      # base de todos los verticales
/plugin install freelancers-mx --marketplace elimorals/Skills_MX   # o cualquier vertical de la lista
```

`core-mexico` (CFDI, IVA y retenciones, RFC, MXN, LFPDPPP, WhatsApp) es la dependencia de todos los verticales. Los MCPs que trae cada plugin se descargan solos la primera vez con [`uv`](https://docs.astral.sh/uv/), que es el único requisito además de Claude Code.

### Usar un MCP suelto

Cada MCP trae un `example.mcp.json` listo para copiar; no depende de dónde esté el repo. Por ejemplo, para el portal del SAT:

```json
{
  "mcpServers": {
    "sat_portal": {
      "command": "uv",
      "args": ["run", "--no-project", "--quiet", "--with",
               "plugins-mx-mcp-servers[sat-ws,sat-portal] @ git+https://github.com/elimorals/Skills_MX@main#subdirectory=mcp-servers",
               "python", "-m", "mp_sat_portal.server"],
      "env": {
        "SAT_RFC": "${SAT_RFC:-}",
        "SAT_EFIRMA_CERT": "${SAT_EFIRMA_CERT:-}",
        "SAT_EFIRMA_KEY": "${SAT_EFIRMA_KEY:-}",
        "SAT_EFIRMA_PASSWORD": "${SAT_EFIRMA_PASSWORD:-}"
      }
    }
  }
}
```

### Desarrollo

```bash
git clone https://github.com/elimorals/Skills_MX && cd Skills_MX/mcp-servers
uv venv .venv --python 3.12
uv pip install -e ".[dev]"            # agrega extras según lo que toques (ver abajo)
.venv/bin/pytest -q                   # 1,900 tests, sin red
```

| Extra | Para qué |
|---|---|
| `sat-ws`, `sat-portal` | Descarga masiva y portal SAT con e.firma |
| `publicos-federales`, `publicos-federales-2` | Portales federales (TLS incompleto, Playwright para CONAMER) |
| `estatal-centro`, `estatal-resto` | Predial genérico con Playwright, tarifas de gas en PDF |
| `sat-playwright` | Ruta Playwright heredada del portal SAT |

---

## Cómo está organizado

```
Skills_MX/
├── .claude-plugin/           marketplace.json con los 40 plugins (scripts/generar-marketplace.py)
├── _shared/                  6 skills base (fuente de verdad), se copian a cada plugin
├── core-mexico/              Plugin base: CFDI, IVA, RFC, MXN, LFPDPPP, WhatsApp + 8 workflows
├── <vertical>-mx/            39 plugins por industria
│   ├── .claude-plugin/       plugin.json
│   ├── skills/               SKILL.md + references/
│   ├── commands/             comandos /<plugin>:<comando>
│   ├── agents/               agentes y workflows en markdown
│   ├── workflows/            *.workflow.js ejecutables
│   └── .mcp.json             MCPs que usa el vertical
├── mcp-servers/              83 MCPs (mp_*) + shared/ (cache, bitácora, errores, handoff, solver)
├── webhooks/                 Receptor FastAPI (HMAC, Bearer, allowlist, idempotencia, audit JSONL)
├── evals/                    Triggering por skill, golden deterministas y promptfoo
├── tests/fixtures/           Casos de regresión por skill
├── schemas/                  JSON Schemas de salida
├── scripts/                  Sync de _shared, lint, generador de estado, crons, hooks
├── website/                  Sitio público (Vercel), generado en parte por scripts/
└── docs/                     Arquitectura, guías, integraciones, ADRs, historial
```

**Cómo se conectan las piezas:** una skill sabe *qué* hacer (reglas fiscales, plantillas, flujos). Un MCP *hace* la consulta real (SAT, Banxico, municipios, pasarelas). Un workflow orquesta varias skills y MCPs para un proceso completo (p. ej. emitir CFDI tras un pago). Los hooks validan antes de acciones sensibles, como timbrar o enviar WhatsApp masivo.

---

## Plugins verticales

| Sector | Plugins |
|---|---|
| **Base** | `core-mexico` |
| **Fiscal y contable** | `pf-anual-mx` (declaración anual PF) · `despacho-contable-mx` (contabilidad multi-cliente) · `nomina-pymes-mx` (nómina, IMSS-IDSE, INFONAVIT) · `cripto-fiscal-mx` (ISR de cripto) · `donatarias-ongs-mx` (CFDI de donativos, transparencia) · `sucesion-empresa-familiar-mx` (patrimonio y sucesión) · `crowdfunding-itf-mx` (inversionistas en IFC) |
| **Comercio** | `ecommerce-mx` (Mercado Libre, Shopify, Amazon) · `tienda-omnicanal-mx` (inventario multicanal) · `restaurante-mx` (restaurantes, dark kitchens, delivery) · `importadores-mx` (IGI, DTA, pedimentos) · `agencia-marketing-mx` (reportes y copy para clientes) |
| **Servicios profesionales** | `freelancers-mx` (cotizaciones, honorarios, RESICO) · `despacho-legal-mx` (honorarios y contratos) · `notarias-mx` (citas, escrituras) · `agente-seguros-mx` (cartera de pólizas, CNSF) |
| **Salud** | `clinica-salud-mx` · `consultorio-especialista-mx` · `telemedicina-mx` · `psicoterapia-mx` · `laboratorio-clinico-mx` · `geriatria-cuidado-mayor-mx` · `veterinaria-mx` · `paciente-mx` · `gmm-asegurado-mx` |
| **Inmobiliario y construcción** | `inmobiliaria-mx` (corredores) · `arrendador-residencial-mx` (rentas PF) · `airbnb-host-mx` (renta corta, ISH) · `constructora-mx` (obra, REPSE) |
| **Educación** | `colegios-mx` (K-12, colegiaturas deducibles) · `educacion-particular-b2c-mx` (cursos en línea) |
| **Servicios personales y eventos** | `salon-mx` (salones, spas, barberías) · `wedding-mx` (wedding planners) · `talleres-mx` (talleres mecánicos) |
| **Vehículos y movilidad** | `tramites-vehiculares-mx` (tenencia, verificación, multas) · `conductor-plataforma-mx` (Uber, DiDi, Cabify) |
| **Hogar, energía y trámites** | `servicios-publicos-mx` (CFE, agua, predial, gas) · `energia-solar-pyme-mx` (interconexión CFE) · `migracion-extranjeros-mx` (trámites INM) |

### Workflows ejecutables

| Plugin | Workflows |
|---|---|
| `core-mexico` | cfdi-emision-completa · emitir-cfdi-tras-pago · pago-conciliacion · cierre-fiscal-mensual · auditoria-fiscal-mensual · declaracion-resico-mensual · due-diligence-cliente · validacion-cfdis-historico |
| `freelancers-mx` | cobranza-multinivel · migracion-rfc-a-otro-regimen |
| `inmobiliaria-mx` | cobranza-renta-mensual · cartera-predial-multi-municipio |
| `cripto-fiscal-mx` | declaracion-anual-cripto · cripto-cierre-anual |
| `agencia-marketing-mx` | reporte-cliente-agencia · respuesta-crisis-cm |
| Otros | pf-anual-completa · dispersion-nomina · sync-multicanal · comunicacion-padres-masiva · garantia-vehicular · monitoreo-diario-vehicular · telemedicina-consulta · donativo-anual · pedimento-importacion · energia-bidireccional-mensual |

---

## MCP servers

Están en `mcp-servers/mp_*`. Por fuente:

| Grupo | MCPs | Cómo obtienen el dato |
|---|---|---|
| **SAT** | `sat_ws`, `sat_portal`, `sat_opinion_32d`, `resico_sat`, `donatarias_sat` | Web service de Descarga Masiva (XMLDSig), `ConsultaCFDIService`, login con e.firma por HTTP, listas 69/69-B y padrón de donatarias oficiales |
| **Federales** | `banxico`, `banxico_cep`, `clabe_validador_oficial`, `repse_stps`, `condusef_sipres`, `dof_api`, `cnbv_fintech`, `impi_marcanet`, `conagua_repda`, `cre_hidrocarburos`, `concilianet_profeco`, `llave_mx`, `retys_catalogo` y más | API o endpoint público detrás de cada portal |
| **Con CAPTCHA** | `curp_renapo`, `repuve`, `sep_profesional`, `ine_verificacion` | Entrega a humano o solver opt-in (ver abajo) |
| **Estatal y municipal** | `cdmx_municipal`, `edomex_municipal`, `queretaro_municipal`, `monterrey_municipal`, `guadalajara_municipal`, `puebla_municipal`, `predial_mx`, `agua_mx`, `gas_natural_mx`, `multas_mx`, `tenencia_mx`, `isn_mx`, `ish_mx`… | Consulta pública por cuenta o placa; tasas citadas a la ley estatal 2026 |
| **APIs privadas** | `mercado_pago`, `conekta`, `mercado_libre`, `shopify_mx`, `amazon_mx_seller`, `paypal_mx`, `clip_terminal`, `cabify_business`, `rappi_partners`, `facturama_extendido`, `bitso` | Cliente contra la documentación oficial de cada proveedor |
| **Cumplimiento normativo** | `ley_silla_nom037`, `desconexion_digital`, `expediente_clinico_nom024`, `cfe_interconexion_solar`, `lnetb_auditor` | Cálculo local con fundamento legal citado |
| **Pendientes (login de usuario)** | `imss_patronal`, `infonavit_patronal`, `bancos_mx`, `buro_credito_personal`, `cfe_facturacion`, `telmex_facturacion` | Requieren credenciales de prueba y captura del flujo (ver Pendientes) |

Utilidades compartidas en `mcp-servers/shared/`: `portal_handoff.py` (entrega a humano con formato único), `captcha_solver.py`, `errors.py` (errores tipados), `bitacora.py` (JSONL con hash de datos sensibles), `cache.py`, `mock.py`.

---

## Configuración y credenciales

Las credenciales van en variables de entorno, nunca en el repo. `.env.example` lista todas.

| Variable | Uso |
|---|---|
| `PLUGINS_MX_MOCK=1` | Fuerza datos de ejemplo (`simulated: true`) en todos los MCPs |
| `PLUGINS_MX_LIVE=1` | Habilita los tests `@pytest.mark.live` contra portales reales |
| `SAT_RFC`, `SAT_EFIRMA_CERT`, `SAT_EFIRMA_KEY`, `SAT_EFIRMA_PASSWORD` | e.firma para el SAT (rutas a `.cer` y `.key` fuera del repo) |
| `BANXICO_TOKEN` | SIE de Banxico (token gratuito) |
| `MERCADOPAGO_ACCESS_TOKEN`, `CONEKTA_API_KEY`, `FACTURAMA_USER`/`PASSWORD`… | Una por proveedor; cada `example.mcp.json` dice cuáles usa |
| `PLUGINS_MX_CAPTCHA_SOLVER`, `TWOCAPTCHA_API_KEY` | Solver de CAPTCHA opt-in |

El `.gitignore` bloquea `.env*`, `*.cer`, `*.key`, `*.pem`, `*.p12`, `*.pfx`, `*password*.txt` y `*contraseña*`.

---

## Solver de CAPTCHA (opt-in)

`mcp-servers/shared/captcha_solver.py` resuelve CAPTCHA con 2captcha. Si falla un captcha de imagen y hay `ANTHROPIC_API_KEY`, usa visión como respaldo. **Está apagado por defecto**: sin la configuración, cada portal devuelve la entrega a humano.

```bash
export PLUGINS_MX_CAPTCHA_SOLVER=2captcha
export TWOCAPTCHA_API_KEY=...          # tu llave
```

| Tipo | Portales conectados |
|---|---|
| Imagen | SAF CDMX (tenencia, verificación, multas), predial Puebla |
| reCAPTCHA v2 / v3 / Enterprise | Cédula SEP, REPUVE, predial Guadalajara, adeudos Jalisco, multas San Pedro, CURP |
| Turnstile | Multas EdoMex |

- **No evade anti-bots de red.** CURP (Akamai), INE (Cloudflare) y Mérida (Radware) bloquean antes del CAPTCHA. Ahí el tool detecta el bloqueo y entrega la consulta a humano sin gastar CAPTCHA.
- **Excluidos por diseño:** `citas_monitor` (apartar citas automáticamente le quita lugar a otras personas) y REPEP (anti-bot deliberado).
- **Sin validar en vivo todavía:** los portales con solver necesitan una llave para la primera prueba real.

---

## Calidad y pruebas

```bash
cd mcp-servers && .venv/bin/pytest -q                       # unitarios, sin red
PLUGINS_MX_LIVE=1 .venv/bin/pytest -q -m live <ruta>       # contra el portal real
python3 scripts/eval-golden.py                              # cálculos fiscales deterministas
bash scripts/lint-skills.sh                                 # frontmatter y reglas de SKILL.md
python3 scripts/generar-estado-mcps.py --check              # el sitio y este README están al día
python3 scripts/generar-marketplace.py --check              # marketplace al día con los plugin.json
python3 scripts/mcp-config-portable.py --check              # configs MCP sin rutas locales ni mock forzado
claude plugin validate .                                    # valida marketplace y plugins
npx promptfoo@0.124.1 eval -c evals/promptfoo/promptfooconfig.yaml   # evals LLM (requiere API key)
```

En cada PR, el CI corre los tests de los MCPs, las evals golden, el lint de skills, la verificación de copias de `_shared`, SkillSpector (análisis estático), la validación de JSON y el escaneo de secretos.

Los tests que necesitan e.firma generan una autofirmada al vuelo. Las comparaciones byte a byte contra phpcfdi usan la e.firma de prueba del SAT desde `SAT_EFIRMA_PRUEBA_DIR`, que vive fuera del repo.

---

## Seguridad y cumplimiento

- **Validación experta antes de producción.** Las skills fiscales las debe revisar un contador; los contratos, un abogado; las plantillas de WhatsApp, Meta.
- **Tasas estatales.** Varias tasas (ISN, ISH, tenencia) vienen de fuentes secundarias de 2026 y están marcadas con su nivel de confianza en cada README.
- **Datos personales.** La bitácora guarda solo hashes de RFC, CURP y correo. CURP e INE no cachean resultados e incluyen un aviso LFPDPPP.
- **Buró de crédito.** `mp_buro_credito_personal` exige el token de autorización del titular: consultar sin ella es delito.
- **Escrituras ante el SAT** (actualizar obligaciones, citas): no se automatizan.
- **Repo público.** No se commitean credenciales ni capturas de navegador. Detalles en [`docs/architecture/seguridad.md`](docs/architecture/seguridad.md).

---

## Pendientes

| Tema | Qué falta |
|---|---|
| **Login de usuario final** | IMSS, INFONAVIT, bancos, Buró, CFE y Telmex necesitan credenciales de prueba y una captura (HAR) de cada flujo para pasarlos a real |
| **Validación en vivo** | Las APIs privadas y los portales con solver necesitan credenciales o llave para su primera prueba real |
| **11 MCPs sin "Estado real"** | Los del grupo de login más `aspel_contpaqi` y `softrestaurant` (software local) |
| **Verticales con lógica profunda** | Varios verticales tienen skills de estructura sin cálculo propio |
El plan por grupos está en [`docs/plan-mock-a-real.md`](docs/plan-mock-a-real.md).

---

## Documentación

| Documento | Contenido |
|---|---|
| [`docs/INDEX.md`](docs/INDEX.md) | Índice general |
| [`docs/architecture/arquitectura.md`](docs/architecture/arquitectura.md) | Modelo `_shared/` + verticales |
| [`docs/plan-mock-a-real.md`](docs/plan-mock-a-real.md) | Plan y grupos de la migración a datos reales |
| [`mcp-servers/CATALOGO.md`](mcp-servers/CATALOGO.md) | Estado y tools de cada MCP |
| [`docs/guides/`](docs/guides/) | Instalación, desarrollo y guías por vertical |
| [`docs/integrations/`](docs/integrations/) | PAC (Facturama), pagos, WhatsApp |
| [`docs/reference/`](docs/reference/) | Glosario fiscal, glosario técnico, FAQ |
| [`docs/adrs/`](docs/adrs/) | Decisiones de arquitectura |
| [`docs/historial/`](docs/historial/) | Bitácora de sprints de junio 2026 (cifras históricas, no vigentes) |

---

## Licencia

[Apache-2.0](LICENSE) · Elías Rashid Morales Mendoza · [github.com/elimorals/Skills_MX](https://github.com/elimorals/Skills_MX)
