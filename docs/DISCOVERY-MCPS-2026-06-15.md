# Discovery con Playwright MCP — Sprint Top 15 (2026-06-15)

> Documenta selectores DOM, endpoints REST y schemas de respuesta para los próximos MCPs del roadmap Top 15. Validado con Playwright MCP en vivo contra los portales reales.

---

## ✅ 1. SAT Opinión 32-D (Top 15 #2) — `mp_sat_opinion_32d` IMPLEMENTADO

### Portal
- **URL**: https://ptsc32d.clouda.sat.gob.mx/ConsultaPublico
- **Stack**: jQuery 3.7.1 slim + Bootstrap + DOMPurify (vanilla JS)
- **Anti-bot**: solo cosmético (`onpaste="return false"`, `onkeydown="validarfc"`)

### Endpoint backend (descubierto)
```
POST https://ptsc32d.clouda.sat.gob.mx/ConsultaPublico/Index
Content-Type: multipart/form-data
Body (FormData):
  Rfc:  "BBA830831LJ2"  (12 chars PM o 13 chars PF)
  Curp: ""              (18 chars o vacío)
```

### Formatos de respuesta (status 200)
1. **`application/json`** → `{"MsjeIformativo": "..."}` cuando RFC no autorizó publicación o no existe.
2. **`text/html`** → HTML con `<div class="alert-success">Opinión Positiva</div>` o `<div class="alert-danger">Opinión Negativa</div>` + PDF base64 firmado por Apache FOP en `<div id="contenidoBase64">...</div>`.

### Estados posibles del MCP
| Estado | Acción |
|---|---|
| `positiva` | Al corriente, puede contratar con APF ✅ |
| `negativa` | Tiene adeudos, NO contratar ⛔ |
| `no_autorizado` | Existe pero no autorizó publicación pública |
| `no_inscrito` | RFC no existe en padrón SAT |
| `error` | Respuesta inesperada |

### Validado E2E con RFC reales
- `BBA830831LJ2` (BBVA México) → **positiva** + PDF
- `PEP970814SF3` (Pemex) → **no_autorizado**
- `AAA010101AAA` (sintaxis válida pero ficticio) → **no_autorizado**

### Tests
27/27 pasando (fixture-based + 4 tests E2E HTTP-layer).

---

## ✅ 2. IMPI ViDoc — Búsqueda de marcas (Top 15 #7) DISCOVERY COMPLETO

> **Cambio importante**: MARCANET (`marcanet.impi.gob.mx`) fue DESCONTINUADO. El IMPI migró a **ViDoc** (Visualización electrónica de Documentos de Propiedad Industrial). El MCP debe llamarse `mp_impi_vidoc` o conservar `mp_impi_marcanet` por SEO/compatibilidad.

### Portal
- **URL**: https://vidoc.impi.gob.mx/busc
- **Stack**: **Angular SPA** (`main-OGCLG24M.js` bundle) sobre ASP.NET Core backend
- **Protecciones**:
  - reCAPTCHA v3 invisible (site key: `6LefZpMqAAAAAGHGQ-kc93rQjqYf1M7LKl8jqYe5`)
  - XSRF Token (ASP.NET Core DataProtection con prefix `CfDJ8...`)

### Endpoint backend (descubierto)
```
POST https://vidoc.impi.gob.mx/api/BusquedaDocumentos/getBusquedaSimpleNdjson
Headers:
  Content-Type: application/json
  X-XSRF-TOKEN: CfDJ8NrMa7xN...

Body (JSON):
  {
    "busqueda":   "TELMEX",
    "recaptcha":  "0cAFcWeA4oujCa3Y..."  (token v3 ~2KB, obtenido en client por Angular)
  }
```

### Respuesta
- **Status**: 200
- **Content-Type**: `application/x-ndjson` (newline-delimited JSON)
- **Tamaño típico**: 700KB+ para queries comunes (~860 documentos sin paginación server-side)

### Schema por línea NDJSON
```json
{
  "event": "processing",
  "data": {
    "expedienteODocumento": "MA/M/1985/3502080",
    "idArea": 114,
    "area": "MARCAS",            // o "PATENTES", "DISEÑOS", "ASUNTOS CONTENCIOSOS"
    "anio": 2025,
    "tipoExpediente": "MARCA",
    "fichaDatos": [
      {"descripcion": "Título o Denominación", "valor": "RELLAMADO TELMEX"},
      {"descripcion": "Titular", "valor": "TELEFONOS DE MEXICO, S.A.B. DE C.V."},
      {"descripcion": "Nacionalidad (Titular.)", "valor": "MEXICO"},
      {"descripcion": "Clase", "valor": "38"},   // Clasificación Niza
      {"descripcion": "Fecha", "valor": "2025-11-11T14:21:29"},
      {"descripcion": "Tipo Descripción", "valor": "DENOMINACION"}
    ]
  }
}
```

### Arquitectura del MCP propuesto

**NO se puede httpx-only.** Requiere Playwright para que reCAPTCHA v3 emita el token desde un contexto de browser real.

**3 modos de operación:**

| Modo | Trigger | Latencia | Costo |
|---|---|---|---|
| `mock` | Default sin creds | < 10ms | $0 |
| `playwright` | `PLUGINS_MX_IMPI_LIVE=1` | 3-5s/query | $0 |
| `2captcha_solver` | `TWOCAPTCHA_API_KEY` + `PLUGINS_MX_IMPI_LIVE=1` | 8-15s/query | ~$0.003 |

**Tools sugeridas:**
- `impi_buscar_marca(query, [limite=20], [area="MARCAS"])` → top N por relevancia
- `impi_detalle_expediente(expediente_id)` → detalle completo de un expediente

**Cache:** 30 días (búsquedas idénticas raramente cambian).

### Universo + ROI estimado
- Top 15 #7, esfuerzo medio (~5h con Playwright en lugar de los ~2h estimados originales).
- Universo: legaltech, agencias creativas, startups, marketplaces (validar denominación de marca antes de lanzar).

---

## 🔜 3. SAT Lista 69 incumplidos — Fix pending

**Estado actual** según `VALIDACION-MCPS-PRODUCCION-2026-06-13.md`:
### ✅ Resuelto (sesión 2026-06-15 PM)

El SAT migró toda la publicación de **Datos Abiertos** a **Azure Blob Storage**
(`wu1agsprosta001.blob.core.windows.net`). Las URLs en `omawww.sat.gob.mx/cifras_sat/`
siguen respondiendo pero con **archivos stale de enero 2026**, mientras los de
Azure se actualizan **mensualmente**.

#### Lista 69 (Art. 69 CFF — incumplidos) — fragmentada en 8 categorías

| Categoría | URL Azure | Tamaño actual (jun 2026) |
|---|---|---|
| **Firmes** ⭐ (default `URL_LISTA_69_INCUMPLIDOS`) | `Documents_AGR/Firmes.csv` | **19.2 MB · 258,333 registros** |
| Cancelados | `Documents_AGR/Cancelados.csv` | 19.9 MB |
| Exigibles | `Documents_AGR/Exigibles.csv` | 462 KB |
| No localizados | `Documents_AGR/No_localizados.csv` | 4.3 MB |
| Sentencias | `Documents_AGR/Sentencias.csv` | 49 KB |
| CSD sin efectos | `Documents_AGR/CSDsinefectos.csv` | 4.7 MB |
| Entes públicos/gob omisos | `Documents_AGR/EntespublicosydeGobiernoomisos.csv` | 373 KB |
| Reducción multas Art 74 | `Documents_AGR/ReduccionArt74CFF.csv` | (variable) |

#### Lista 69-B (Art. 69-B CFF — EFOS) — 5 archivos

| Categoría | URL Azure | Tamaño |
|---|---|---|
| **Listado completo** ⭐ | `Documents_AGAFF/Listado_completo_69-B.csv` | 4.5 MB |
| Definitivos | `Documents_AGAFF/Definitivos.csv` | **3.6 MB · 12,426 registros** |
| Desvirtuados (NUEVO) | `Documents_AGAFF/Desvirtuados.csv` | 110 KB |
| Presuntos | `Documents_AGAFF/Presuntos.csv` | 153 KB |
| Sentencias favorables | `Documents_AGAFF/SentenciasFavorables.csv` | 712 KB |

#### Formato CSV nuevo (gotchas detectados)

1. **2 líneas de preámbulo legal antes del header**:
   ```
   Línea 1: "Información actualizada al 30 de abril de 2026; los listados..."
   Línea 2: "Listado completo de contribuyentes (Artículo 69-B del CFF),,,,"
   Línea 3 (HEADER REAL): No.,RFC,Nombre del Contribuyente,Situación,...
   ```
2. **Encoding ISO-8859-1** (no UTF-8 declarado en Content-Type → httpx default rompe acentos).
3. **Cadena de cert SSL incompleta** en `wu1agsprosta001.blob.core.windows.net`
   — requiere `truststore` o el cert intermedio DigiCert manualmente.

#### Refactor aplicado al monorepo

- **`shared/csv_helpers.py`**: `skip_csv_preamble_until_header()` + `normalize_csv_key()` + `normalize_row()`.
- **`shared/http_helpers.py`**: `build_ssl_verify()` (truststore→certifi→default) + `decode_response_robust()` (UTF-8 strict→latin-1).
- **`mp_sat_portal/rfc69b.py`**: usa los helpers en lugar de duplicar.

---

## Métricas Sprint 2026-06-15 (consolidado AM + PM)

| Métrica | Valor |
|---|---|
| **MCPs nuevos implementados** | **6** (`mp_sat_opinion_32d`, `mp_impi_marcanet`, `mp_condusef_sipres`, `mp_repuve`, `mp_sat_ws`, `mp_no_antecedentes_penales_mx`) |
| **MCPs fixed/refactored** | 1 (`mp_sat_portal` URLs migradas + parser robusto) |
| **Shared libs nuevas** | 6 (`playwright_session`, `impi_vidoc`, `sipres_condusef`, `sat_opinion_32d`, `repuve`, `sat_ws`, `no_antecedentes`, `http_helpers`, `csv_helpers`) |
| **Endpoints backend mapeados** | 5 (SAT 32-D, IMPI ViDoc, SIPRES, SAT WS, SAT Azure Blob) |
| **Tests pasando** | **218/218 ✅** (4 MCPs nuevos + 4 existentes consolidados) |
| **MCPs Top 15 cubiertos** | **11/15 (73%)** ↑ desde 5/15 (33%) inicial |

### Top 15 status post-sesión

| # | MCP | Status |
|---|---|---|
| 1 | `mp_repse_stps` | ✅ Pre-existente |
| 2 | `mp_sat_opinion_32d` | ✅ Esta sesión |
| 3 | `mp_isn_mx` | ✅ Pre-existente |
| 4 | `mp_whatsapp_business` | ❌ Pendiente |
| 5 | **`mp_repuve`** | ✅ **Esta sesión** |
| 6 | `mp_dof_api` | ✅ Pre-existente |
| 7 | `mp_impi_marcanet` | ✅ Esta sesión |
| 8 | `mp_belvo_open_banking` | ❌ Pendiente |
| 9 | **`mp_sat_ws`** | ✅ **Esta sesión** |
| 10 | `mp_condusef_sipres` | ✅ Esta sesión |
| 11 | `mp_cnbv_fintech` | ✅ Pre-existente |
| 12 | `mp_metamap` | ❌ Pendiente |
| 13 | `mp_skydropx` + `mp_99minutos` | ❌ Pendiente |
| 14 | **`mp_no_antecedentes_penales_mx`** | ✅ **Esta sesión** |
| 15 | `mp_donatarias_sat` | ✅ Pre-existente |

### Patrones arquitectónicos consolidados

1. **`shared/playwright_session.py`** — `PortalSession` reusable para portales con
   reCAPTCHA v3 + XSRF. Activado vía `should_use_real_browser(env_flag)`.
2. **`is_mock_mode(default_when_no_creds=False)`** — patrón estándar para portales
   públicos sin auth (SAT 32-D, SIPRES, IMPI). Default = real con `PLUGINS_MX_MOCK=1` override.
3. **`shared/http_helpers.py::build_ssl_verify()`** — truststore → certifi → default,
   esencial para servers gov.mx con cadena de cert incompleta.
4. **`shared/csv_helpers.py::skip_csv_preamble_until_header()`** — para archivos SAT
   AGAFF/AGR con preámbulo legal antes del header real.
5. **`shared/http_helpers.py::decode_response_robust()`** — UTF-8 strict → latin-1 fallback,
   para responses gov.mx sin charset declarado.

**Pendiente Top 15** (próxima sesión): #4 WhatsApp Business, #8 Belvo, #12 MetaMap, #13 Skydropx+99minutos.

— Sesión 2026-06-15 consolidada (AM: discovery + 3 MCPs · PM: 3 MCPs más + refactor + fix Lista 69).
