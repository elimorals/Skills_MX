# Trámites/APIs mexicanas NO implementadas — Reporte ejecutivo 2026-06-14

> Investigación deep research con 4 agentes paralelos (federal, estatal, sectorial, B2B SaaS) sobre qué pueden automatizar otros MCPs **que no existan ya** en `mcp-servers/`. Resultado: **80+ trámites/APIs identificadas, 18 priorizadas como Tier 1 + Tier 2**.

---

## TL;DR — Top 15 priorizado para ejecución

Orden por (valor × universo de empresas afectadas) / esfuerzo:

| # | MCP propuesto | Por qué importa | Esfuerzo | Captcha |
|---|---|---|---|---|
| 1 | **`mp_repse_stps`** | Subcontratación obligatoria Art. 15 LFT. Universo: cualquier empresa B2B que contrate servicios. Compliance laboral universal. | Bajo | No |
| 2 | **`mp_sat_opinion_32d`** | "Sin opinión 32-D no contratas con nadie". Universo: todo proveedor B2B/B2G. | Medio | No (público) |
| 3 | **`mp_isn_mx`** (multi-estado) | Impuesto sobre nómina estatal. Universo: TODA empresa con trabajadores. Empezar CDMX+JAL+NL+EdoMex. | Medio-alto | Variable |
| 4 | **`mp_whatsapp_business`** | Canal de mensajería #1 B2C/B2B MX. Universo: todos los verticales. | Medio | No (Meta token) |
| 5 | **`mp_repuve`** | Consulta NIV/placa robados. Universo: agente-seguros, conductor-plataforma, leasing, kavak-like. | Medio | reCAPTCHA v2 |
| 6 | **`mp_dof_api`** | Monitoreo legal continuo. Hay base open-source de IMCO (`github.com/imco/dof-api`). Universo: despacho-legal, compliance horizontal. | Bajo | No |
| 7 | **`mp_impi_marcanet`** | Búsqueda fonética de marcas (público gratis). Universo: legaltech, agencias, startups, marketplaces. | Bajo | No |
| 8 | **`mp_belvo_open_banking`** | Desbloquea ~12 bancos MX (Inbursa, BanCoppel, Compartamos, Banamex secundario) en un solo conector. | Medio | No |
| 9 | **`mp_sat_ws`** (o **`mp_finkok`**) | Bulk CFDI download + conciliación. Complementa Facturama. Universo: despacho-contable, ERPs. | Medio | No |
| 10 | **`mp_condusef_sipres`** | Padrón financiero MX (SOFOMes/fintech). Universo: agente-seguros, cripto-fiscal, KYC institucional. | Bajo | No |
| 11 | **`mp_cnbv_padron_fintech`** | ITF autorizadas Ley Fintech. Universo: cripto-fiscal, despacho-contable. | Bajo | No |
| 12 | **`mp_metamap`** | KYC nativo MX (CURP/INE/RFC/biometría). Universo: cualquier vertical con onboarding. | Medio | No |
| 13 | **`mp_skydropx`** + **`mp_99minutos`** | Multi-carrier MX completo. Universo: e-commerce, marketplaces. | Bajo | No |
| 14 | **`mp_no_antecedentes_penales_mx`** (CDMX + EdoMex) | Contratación masiva (RRHH, gig economy). Universo: conductor-plataforma, didi-partners, RRHH. | Medio | Llave CDMX SSO |
| 15 | **`mp_donatarias_sat`** | Padrón de donatarias autorizadas (público). Universo: donatarias-ongs, despacho-contable. | Bajo | No |

---

## Por dominio

### A. Federales (18 candidatos)

#### Tier 1 — Alto valor + bajo/medio esfuerzo

- **REPSE STPS** — `https://repse.stps.gob.mx/Publico` — Consulta por RFC, sin login.
- **SAT Opinión 32-D pública** — `https://ptsc32d.clouda.sat.gob.mx/ConsultaPublico` — Sin captcha si el contribuyente autorizó publicación.
- **SAT contribuyentes incumplidos** — `wwwmat.sat.gob.mx/consultas/11981/` y `/64171/` — Listas negras adicionales a 69/69-B.
- **CONDUSEF SIPRES** — Entidades financieras autorizadas. Crítico para KYC.
- **CNBV Padrón ITF** — Ley Fintech.
- **IMPI MARCANET** — Búsqueda de marcas.
- **PROFECO RCAL/RPCA** — Contratos de adhesión registrados (e-commerce/fintech obligados).
- **DOF API** — Hay base IMCO open-source.
- **CONAGUA REPDA** — Concesiones de agua (ASP.NET ViewState, fácil scraping).
- **COFEPRIS Visor** — 28 campos por medicamento, recién lanzado abr-2026.

#### Tier 2 — Alto valor + alto esfuerzo (e.firma/CAPTCHA)

- **SAT validación masiva RFC** — Hasta 5K registros.
- **SAT Padrón Importadores Sectorial** — Comercio exterior.
- **SE RUG** — Registro Único de Garantías Mobiliarias (fintech crédito).
- **VUCEM** — 10 dependencias en 1 punto. Muy alto valor para constructora/comex.
- **CompraNet (Compras MX)** — Licitaciones federales. Govtech.
- **CJF/PJF Sentencias** — Diferenciador para despacho-legal.
- **PNT Plataforma Nacional Transparencia** — Due diligence corporativo.
- **RNPDNO SEGOB** — Personas desaparecidas (KYC reforzado lavado de dinero).
- **SRE Apostilla** — Cita + validación (reCAPTCHA).

### B. Estatales (8 candidatos)

#### Tier 1 — ISN multi-estado (el "santo grial" estatal)

| Estado | Portal | Notas |
|---|---|---|
| CDMX | `dgtc.finanzas.cdmx.gob.mx` (SAC) | e.firma + captcha simple |
| Jalisco | `gobiernoenlinea1.jalisco.gob.mx/impuestos` | Sin captcha conocido |
| Nuevo León | `egobierno.nl.gob.mx/egob/Nomina.php` + `cfdi.nl.gob.mx` | 2 portales: pago + CFDI |
| EdoMex | `sfpya.edomexico.gob.mx/recaudacion` | Login REC + password |
| Querétaro | `asistenciaspf.queretaro.gob.mx` | Manual oficial PDF |
| Puebla/Guanajuato/Yucatán | SEFIN respectivas | Mismo patrón |
| BC | `www4.ebajacalifornia.gob.mx/Impuesto` | Java legacy |

Recomendación: skill `mp_isn_mx` con submódulos por estado, exponiendo `descargar_declaracion(estado, periodo, rfc)` y `obtener_linea_captura(...)`.

#### Tier 2 — Verticales específicos estatales

- **`mp_ish_mx`** (Impuesto Hospedaje) — CDMX 3.5%, QRoo 6%, Yucatán 3%, Jalisco 3%. Combo con `airbnb-host-mx`.
- **`mp_vehicular_estatal_mx`** — Tenencia + refrendo + reemplaca (EdoMex, Jal, Sonora 2026). Combo con flotillas.
- **`mp_no_antecedentes_penales_mx`** — CDMX + EdoMex 100% digitales con Llave SSO.
- **`mp_constancia_no_adeudo_estatal`** — Due diligence M&A (Tlaxcala, Chiapas, Michoacán, Sonora, CDMX).
- **`mp_catastro_estatal`** — IGECEM (EdoMex 125 muns), IRCEP (Puebla), Veracruz.

#### Despriorizado

- **Cédulas estatales**: Jalisco caída por SCJN (2024). Mercado fragmentado.
- **DIF/SEDESOL padrones**: opacos por LFPDPPP, riesgo regulatorio.

### C. Sectoriales (10 candidatos)

#### Por vertical existente

- **`telemedicina-mx` / `clinica-salud-mx`**: COFEPRIS DIGIPRiS (avisos funcionamiento), SINAVE SUAVE.
- **`despacho-legal-mx`**: CJF sentencias, PNT, PJEDF + PJEM (CDMX+EdoMex = 40% litigios).
- **`agente-seguros-mx`**: CONDUSEF SIPRES + REUNE/RECA, REPUVE para cotización.
- **`cripto-fiscal-mx`**: CNBV ITF, CONDUSEF SIPRES (validar exchanges/IFPE).
- **`colegios-mx`**: SIRVOES SEP (consulta RVOE).
- **`donatarias-ongs-mx`**: SAT directorio donatarias, CLUNI Bienestar.
- **`arrendador-residencial-mx` / `constructora-mx`**: Registros Públicos Propiedad estatales (CDMX prioritario).
- **`constructora-mx`**: RUV (Registro Único Vivienda) — INFONAVIT cuv consulta pública.

#### Verticales NUEVOS sugeridos (no existen en monorepo)

1. **`transportista-carga-mx`** — SICT autotransporte federal + REPUVE flotilla.
2. **`agroindustria-mx`** — SADER SURI + SENASICA fitosanitarios.
3. **`generador-distribuido-mx`** — CENACE PML + CRE + CFE bidireccional.
4. **`comercio-exterior-mx`** — VUCEM + Padrón Importadores SAT + COVE.

### D. B2B SaaS / APIs comerciales (40+ identificadas)

#### Tier 1 (todos críticos)

- **`mp_whatsapp_business`** — Cloud API Meta (#1 canal MX).
- **`mp_belvo`** — Open banking: cubre Inbursa, BanCoppel, Compartamos, Banamex secundario en 1 conector.
- **`mp_sat_ws` / `mp_finkok`** — Bulk CFDI + conciliación (complementa Facturama).
- **`mp_skydropx`** + **`mp_99minutos`** + **`mp_envia`** — Multi-carrier MX (envíos).
- **`mp_metamap`** — KYC LATAM nativo (CURP/INE/RFC/biometría).
- **`mp_hubspot`** — CRM B2B dominante en MX mid-market.
- **`mp_hsbc_mx`** — Único banco grande con API Open Banking pública.
- **`mp_vtex`** + **`mp_tienda_nube`** — Bases instaladas enormes.
- **`mp_walmart_marketplace_mx`** — Alto GMV, API madura.
- **`mp_worky`** + **`mp_runa_hr`** — Nómina PyMEs.
- **`mp_mercado_envios_flex`** — Reusa OAuth MELI existente.
- **`mp_proppit`** — Lamudi/Trovit/Mitula/Icasas en 1 conector (Lifull Connect).

#### Tier 2

- **`mp_truora`** — Background checks LATAM.
- **`mp_dhl_mx`** + **`mp_fedex_mx`** + **`mp_estafeta`** — Carriers internacionales.
- **`mp_prometeo`** — Open banking alternativo (LATAM).
- **`mp_palenca`** — Verificación nómina (scrap Runa/Worky).
- **`mp_banco_azteca_apilab`** — Partner-only pero alta penetración.
- **`mp_mailchimp`** / **`mp_activecampaign`** / **`mp_klaviyo`** — Marketing automation.

#### Skip list (bajo ROI o bloqueado)

- **Linio** (cerró 2023), **Sears MX/Privalia** (sin API pública robusta).
- **Crowdfunding** (Yotepresto/Doopla/Briq/Play Business) — todos sin REST públicas.
- **Stori/Klar/Albo/Konfío** — B2C closed.
- **Comparadores** (Coru, Comparaguru, KAYAK) — affiliate-only.
- **PandaPe/BambooHR/Workday** — APIs globales, mejor cubrir individualmente bajo demanda.
- **Receta electrónica federal** — no existe portal oficial nacional.

---

## Roadmap propuesto

### Sprint 1 (siguiente sesión, ~10-15h)
**Foco: compliance horizontal + canal masivo**
1. `mp_repse_stps` (1h) — público, sin captcha.
2. `mp_sat_opinion_32d` (3h) — público con autorización.
3. `mp_dof_api` (2h) — base IMCO open-source disponible.
4. `mp_donatarias_sat` (2h) — público.
5. `mp_whatsapp_business` (4h) — Meta Cloud API.

### Sprint 2 (~12h)
**Foco: ISN estatal + KYC**
6. `mp_isn_mx` (CDMX+JAL+NL+EdoMex) (8h) — el "santo grial" para `despacho-contable-mx`.
7. `mp_condusef_sipres` + `mp_cnbv_padron_fintech` (2h) — agente-seguros + cripto-fiscal.
8. `mp_metamap` (2h) — KYC universal.

### Sprint 3 (~10h)
**Foco: marketplaces + logística**
9. `mp_belvo` (3h) — desbloquea 12 bancos.
10. `mp_sat_ws` o `mp_finkok` (3h) — bulk CFDI.
11. `mp_skydropx` (2h) + `mp_99minutos` (2h) — envíos.

### Sprint 4 (~12h)
**Foco: nuevos verticales**
12. `mp_repuve` (4h) — resuelve reCAPTCHA una vez, lo monetizas siempre.
13. Vertical nuevo `transportista-carga-mx` (4h) — SICT + REPUVE.
14. Vertical nuevo `comercio-exterior-mx` (4h) — VUCEM.

### Tier diferido (no priorizar)
- VUCEM full (alto esfuerzo: 10 dependencias).
- CJF sentencias (alto esfuerzo, vertical único).
- Registros Públicos Propiedad estatales (33 portales distintos).

---

## Stats finales

| Métrica | Valor |
|---|---|
| Trámites/APIs investigados | 80+ |
| Tier 1 priorizado | 15 |
| Tier 2 | ~15 |
| Verticales nuevos sugeridos | 4 (transportista-carga, agroindustria, generador-distribuido, comercio-exterior) |
| Skip list (bajo ROI) | 12 |
| Esfuerzo total Sprint 1-4 | ~45h chat |
| Cobertura adicional estimada | +28 MCPs sobre los 43 actuales |

---

## Insight crítico de la investigación

El descubrimiento más relevante NO son los MCPs individuales, sino **3 patrones arquitectónicos**:

1. **Patrón Compliance Horizontal**: REPSE, 32-D, SIPRES, donatarias-SAT son consultas público-públicas (sin login) que **TODOS los verticales necesitan**. Conviene un módulo `shared/compliance_publico_mx.py` con función `validar_proveedor(rfc) → {repse, 32d, listas_69, donatarias_status, ...}`.

2. **Patrón ISN-multi-estado**: 32 portales con el mismo trámite. Es exactamente la situación predial pero con MUCHO más universo (toda empresa con nómina vs. solo propietarios de inmuebles). El catálogo central debe extenderse a `shared/catalogo_isn_estatal.py`.

3. **Patrón Aggregator API**: Belvo (12 bancos), Skydropx (5 carriers), Proppit (4 portales inmobiliarios), Finkok (CFDI bulk SAT). Un solo MCP que envuelve un aggregator vale ~5 MCPs individuales — ROI ~5x.

---

— Sesión 2026-06-14, FASE 57, deep research consolidado de 4 agentes paralelos
