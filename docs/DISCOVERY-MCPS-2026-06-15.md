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
- ✅ `Definitivos.csv` (69-B EFOS): 200 OK, 3.5MB
- ✅ `Presuntos.csv` (69-B presuntos): 200 OK, 185KB
- ❌ `IncumplidosListado.csv` (Lista 69): **404 — URL cambió**

**Acción pendiente**: discovery con Playwright en `omawww.sat.gob.mx/cifras_sat/Paginas/datos/vinculo.html` (página índice que sí responde 200) para encontrar el nuevo path tras la migración a `/minisitio/DatosAbiertos`.

---

## Métricas Sprint 2026-06-15

| Métrica | Valor |
|---|---|
| MCPs implementados | 1 (`mp_sat_opinion_32d` — Top 15 #2) |
| MCPs discovery completado | 1 (`mp_impi_marcanet` — Top 15 #7) |
| Tests pasando | 27/27 ✅ |
| Endpoints backend mapeados | 2 (SAT 32-D, IMPI ViDoc) |
| Líneas Python nuevas | ~800 |
| MCPs Top 15 cubiertos a la fecha | 6/15 (40%) |

**Siguiente sesión**:
1. Implementar `mp_impi_marcanet` con modo Playwright (~5h)
2. Fix `URL_LISTA_69_INCUMPLIDOS` (30 min)
3. Continuar con #10 `mp_condusef_sipres` (Tier 1, sin captcha, ~2h)

— Sesión 2026-06-15, Playwright MCP discovery.
