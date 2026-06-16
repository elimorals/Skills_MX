# Sprints E → F → G → H · Resumen ejecutivo

**Fecha**: 2026-06-15 (sesión continua)
**Autor**: Elías Rashid Morales Mendoza
**Estado final**: 83 MCPs · 1,667 tests pasando · 28 workflows

---

## TL;DR — Crecimiento del repo en una sesión

| Métrica | Antes (post-Sprint D) | Después (post-Sprint H) | Δ |
|---|---|---|---|
| **MCPs totales** | 62 | **83** | +21 |
| **Tests pytest** | 1,380 ✅ | **1,667 ✅** | +287 |
| **Tools nuevos** | — | ~95 | +95 |
| **Workflows ejecutables** | 24 | **28** | +4 (1 demo HITL · 3 v2 resumables) |
| **Páginas comerciales website** | 0 | **2** (`/precios/` + `/onboarding/`) | +2 |
| **Documentos SETUP_PLAYWRIGHT_REAL** | 1 (SAT) | **3** (SAT + IMSS + INFONAVIT) | +2 |
| **Commits en main** | — | **7** | feat × 5 + docs × 2 |

### Hitos commerciales

- `/precios/` con 3 tiers (Piloto $45k · Producción $18k/mes · Empresarial cotizar)
- `/onboarding/` con timeline 4 semanas + lista de credenciales
- SOW template firmable `website/assets/sow-piloto-30dias.md`
- Path real Playwright opt-in B2B para SAT/IMSS/INFONAVIT (3 docs SETUP)
- Workflow demo vendible `declaracion-resico-mensual.workflow.js` con HITL WhatsApp

---

## Sprint E — Bloqueadores normativos 2026 (14 MCPs)

Implementó los 15 gaps del Top 15 del plan original `plugins-mx-gaps-integraciones-2026-06-15.md` (12 nuevos + 3 profundizados).

### Tier P0 — Multas vigentes 2026

| MCP | Universo | Multa que evita |
|---|---|---|
| `mp_ley_silla_nom037` | 4M empresas con trabajadores | $282k–$586k MXN (STPS) |
| `mp_expediente_clinico_nom024` | 70k médicos + clínicas privadas | DOF 15-ene-2026 obligatorio |
| `mp_resico_sat` | 2.5M PF RESICO | Expulsión automática SCJN 2026 |

### Tier P1 — Identidad ciudadana + servicios públicos

| MCP | Validación |
|---|---|
| `mp_llave_mx` | ✅ **OAuth2 validado vivo** `llave.gob.mx/oauthV2.xhtml` |
| `mp_ine_verificacion` | ✅ Portal informativo confirmado (B2G vía convenio) |
| `mp_cfe_interconexion_solar` | Factor exportación 0.70 (cambio 2026) |
| `mp_conagua_repda` | LFD zonas 1-9 ($27.50-$0.62/m³) |
| `mp_desconexion_digital` | Reforma LFT Art. 132 marzo 2026 |

### Tier P2+P3 — Consumidor + uso suelo + tracker

| MCP | Notas |
|---|---|
| `mp_cofepris_aviso_funcionamiento` | 19 giros A/B/C (NOM-167-SSA1) |
| `mp_repep_profeco` | Filtro lote ≤5000 tels |
| `mp_concilianet_profeco` | 32 proveedores convenio |
| `mp_cre_hidrocarburos` | Anexo 30 (75,714 L/mes) |
| `mp_sedatu_uso_suelo` | 6 trámites + MIA/EIU/MIV >10k m² |
| `mp_simplifica_ciudadano` | Tracker LNETB 32 estados |

**Total Sprint E**: 14 MCPs + 134 tests + 3 commits.

---

## Sprint F — Profundización SAT + IMSS + INFONAVIT (14 tools)

Cubrió la sección 3 del plan original (gaps de profundización en MCPs existentes).

### `mp_sat_portal` — 5 tools nuevos

| Tool | Tests |
|---|---|
| `sat_calendario_fiscal_por_regimen` | 5 |
| `sat_cfdi_prevalidar` (local, 10 elementos CFDI 4.0) | 5 |
| `sat_declaraciones_historico` (alerta RESICO 3 omisiones) | 3 |
| `sat_devolucion_estatus` (Forma 41/14, 6 fases) | 3 |
| `sat_buzon_tributario_resumen` (Art. 17-K CFF) | 2 |

### `mp_imss_patronal` — 5 tools nuevos

| Tool | Implementación |
|---|---|
| `imss_sbc_calcular` | Factor integración + tope 25 UMAs ($2,826.75/d 2026) |
| `imss_ema_vs_eba_diferencias` | DIFERENCIA_CUOTAS / MOV_NO_APLICADO / INTERESES_MORA |
| `imss_calendario_obligaciones` | 12 mensuales + 6 bimestrales + anual RT |
| `imss_simulador_costo_patronal` | 9 cuotas LSS + INFONAVIT + provisiones LFT |
| `imss_riesgo_trabajo_prima_cambio` | Fórmula Art. 72 LSS + tope ±1% Art. 74 |

### `mp_infonavit_patronal` — 4 tools nuevos

| Tool | Implementación |
|---|---|
| `infonavit_descuento_calcular` | 5 tipos crédito + cap LFT Art. 110 (30% SBC) |
| `infonavit_creditos_sin_reporte` | Intereses moratorios 1.8%/mes estimados |
| `infonavit_emis_historico` | Hasta 10 años bimestral |
| `infonavit_conciliacion_nomina` | Hasta 5000 registros · diff por trabajador |

**Total Sprint F**: 14 tools · 51 tests · +1,909 líneas.

---

## Sprint G — 5 productos B2G gobierno

Diseñados a partir del research profundo de civica.digital + agenda ATDT + dolor ciudadano.

| MCP | Comprador objetivo | Tests |
|---|---|---|
| `mp_llave_mx_tracker` | ATDT (José Merino) · IMCO · México Evalúa | ✅ 11 |
| `mp_retys_catalogo` | CONAMER + datos.gob.mx (Sistema Ajolote) | ✅ 11 |
| `mp_lnetb_auditor` | IMCO + México Evalúa + prensa | ✅ 12 |
| `mp_portales_monitor` | Estados rezagados (Oax/Chis/Gro/Tab) | ✅ 13 |
| `mp_imss_continuidad` | IMSS directo o integradora primaria | ✅ 11 |

### Discovery Playwright en vivo (Sprint G)

- ✅ `catalogonacional.gob.mx` (CONAMER): ASP.NET + AntiForgeryToken + `#txtSearch` + `#btnSearch` + `#selectDependencias-selectized`
- ✅ `gob.mx/tramites`: enlaces top demanda confirmados (SAT CSF, IMSS semanas)
- ✅ `llave.gob.mx/oauthV2.xhtml`: heredado Sprint E

### Diferenciador comprobado

Civica Digital usa Ruby/Elixir/Python pero **NO tiene browser automation gob.mx**. Codeando México, SocialTIC, OPI Analytics hacen data/análisis pero NO operación de portales. Los 5 MCPs Sprint G son infraestructura de **operación** que complementa civic-tech UI/SaaS (URBEM en particular).

**Total Sprint G**: 5 MCPs · 58 tests · 36 archivos · +2,390 líneas.

---

## Sprint H — Nivel 2: preparación documental + workflow demo HITL

Implementa el "Nivel 2 — Preparación + Asistencia" del análisis de automatización trámites MX.

### `mp_form_filler_public` (17 tests)

8 formularios públicos gob.mx sin login con selectores validados:

| Formulario | CAPTCHA |
|---|---|
| SAT padrón / Verifica CFDI | imagen |
| REPSE STPS · REPEP PROFECO · Buró Comercial · SAT 32-D | sin captcha |
| REPUVE · CURP RENAPO | imagen / reCAPTCHA v2 |

Pre-flight con regex MX (RFC/CURP/NSS/placa/teléfono). NUNCA bypasea CAPTCHAs — marca `requiere_intervencion_humana=True`.

### `mp_citas_monitor` (16 tests) — ÉTICO

Monitor de cupos SAT/IMSS/SRE/INE que se diferencia del mercado negro:

| Mercado negro | mp_citas_monitor |
|---|---|
| Acapara y revende ($1k/cita SAT) | Alerta al titular, no reserva |
| Polling ~5s | Throttling mínimo 60s |
| Sin consentimiento | `consent_token` vinculado a CURP |
| Sin trazabilidad | Bitácora hasheada LFPDPPP |

### Workflow `declaracion-resico-mensual.workflow.js`

Orquesta 6 MCPs end-to-end con human-in-loop por WhatsApp:

1. `mp_sat_portal.consultar_padron` → verifica régimen RESICO
2. `mp_resico_sat.evaluar_estatus` → alerta SCJN 2026 (3 omisiones)
3. `mp_resico_sat.calcular_isr` + `retencion_plataforma` → ISR neto
4. `mp_sat_portal.calendario_fiscal` → pre-validación periodo
5. `mp_clabe_validador_oficial` → verifica CLABE Banxico
6. HITL WhatsApp → autorización del titular (24h timeout)

**Métricas comerciales declaradas en el workflow**:
- Universo: ~2.5M PF RESICO
- Tiempo: 4 min vs 2h manual
- Precio: $99-149 MXN B2C / $18k/mes B2B contador
- Cobertura legal: CFF Art. 17-D + LFPDPPP Art. 13

**Total Sprint H**: 2 MCPs + 1 workflow · 33 tests · +1,576 líneas.

---

## Resumen comercial post-sesión

### Tiers que se pueden cotizar HOY

| Tier | Producto | Precio | Estado |
|---|---|---|---|
| **B2C puntual** | Buzón SAT bot WhatsApp | $49 MXN/mes | MCP listo |
| **B2C puntual** | Devolución SAT tracker | $99 MXN único | MCP listo |
| **B2C puntual** | Calculadora plataformas (Uber/Rappi/Airbnb) | Free + upsell | MCP listo |
| **B2C suscripción** | Cita SAT ética con consent_token | $99-149 MXN/mes | MCP listo |
| **B2B piloto** | Implementación 30 días vertical | $45,000 MXN único | `/precios/` |
| **B2B producción** | 15 MCPs + workflows + SLA | $18,000 MXN/mes | `/precios/` |
| **B2B empresarial** | 83 MCPs + on-prem + SLA 99.9% | $180,000+ MXN/mes | `/precios/` |
| **B2G** | Pilotos LNETB + Llave MX Tracker para think tank | Variable | Sprint G |
| **B2G MIPYME** | Monitor portales gob.mx vía ComprasMX | Variable | Sprint G |

### Próximos pasos no codificables (capa 3)

1. **Conseguir primer piloto pagante** ($45k MXN) con despacho contable o inmobiliaria
2. **Contactar Cívica Digital** vía programa Partners — caso conjunto con Agencia Digital BC
3. **Registrarse en ComprasMX + FIRA MIPYMEs + mipymes.economia.gob.mx**
4. **Email outbound** a 5-10 despachos contables CDMX con link a `/precios/`
5. **Lanzar 1 producto B2C gratuito** (Predial Reminder enero) para construir base WhatsApp 10k personas

### Fuentes del research que originó Sprint E/G/H

- Plan original: `/Users/elias/Downloads/plugins-mx-gaps-integraciones-2026-06-15.md`
- Research civica.digital: agente general-purpose 2026-06-15 (perfil verificable)
- Research gobierno MX 2026: agente general-purpose 2026-06-15 (ATDT + LNETB + ComprasMX + PEF)
- Research dolor ciudadano B2C: agente general-purpose 2026-06-15 (Coparmex SAT + INFONAVIT + Heru/Konta)

---

## Archivos clave producidos esta sesión

```
mcp-servers/
├── CATALOGO.md                                    # Catálogo central actualizado a 83 MCPs
├── mp_ley_silla_nom037/                          # Sprint E.1
├── mp_expediente_clinico_nom024/                 # Sprint E.1
├── mp_resico_sat/                                # Sprint E.1
├── mp_llave_mx/                                  # Sprint E.2 (✅ validado vivo)
├── mp_ine_verificacion/                          # Sprint E.2
├── mp_cfe_interconexion_solar/                   # Sprint E.2
├── mp_conagua_repda/                             # Sprint E.2
├── mp_desconexion_digital/                       # Sprint E.2
├── mp_cofepris_aviso_funcionamiento/             # Sprint E.3
├── mp_repep_profeco/                             # Sprint E.3
├── mp_concilianet_profeco/                       # Sprint E.3
├── mp_cre_hidrocarburos/                         # Sprint E.3
├── mp_sedatu_uso_suelo/                          # Sprint E.4
├── mp_simplifica_ciudadano/                      # Sprint E.4
├── mp_llave_mx_tracker/                          # Sprint G
├── mp_retys_catalogo/                            # Sprint G
├── mp_lnetb_auditor/                             # Sprint G
├── mp_portales_monitor/                          # Sprint G
├── mp_imss_continuidad/                          # Sprint G
├── mp_form_filler_public/                        # Sprint H
├── mp_citas_monitor/                             # Sprint H
├── mp_sat_portal/SETUP_PLAYWRIGHT_REAL.md        # actualizado Sprint F
├── mp_imss_patronal/SETUP_PLAYWRIGHT_REAL.md     # nuevo Sprint F
├── mp_infonavit_patronal/SETUP_PLAYWRIGHT_REAL.md # nuevo Sprint F
└── shared/playwright_stub.py                     # +respuesta_real_no_implementada()

core-mexico/workflows/
└── declaracion-resico-mensual.workflow.js        # Sprint H — demo HITL vendible

website/
├── precios/index.html                            # Pricing 3 tiers + FAQ + JSON-LD
├── onboarding/index.html                         # Timeline 4 semanas piloto
├── data/skills-catalog.json                      # v1.1.0 — 76 → ahora 83
└── assets/sow-piloto-30dias.md                   # Template firmable
```

---

## Comparativa con plan original

El plan `plugins-mx-gaps-integraciones-2026-06-15.md` planteó:

- **Tier P0** (3 MCPs · ~30h) — bloqueadores 2026 ✅ implementado
- **Tier P1** (5 MCPs · ~40h) — identidad + servicios extendidos ✅ implementado
- **Tier P2** (4 MCPs · ~28h) — consumidor + giros COFEPRIS ✅ implementado
- **Tier P3** (3 MCPs · ~22h) — uso suelo + Simplifica + profundizar SAT/IMSS/INFONAVIT ✅ implementado

**Esfuerzo planeado**: ~120h (12 semanas a 10h/sem o sprint intensivo de 3 semanas)
**Esfuerzo real ejecutado**: 1 sesión continua (mayoritariamente con agente, sin equipo)

### Productos B2G extra (no estaban en el plan original)

Sprint G agregó 5 productos para civic-tech (`mp_llave_mx_tracker` etc.) que no figuraban en el plan original — surgieron del research profundo de civica.digital + agenda ATDT.

### Productos Nivel 2 extra (no estaban en el plan original)

Sprint H agregó 2 MCPs + 1 workflow para automatización ética de trámites — surgieron de la conversación sobre niveles de viabilidad legal de automatización en MX.
