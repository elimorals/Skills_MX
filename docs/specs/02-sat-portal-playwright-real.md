---
spec: "sat-portal-playwright-real"
estado: "DRAFT"
creado: "2026-06-11"
autor: "Elias"
ultima_actualizacion: "2026-06-11"
esfuerzo_estimado_horas: [100, 200]
prioridad: "tier-1"
---

# Spec 02 — `mp_sat_portal` Playwright path real (auth + scraping)

## 1. Propósito

El MCP `mp_sat_portal` actualmente expone **11 tools en mock + 4 públicos vía HTTP** (padrón, 69-B, 69, verifica CFDI). Las 6 tools con auth (CSF, Buzón, descarga masiva CFDIs, citas, e.firma, acuse) están **mock-only**.

Este spec define el **path real con Playwright + e.firma** que desbloquea:
- Descarga masiva de CFDIs emitidos+recibidos (crítico para `cierre-fiscal-mensual` y `pf-anual-completa`)
- Notificaciones del Buzón Tributario en tiempo real
- CSF en PDF descargable para due-diligence
- Status e.firma con renovación anticipada
- Acuses de declaraciones

Sin esto los workflows fiscales generan **datos sintéticos** que no son utilizables para SAT real.

## 2. Contexto y por qué es novedoso

- **Lo que existe**: estructura `mp_sat_portal/client.py` con todos los métodos pero retornando mock cuando no hay credenciales.
- **Por qué es novedoso**: este sería el **primer Playwright real** del repo. `shared/playwright_stub.py` existe pero solo abstrae la decisión mock vs real — no implementa el browser automation.
- **Reto técnico**: e.firma (.cer + .key + contraseña) + selectores SAT que **cambian cada 3-6 meses** + CAPTCHAs en algunos endpoints + sesiones que expiran en 10min.
- **Referencia plan original**: sección 6.1, esfuerzo estimado original 200-300h.

## 3. Alcance

**Dentro:**
- Login automatizado con e.firma (.cer + .key + contraseña)
- `descargar_csf(rfc)` — PDF de Constancia de Situación Fiscal
- `descargar_buzon_tributario(rfc)` — JSON con notificaciones
- `descargar_cfdi_masivo(rfc, ejercicio, mes, tipo)` — ZIP con XMLs
- `verificar_efirma_vigente(rfc)` — status + días para vencer
- `descargar_acuse(folio)` — PDF acuse
- Cache de sesión (8h dentro del límite SAT de 10min idle)
- Detector de breakage de selectores con alerta

**Fuera (decisión deliberada):**
- `actualizar_obligaciones` — sigue 100% bloqueado por seguridad
- Login con CIEC (solo e.firma) — CIEC tiene mucho captcha
- Playwright real para `verificar_cfdi_uuid` — el path HTTP público actual basta
- Persistencia de sesión entre runs (cada sesión Claude Code es separada)

## 4. Inputs / outputs / schemas

### Auth setup

```bash
SAT_EFIRMA_CERT=/path/to/firma.cer       # certificado público
SAT_EFIRMA_KEY=/path/to/firma.key        # llave privada
SAT_EFIRMA_PASSWORD=...                  # password e.firma
SAT_RFC=ABC010101AA1                     # RFC del contribuyente
PLUGINS_MX_PLAYWRIGHT_REAL=1             # opt-in explícito
```

### Schema descarga masiva

```python
class DescargaMasivaResult(BaseModel):
    rfc: str
    ejercicio: int
    mes: int
    tipo: Literal["emitidos", "recibidos"]
    solicitud_id: str                      # ID asignado por SAT
    estado: Literal["solicitada", "en_proceso", "lista", "expirada"]
    fecha_solicitud: datetime
    fecha_estimada_disponibilidad: datetime
    total_cfdis: int | None                # cuando esté lista
    url_descarga_zip: str | None           # vigencia 72h
    simulated: bool
```

## 5. Tools afectados

| Tool | Mock actual | Path real |
|---|---|---|
| `sat_descargar_csf` | ✅ mock | + Playwright login + descarga PDF |
| `sat_descargar_buzon_tributario` | ✅ mock | + Playwright scraping notificaciones |
| `sat_descargar_cfdi_masivo` | ✅ mock | + Playwright solicitud + polling |
| `sat_verificar_efirma_vigente` | ✅ mock | + scraping fecha vencimiento |
| `sat_agendar_cita` | ✅ mock | + Playwright disponibilidad (lectura) |
| `sat_descargar_acuse` | ✅ mock | + Playwright descarga PDF |

## 6. Casos edge

| Caso | Comportamiento |
|---|---|
| Selectores SAT cambiaron | Auto-detect breakage → fallback mock + alerta crítica + abrir issue |
| Sesión expira mid-operación | Re-login automático con misma e.firma |
| CAPTCHA aparece | Fallback mock + alerta "manual fallback requerido" |
| e.firma vencida | Error específico `EfirmaVencidaError` antes de cualquier intento |
| RFC del .env distinto al RFC en e.firma | Validación pre-vuelo, error claro |
| Descarga masiva > 100k CFDIs | SAT pagina automáticamente — manejar |
| SAT down (mantenimiento) | Retry 3 veces backoff 30s → mock con alerta |
| .cer/.key corruptos | `KeyLoadError` antes de Playwright |

## 7. Dependencias

- **Librerías nuevas**: `playwright>=1.42`, `playwright-stealth` (anti-detect), `cryptography` (para validar e.firma local)
- **MCPs**: ninguno nuevo — extiende mp_sat_portal existente
- **Browser**: Chromium headless via Playwright (~200MB download)
- **Servicios externos**: portales SAT (siat.sat.gob.mx, buzonservicios.sat.gob.mx)

## 8. Criterios de aceptación

- [ ] Sin credenciales setadas → modo mock idéntico al actual (no rompe nada)
- [ ] Con e.firma + `PLUGINS_MX_PLAYWRIGHT_REAL=1` → login real exitoso
- [ ] `sat_descargar_csf` retorna PDF real descargado con UUID del documento
- [ ] `sat_descargar_buzon_tributario` retorna notificaciones reales
- [ ] `sat_descargar_cfdi_masivo` crea solicitud real (no mock) y devuelve solicitud_id verificable
- [ ] Detector de breakage: si selector falla, fallback mock + log claro
- [ ] Tests con e.firma de SAT sandbox (existe — RFCs ficticios oficiales)
- [ ] Sesión cacheada en `~/.cache/plugins-mx/sat_portal/session.json` con TTL
- [ ] Bitácora con RFC hasheado de cada operación
- [ ] Docs `mp_sat_portal/README.md` actualizado con sección "Path real"

## 9. Esfuerzo estimado

- **Setup Playwright + e.firma loader**: 15-20h
- **Login automation + sesión cache**: 20-30h
- **`descargar_csf` (más simple, navega + descarga)**: 15-20h
- **`descargar_buzon_tributario` (parser HTML notificaciones)**: 20-25h
- **`descargar_cfdi_masivo` (multi-step: solicitar + polling + descarga ZIP)**: 30-40h
- **`verificar_efirma_vigente`**: 10-15h
- **`descargar_acuse`**: 10-15h
- **Detector breakage selectores + alertas**: 10-15h
- **Tests + fixtures + docs**: 20-30h
- **TOTAL**: **150-210 horas** (~4-6 semanas FT)

## 10. Riesgos + mitigaciones

| Riesgo | Prob | Impacto | Mitigación |
|---|---|---|---|
| Selectores SAT cambian | **Alta (cada 3-6m)** | Alto | Detector + versionado selectores + mantenimiento mensual presupuestado |
| CAPTCHA agregado a flujos críticos | Media | Alto | Mantener mock fallback + alerta manual |
| Bloqueo IP por scraping intenso | Baja | Alto | Rate limit 1 req/30s + headers humanos via stealth |
| e.firma vence en producción real | Alta | Alto | Pre-check vigencia + alerta 90 días antes |
| Robo de e.firma del .env | Media | Crítico | NUNCA commit .env, restringir acceso, considerar HSM |
| Playwright ZIP browser 200MB | Baja | Bajo | Lazy install + cache local |

## 11. Decisiones pendientes

- [ ] ¿Headless o headed durante desarrollo? (headed = más fácil debug, headless = prod)
- [ ] ¿Donde guardar PDFs descargados? (`~/.local/share/plugins-mx/sat-pdfs/` sugerido)
- [ ] ¿Test con e.firma sandbox del SAT o crear cuenta de prueba? (sandbox existe)
- [ ] ¿Aceptar usuario con `playwright-stealth` adicional? (sí — reduces detect)
- [ ] ¿Cómo notificar al usuario que su e.firma vencerá? (WhatsApp hook diario?)

## 12. Plan de implementación

### Fase 1: Foundation (15-20h)
1. `pip install playwright cryptography playwright-stealth`
2. `playwright install chromium`
3. `mp_sat_portal/playwright_client.py` con login stub
4. Loader de .cer + .key con cryptography
5. Pre-check vigencia e.firma antes de Playwright

### Fase 2: Login real (20-30h)
1. Navegar a https://siat.sat.gob.mx
2. Subir .cer + .key
3. Ingresar password
4. Capturar cookies de sesión
5. Persistir sesión a JSON cache

### Fase 3: Tools simples (35-55h)
1. `sat_descargar_csf` (navegar + descargar)
2. `sat_verificar_efirma_vigente` (scrape texto)
3. `sat_descargar_acuse` (navegar + descargar)

### Fase 4: Buzón Tributario (20-25h)
1. Navegar Buzón
2. Parser de tabla de notificaciones
3. Detección de pendientes con fecha límite

### Fase 5: Descarga masiva CFDIs (30-40h)
1. Solicitar descarga (form multi-step)
2. Polling cada 30 min hasta `lista`
3. Descargar ZIP
4. Extraer + parsear XMLs

### Fase 6: Hardening (10-15h)
1. Detector breakage cada vez que falla selector
2. Logs estructurados de cada navigation step
3. Fallback mock con alerta clara

### Fase 7: Tests + docs (20-30h)
1. Tests con sandbox SAT (RFCs ficticios)
2. Fixtures de breakage simulado
3. Update README + STATUS.md

## 13. Links

- Plan original: `/Users/elias/Downloads/plugins-mx-planeacion-mcps-agentica.md` sección 6.1
- mp_sat_portal actual: `mcp-servers/mp_sat_portal/`
- Portal SAT: https://www.sat.gob.mx
- Playwright Python docs: https://playwright.dev/python/
- e.firma SAT info: https://www.sat.gob.mx/personas/firma-electronica-vigente
- RFCs ficticios SAT (test): EKU9003173C9, URE180429TM6
