# Sprint D — Roadmap (2026-06-15 → 2026-07-XX)

Objetivo: cerrar los 4 huecos críticos identificados en el audit nacional,
en orden secuencial. Total estimado: **~28h activas**.

Principios:
- **Discovery primero en vivo con Playwright MCP** antes de escribir parsers.
- **Mock-first** siempre. Path real opt-in vía env flag por capítulo.
- **`needs_calibration: True`** cuando el HTML de respuesta no se haya verificado.
- Cada bloque cierra con commit + push + ≥10 tests nuevos.

---

## D.1 — Top-7 muns predial (~9h)

**Universo**: 9.4M hab en 7 muns. Cada uno tiene portal documentado.

### Lista priorizada (por población)

| # | Municipio | Estado | Pob (M) | Portal hipótesis | Tipo |
|---|---|---|---|---|---|
| 1 | Tijuana | BCN | 1.92 | recaudacion.tijuana.gob.mx | ASP.NET + captcha |
| 2 | León | GTO | 1.72 | tesoreria.leon.gob.mx | SPA Angular |
| 3 | Mexicali | BCN | 1.05 | servicios.mexicali.gob.mx | ASP.NET |
| 4 | Querétaro | QRO | 1.05 | tramites.queretaro.gob.mx | SPA |
| 5 | Mérida | YUC | 1.00 | merida.gob.mx/pago-predial | PHP custom |
| 6 | Culiacán | SIN | 0.96 | tramites.culiacan.gob.mx | ASP.NET |
| 7 | Cancún (Benito Juárez) | QROO | 0.91 | benitojuarez.gob.mx/predial | SPA |

### Pasos por municipio (~1.2h c/u)

1. **Discovery Playwright MCP** (15 min):
   - `browser_navigate` al portal candidato.
   - `browser_evaluate` para listar `<input>`, `<form action>`, captcha scripts.
   - Capturar selectores reales (no asumir).
2. **Catalogar** (10 min): agregar a `shared/catalogo_municipios_mx.py`
   con `MunicipioConfig` + `PortalConfig` (url_consulta, identificador_regex,
   captcha_tipo, validated=True).
3. **Test del catálogo** (5 min): verificar `get_municipio_config` devuelve config.
4. **Smoke test del portal** (15 min): comprobar que el portal responde HTTP 200
   y que el form sigue ahí (no migró).
5. **No implementar path real**: el cliente `mp_predial_mx` ya tiene
   `playwright_municipal_generic` que itera selectores. Sólo necesitamos
   alimentar el catálogo con configs correctas.

### Entregables D.1

- `shared/catalogo_municipios_mx.py` con 7 muns nuevos validados.
- Tests: `tests/test_catalogo_top7.py` con 7 asserts (uno por mun).
- Commit: `feat(mx): predial top-7 muns (+9.4M hab cobertura)`.

---

## D.2 — Agua organismos top faltantes (~6h)

**Universo**: 6 organismos · ~5M usuarios.

### Lista priorizada

| # | Organismo | Ciudad | Usuarios (M) | Portal hipótesis |
|---|---|---|---|---|
| 1 | JMAS Juárez | Cd. Juárez CHIH | 1.50 | jmaspr.gob.mx |
| 2 | CESPM | Mexicali BCN | 1.05 | cespm.gob.mx |
| 3 | AGUAH | Hermosillo SON | 0.94 | aguah.gob.mx |
| 4 | SIMAS Saltillo | Saltillo COAH | 0.88 | aguasdesaltillo.com |
| 5 | OOAPAS | Morelia MICH | 0.75 | ooapas.gob.mx |
| 6 | OAPAS Tlalnepantla | EdoMex | 0.70 | tlalnepantla.gob.mx/oapas |

### Pasos por organismo (~1h c/u)

1. **Discovery Playwright** (20 min): igual que predial.
2. **Catalogar** (10 min): agregar a `shared/agua_mx.py::CATALOGO_AGUA`
   con `OrganismoAgua` (consultable=True, identificador_regex real).
3. **Implementar `_real_<clave>`** (20 min): patrón Playwright similar a
   `_real_siapa`, ajustando selectores por organismo.
4. **Test parser HTML** (10 min): con HTML mock estructurado.

### Entregables D.2

- `shared/agua_mx.py` con 18 organismos (12 + 6).
- 6 métodos `_real_<clave>` en `mp_agua_mx/client.py`.
- 12 tests nuevos (6 parsers + 6 routing live-flag).
- Commit: `feat(mx): agua 6 organismos top (+5M usuarios)`.

---

## D.3 — Catastro 5 estados grandes (~7h)

**Universo**: 5 sistemas estatales · cubren 35M+ habitantes (CDMX 9.2M, JAL 8.4M, NL 5.8M, GTO 6.2M, SON 3M).

### Lista priorizada

| # | Estado | Sistema | URL portal hipótesis |
|---|---|---|---|
| 1 | CDMX | Tesorería Catastro | data.finanzas.cdmx.gob.mx/catastro |
| 2 | Jalisco | IGEJ / Catastro Edo | catastro.jalisco.gob.mx |
| 3 | Nuevo León | Instituto Catastral NL | icl.nl.gob.mx |
| 4 | Guanajuato | IGECEM-G / DICOM | dicom.guanajuato.gob.mx |
| 5 | Sonora | CCS Sonora | catastrosonora.gob.mx |

### Pasos por estado (~1.4h c/u)

1. **Discovery Playwright** (25 min): inspeccionar formulario consulta por
   cuenta catastral o clave única. Verificar tipo de identificador (16 dig CCU,
   etc.) y captcha.
2. **Catalogar** (15 min): agregar a `shared/catastro_estatal.py::CATALOGO_CATASTRO_ESTATAL`
   con `SistemaCatastral` (clave, total_muns, identificador_regex, url_consulta).
3. **Implementar path real** (30 min) o documentar limitación (algunos
   requieren cita presencial / no consulta pública).
4. **Tests** (15 min): catálogo + parser HTML.

### Entregables D.3

- `shared/catastro_estatal.py` con 10 sistemas (5 + 5).
- Path real Playwright donde haya portal público.
- Marcador `requires_in_person: True` donde no haya.
- 10 tests nuevos.
- Commit: `feat(mx): catastro 5 estados grandes (+35M hab)`.

---

## D.4 — mp_multas_vehiculares_mx (~6h)

**Universo**: capítulo NUEVO. ~30M vehículos registrados MX.

### Sistemas a cubrir (4 iniciales)

| # | Sistema | Cobertura | Portal hipótesis |
|---|---|---|---|
| 1 | Foto-multas CDMX | 5M vehículos | data.finanzas.cdmx.gob.mx (mismo SAF — reusar) |
| 2 | Foto-multas EdoMex | 8M vehículos | sf.edomex.gob.mx |
| 3 | Tránsito NL | 5M vehículos | banca.nl.gob.mx/multas |
| 4 | Tránsito Jalisco | 4M vehículos | sat.jalisco.gob.mx/multas |

### Pasos

1. **Crear estructura**:
   - `shared/multas_vehiculares_mx.py` con `CATALOGO_MULTAS`.
   - `mp_multas_vehiculares_mx/` con `client.py`, `server.py`, `tests/`.
2. **Tools planeadas**:
   - `multas_consultar_por_placa(estado, placa)` → lista de multas.
   - `multas_calcular_total(estado, placa)` → suma + descuentos vigentes.
   - `multas_generar_linea_captura(estado, placa, monto)` → link de pago.
   - `multas_listar_sistemas()`.
3. **Discovery Playwright en vivo** (4 portales × 20 min = 80 min).
4. **Implementar path real CDMX primero** (reusa `URL_SAF_CDMX_CONSULTA`).
5. **Mock + path real para los 3 restantes** (~60 min c/u).
6. **Tests**: 15+ (mocks por estado, parser, routing).

### Entregables D.4

- MCP nuevo con 4 tools.
- Path real CDMX funcional.
- Mocks deterministas para los otros 3.
- Commit: `feat(mx): mp_multas_vehiculares_mx (CDMX/EdoMex/NL/JAL)`.

---

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Portal con DNS muerto (caso EdoMex verificación) | Discovery con Playwright primero, abandonar si DNS_NOT_RESOLVED y marcar `requires_in_person` |
| reCAPTCHA Enterprise v3 invisible | Patrón Telmex ya probado (Playwright sin headless intervention) |
| reCAPTCHA v2 checkbox | Patrón SIAPA ya probado (wait_for_function sobre `g-recaptcha-response`) |
| Captcha imagen ASP.NET | Patrón CFE ya probado (screenshot → resolver cascade env/TTY) |
| Portal cae en domingo (caso SACMEX) | Documentar en discovery, reintentar día hábil |
| HTML de respuesta no verificable sin cuenta real | Marcar parser `needs_calibration: True` y devolver `html_snippet` |

---

## Orden de ejecución

```
D.1 (predial) → D.2 (agua) → D.3 (catastro) → D.4 (multas)
   9h            6h            7h               6h
                                             ───────
                                              28h total
```

Cada D.X termina con: tests verdes + commit + push + actualización
`docs/discovery-portales-2026-06-15.md` con hallazgos negativos
encontrados en discovery (siguiendo patrón Naturgy/EdoMex de honestidad).

## Después de Sprint D

Sprints potenciales E/F (no plan ahora, sólo ideas):
- Predial muns 8-30 más grandes (+15M hab adicionales).
- Pagos multas/predial via OXXO/SPEI (línea de captura).
- Tenencia 12 estados restantes con calculadora.
- Catastro 22 estados restantes.
