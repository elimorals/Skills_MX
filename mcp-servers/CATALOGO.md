# Catálogo de MCPs — plugins-mx

**Última actualización**: 2026-06-15 (post-Sprint E)
**Total MCPs**: 76
**Tests pasando**: 1,514

Catálogo central de los 76 MCP servers del monorepo, organizados por **Tier de producción** y categoría. Cada MCP cumple el contrato mock-first: corre sin credenciales con respuestas plausibles marcadas `simulated: true`.

## Convención de Tier

| Tier | Definición | Criterios |
|---|---|---|
| **S** | Producción crítica | Path real implementado · 100% tests pasando · cobertura nacional alta · validación experta o portal estable >12 meses |
| **A** | Producción con human-in-loop | Path real con CAPTCHA/cookies/MFA · tests pasando · operativo bajo supervisión |
| **B** | Catálogo + mock-first | Discovery validado en vivo · selectores documentados · path real opt-in pero parser puede requerir calibración |
| **C** | Mock-only definitivo | Portal no expone consulta pública · solo app móvil o login-only · mantenido como referencia |

## Tabla maestra (76 MCPs)

### Tier S — Producción crítica (7)

| MCP | Categoría | Universo MX | Tests | Path real | Notas |
|---|---|---|---|---|---|
| `mp_banxico` | Federal financiero | Universal | ✅ | ✅ REST | TCs DOF + UMA + INPC + TIIE diario |
| `mp_facturama_extendido` | CFDI 4.0 | 5.5M PyMEs | ✅ | ✅ REST | Sandbox + producción |
| `mp_mercado_pago` | Pagos | Universal | ✅ | ✅ REST + HMAC | Webhooks idempotentes |
| `mp_mercado_libre` | Marketplace | 50k+ vendedores activos MX | ✅ | ✅ REST | Listings + órdenes + mensajes |
| `mp_curp_renapo` | Identidad | 130M habitantes | ✅ | ✅ Estructural + Playwright | CURP estructural real + RENAPO stub |
| `mp_banxico_cep` | SPEI | Universal | ✅ | ✅ REST/form-POST | CLABE + CEP |
| `mp_sat_opinion_32d` | Compliance fiscal | 5.5M PyMEs | ✅ | ✅ HTTP público | Opinión 32-D sin captcha |

### Tier A — Producción con human-in-loop (10)

| MCP | Categoría | Universo MX | Tests | Path real | Notas |
|---|---|---|---|---|---|
| `mp_cfe_facturacion` | Servicios públicos | 42M usuarios CFE | ✅ | ✅ Playwright + CAPTCHA + cookies | Human-in-loop CAPTCHA · sesión 30 min |
| `mp_telmex_facturacion` | Servicios públicos | 15M líneas Telmex | ✅ | ✅ Playwright + reCAPTCHA v3 invisible | `pago_sin_login` sin credenciales del usuario |
| `mp_verificacion_vehicular_mx` | Fiscal vehicular | 8M veh zonas verificación | ✅ | ✅ SAF CDMX calibrado | 7 estados · parser calibrado en vivo 2026-06-15 |
| `mp_agua_mx` | Servicios públicos | ~50% pob urbana | ✅ | ✅ SIAPA Playwright | 17 organismos · 2 públicos (JMAS Juárez + OOAPAS Morelia) |
| `mp_conekta` | Pagos | Universal | ✅ | ✅ REST | Charges + refunds + suscripciones |
| `mp_shopify_mx` | Marketplace | 30k tiendas | ✅ | ✅ REST | Wrapper específico MX |
| `mp_bitso` | Cripto | 4M cuentas | ✅ | ✅ REST | Calculadora ISR cripto |
| `mp_sep_profesional` | Validación profesional | Médicos/abogados/etc | ✅ | ✅ HTTP público | Sin captcha — desbloquea telemedicina-mx |
| `mp_repse_stps` | Compliance laboral | 4M empresas formales | ✅ | ✅ HTTP público | Art. 15 LFT subcontratación |
| `mp_dof_api` | Compliance horizontal | Despachos legales/contables | ✅ | ✅ HTTP público | Sumario diario + búsqueda full-text |

### Tier B — Catálogo + mock-first con discovery validado (33)

#### B.1 Fiscal estatal y vehicular (7)

| MCP | Categoría | Universo MX | Tests | Path real | Notas |
|---|---|---|---|---|---|
| `mp_tenencia_mx` | Fiscal vehicular | 40M vehículos | ✅ | Cálculo + tablas | 20 estados con tasa + factor depreciación |
| `mp_ish_mx` | Fiscal estatal | 100k anfitriones Airbnb | ✅ | Cálculo | ISH 32 estados (27 cobran, 5 sin) |
| `mp_isn_mx` | Fiscal estatal | 4M empresas formales | ✅ | 8 estados Playwright | 32 estados catalogados |
| `mp_multas_vehiculares_mx` | Fiscal vehicular | ~22M vehículos | ✅ | CDMX (SAF reusado) | 5 sistemas: CDMX + EdoMex + NL ICVNL + NL San Pedro + JAL |
| `mp_catastro_estatal_mx` | Inmobiliario | Notarías + peritos | ✅ | Mock | 10 sistemas — patrón nacional confirmado no-público |
| `mp_predial_mx` | Municipal | 35.2M hab (26.7% nacional) | ✅ | 71 muns Playwright validados | 243 muns catalogados |
| `mp_multas_mx` | Fiscal vehicular | 8 estados | ✅ | Mock + reCAPTCHA opt-in | Catálogo legacy |

#### B.2 Compliance y registros (7)

| MCP | Categoría | Universo MX | Tests | Path real | Notas |
|---|---|---|---|---|---|
| `mp_donatarias_sat` | Compliance fiscal | ~10k donatarias + donantes | ✅ | Mock + Akamai diferido | Anexo 14 RMF — CFDI uso D04 |
| `mp_cnbv_fintech` | Compliance regulatorio | Ecosistema fintech/cripto | ✅ | Mock + catálogo curado | ITF Ley Fintech (IFPE/IFC) |
| `mp_no_antecedentes_penales_mx` | Compliance identidad | Reclutamiento corporativo | ✅ | Playwright stub | Carta no antecedentes federal |
| `mp_repuve` | Compliance vehicular | 40M veh | ✅ | Playwright stub | Registro público vehicular |
| `mp_condusef_sipres` | Compliance financiero | Ecosistema financiero | ✅ | Playwright stub | SIPRES entidades financieras |
| `mp_impi_marcanet` | Propiedad intelectual | Marcas registradas | ✅ | Playwright stub | Marcanet IMPI |
| `mp_sat_ws` | Web Services SAT | CFDI emisores | ✅ | Stub + e.firma | Web Services oficiales |

#### B.3 Municipales individuales (8)

Refactorizados al catálogo central `shared/catalogo_municipios_mx.py`. Se mantienen por backward compat.

| MCP | Cobertura | Tests | Path real |
|---|---|---|---|
| `mp_cdmx_municipal` | CDMX 16 alcaldías | ✅ | Mock + validado |
| `mp_edomex_municipal` | EdoMex | ✅ | Mock |
| `mp_monterrey_municipal` | Monterrey | ✅ | Mock |
| `mp_guadalajara_municipal` | Guadalajara | ✅ | Mock |
| `mp_merida_municipal` | Mérida | ✅ | Playwright validado |
| `mp_puebla_municipal` | Puebla | ✅ | Mock |
| `mp_queretaro_municipal` | Querétaro | ✅ | Playwright validado |
| `mp_tijuana_municipal` | Tijuana | ✅ | Login-only (Sprint D) |

#### B.4 Marketplaces e inmobiliario (4)

| MCP | Categoría | Universo MX | Tests | Path real |
|---|---|---|---|---|
| `mp_amazon_mx_seller` | Marketplace | Sellers MX | ✅ | LWA + 6 endpoints |
| `mp_inmuebles24` | Inmobiliario | ~30k inmobiliarias | ✅ | Playwright real |
| `mp_vivanuncios` | Inmobiliario + autos | Multi-categoría | ✅ | Mock |
| `mp_buro_credito_personal` | Crédito personal | Reclutamiento + arrendamiento | ✅ | Mock + autorización Pydantic |

#### B.5 Pagos extendidos (4)

| MCP | Categoría | Tests | Path real |
|---|---|---|---|
| `mp_paypal_mx` | Pagos | ✅ | Mock + REST stub |
| `mp_klap` | POS alterno | ✅ | Mock |
| `mp_kueski` | Crédito BNPL | ✅ | Mock |
| `mp_trustly_mx` | Open banking | ✅ | Mock + REST stub |

#### B.6 SACPI y agregadores estatales (1)

| MCP | Cobertura | Tests | Path real |
|---|---|---|---|
| `mp_sacpi_michoacan` | 95 muns Michoacán | ✅ | Playwright real (95:1 ratio) |

#### B.7 Identidad bancaria (1)

| MCP | Categoría | Tests | Path real |
|---|---|---|---|
| `mp_clabe_validador_oficial` | CNBV reverso CLABE | ✅ | ✅ REST |

### Tier C — Mock-only definitivo (12)

Portales no exponen consulta pública. Mantenidos como referencia + scaffolding para clientes que tengan credenciales propias.

| MCP | Razón mock-only | Tests | Notas |
|---|---|---|---|
| `mp_imss_patronal` | IDSE requiere e.firma + MFA empresarial | ✅ | Cliente provee credenciales |
| `mp_infonavit_patronal` | Igual IMSS | ✅ | Cliente provee credenciales |
| `mp_bancos_mx` | BBVA/Banamex/Santander cierran scraping | ✅ | Esqueleto Playwright |
| `mp_gas_natural_mx` | Naturgy/ENGIE solo app móvil + WhatsApp | ✅ | Sprint C hallazgo negativo |
| `mp_sat_portal` | SAT bloquea bots agresivamente | ✅ | 4/11 HTTP públicos reales |
| `mp_aspel_contpaqi` | Solo CSV exports | ✅ | Parser sin API directa |
| `mp_softrestaurant` | Solo CSV exports | ✅ | Parser sin API directa |
| `mp_cabify_business` | API restringida a partners | ✅ | Cliente provee credenciales |
| `mp_didi_partners` | API restringida a partners | ✅ | Cliente provee credenciales |
| `mp_didi_food_partners` | API restringida a partners | ✅ | Cliente provee credenciales |
| `mp_rappi_partners` | API restringida a partners | ✅ | Cliente provee credenciales |
| `mp_uber_eats_partners` | API restringida a partners | ✅ | Cliente provee credenciales |

---

## Sprint E — 14 MCPs nuevos (Tier P0–P3 normativa 2026)

Lote agregado 2026-06-15 cubriendo bloqueadores normativos críticos para 2026 (Ley Silla NOM-037, RESICO, ECE NOM-024, desconexión digital), identidad ciudadana (Llave MX, INE), energía renovable (CFE solar, CRE), recursos naturales (CONAGUA), consumidor (PROFECO REPEP/Concilianet), urbano (SEDATU) y tracker de simplificación estatal.

### Tier A · Validado vivo Playwright (1)

| MCP | Categoría | Universo MX | Tests | Path real | Notas |
|---|---|---|---|---|---|
| `mp_llave_mx` | Identidad ciudadana | 130M habitantes | ✅ | ✅ OAuth2 form real | Validado `llave.gob.mx/oauthV2.xhtml` — selectores `frmLogin:txtCorreo`, `frmLogin:txtPassword`, sin captcha. JSF + PrimeFaces. 20 trámites catalogados (identidad/fiscal/salud/vivienda/etc.) |

### Tier B · Discovery validado parcialmente (4)

| MCP | Categoría | Universo MX | Tests | Path real | Notas |
|---|---|---|---|---|---|
| `mp_conagua_repda` | Recursos naturales | ~500k titulares | ✅ | Mock + REPDA público | Tarifa LFD 2026 por zona 1-9 ($27.50-$0.62/m³). Umbral medidor 150k m³/año |
| `mp_repep_profeco` | Consumidor | 130M habitantes | ✅ | Mock + portal público | Normalización teléfonos +52; filtro lote ≤5000 |
| `mp_concilianet_profeco` | Consumidor | 130M habitantes | ✅ | Mock + 32 proveedores convenio | Aeroméxico, Volaris, Telcel, Liverpool, Rappi, BBVA, etc. |
| `mp_cre_hidrocarburos` | Energía | ~12k permisionarios | ✅ | Mock + RUPETH público | Umbral Anexo 30 = 75,714 L/mes; calendario 10 primeros días hábiles |

### Tier C · Mock + calculadora/validador (8)

Sin portal público a scrapear — son calculadoras normativas, validadores de cumplimiento, generadores de plantilla legal o trackers estadísticos.

| MCP | Categoría | Razón Tier C | Tests |
|---|---|---|---|
| `mp_ley_silla_nom037` | Compliance laboral | Calculadora multas STPS (UMA 113.07) + checklist NOM-035/037/desconexión + generador política SST | ✅ |
| `mp_expediente_clinico_nom024` | Salud digital | Validador 10 requisitos NOM-024 + clasificador medicamentos COFEPRIS (fracciones I-V) | ✅ |
| `mp_resico_sat` | Fiscal | Calculadora ISR mensual 5 tramos (1.00-2.50%) + alerta tope $3.5M + 12 plataformas digitales retención 2.5% | ✅ |
| `mp_ine_verificacion` | Identidad | Portal INE solo informativo (B2G/B2B vía convenio) — validado vivo 2026-06-15 | ✅ |
| `mp_cfe_interconexion_solar` | Energía renovable | Simulador ahorro + tarifas DAC/PDBT/GDMTH (factor exportación 0.70 vigente 2026) | ✅ |
| `mp_desconexion_digital` | Compliance laboral | Checklist 8 items reforma 2026 + generador política firmable + plantilla capacitación 45min | ✅ |
| `mp_cofepris_aviso_funcionamiento` | Salud | Clasificador 19 giros A/B/C (NOM-167-SSA1) — portal Digipro requiere login | ✅ |
| `mp_sedatu_uso_suelo` | Inmobiliario/Urbano | Catálogo 6 trámites + 13 usos suelo + estimador MIA/EIU/MIV (>10k m²) — competencia municipal varía | ✅ |
| `mp_simplifica_ciudadano` | Tracker estatal | Avance Ley Nacional Trámites Burocráticos (DOF 16-jul-2025) en 32 estados — datos estadísticos curados | ✅ |

### Tier S · Cobertura federal anclada en SAT (1)

| MCP | Categoría | Tests | Path real | Notas |
|---|---|---|---|---|
| `mp_resico_sat` (calculadora) | Promovido a S para empresas <$3.5M MXN | ✅ | Cálculo + calendario | Cubre el 78% del padrón RFC PyMEs MX |

> **Nota de honestidad**: `mp_resico_sat` aparece dos veces — como **calculadora/validador Tier C** (sin scraping al portal SAT) y como **Tier S funcional** porque su lógica de tasas RESICO está validada contra LISR 2026 Art. 113-E. La duplicidad refleja que un mismo paquete puede tener valor operativo S aunque su path técnico sea C.

---

## Métricas globales

- **Path real validado en vivo Playwright**: 20 MCPs (incluye `mp_llave_mx` validado 2026-06-15)
- **Catálogo + mock con discovery documentado**: 39 MCPs (incluye 4 Sprint E Tier B)
- **Mock-only definitivo + calculadoras/validadores normativos**: 21 MCPs (incluye 9 Sprint E Tier C)
- **Tests totales**: 1,514 pasando (1,380 anteriores + 134 Sprint E)
- **Cobertura normativa 2026**: Ley Silla NOM-037 + ECE NOM-024 + RESICO + Desconexión Digital + Simplifica + Anexo 30 CRE

## Convención para agregar un MCP nuevo

1. **Discovery primero** con Playwright MCP en vivo — NO escribir parsers sin ver HTML real.
2. **Documentar hallazgos** en `docs/discoveries/discovery-portales-YYYY-MM-DD.md`.
3. **Asignar Tier** desde el primer commit: S, A, B o C.
4. **Tests mínimos**: catálogo + 1 parser + 1 routing live-flag = 3 tests.
5. **Mock-first obligatorio**: cliente corre sin credenciales con `simulated: true`.
6. **Bitácora con hash**: identificadores sensibles (RFC, CURP, placa) hasheados.
7. **Actualizar este CATALOGO.md** + `mcp-servers/README.md` + `website/mcp-manifest.json`.

## Comandos útiles

```bash
# Listar todos los MCPs
ls mcp-servers/ | grep '^mp_'

# Correr suite completa
PYTHONPATH=mcp-servers python3 -m pytest mcp-servers/ -q

# Validar un MCP específico
PYTHONPATH=mcp-servers python3 -m pytest mcp-servers/mp_predial_mx/tests/ -v
```
