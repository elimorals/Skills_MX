# mp_sat_opinion_32d

MCP standalone para **Consulta Pública de Opinión 32-D del SAT** (Art. 32-D
del Código Fiscal de la Federación).

## Estado real (2026-10-14)

| Tool | Estado | Validación en vivo |
|---|---|---|
| `sat_opinion_32d_consultar` / `_verificar_proveedor` | **Real** por default (pública, sin login ni CAPTCHA). Mock solo con `PLUGINS_MX_MOCK=1`. HTTP/red fallida → error explícito. Las respuestas `estado: "error"` ya no se cachean. | 2026-10-14 `POST https://ptsc32d.clouda.sat.gob.mx/ConsultaPublico/Index` (RFC `SAT970701NN3`) → 200, `estado: positiva`. |
| `sat_opinion_32d_descargar_propia` (nuevo) | **Real con e.firma, sin validar con e.firma real.** Login FIEL httpx (`shared/sat_portal_fiel.py`, port de satcfdi) → `RespuestaCompleta/ObtenerRespuestaCompletaPdf`. Funciona aunque la opinión no sea pública. El sentido (positiva/negativa) queda dentro del PDF, sin extraer. | Entrada `ptsc32d.clouda.sat.gob.mx/?/reporteOpinion32DContribuyente` redirige al NIDP `loginda.siat` (id=ciec) — vivo 2026-10-14. Test live: `test_live_opinion_propia`. |

## Por qué importa

"Sin Opinión 32-D vigente, no se contrata con nadie."

- Es **obligatorio** para todo proveedor que contrate con la APF (gobierno
  federal mexicano).
- Es **práctica estándar B2B** para due-diligence de proveedores nuevos.
- Universo: **TODO proveedor B2B/B2G** mexicano.

## Portal

- **URL**: https://ptsc32d.clouda.sat.gob.mx/ConsultaPublico
- **Sin CAPTCHA, sin login, sin sesión**.
- **Endpoint real backend** (descubierto con Playwright MCP 2026-06-14):
  `POST /ConsultaPublico/Index` con multipart FormData (`Rfc` + `Curp`).
- Latencia ~200-500ms. NO requiere Playwright en producción.

## Tools

### `sat_opinion_32d_consultar(rfc, curp, incluir_pdf=True)`

Consulta full con PDF firmado por SAT. Devuelve:

```json
{
  "rfc": "...",
  "curp": "...",
  "estado": "positiva | negativa | no_autorizado | no_inscrito | error",
  "puede_contratar_con_gobierno": true,
  "mensaje_oficial": "Opinión Positiva. * Información a la fecha de la consulta.",
  "pdf_base64": "JVBERi0xLjQK...",
  "fecha_consulta": "2026-06-15T03:57:48.000Z",
  "fuente": "https://ptsc32d.clouda.sat.gob.mx/ConsultaPublico/Index"
}
```

### `sat_opinion_32d_verificar_proveedor(rfc)`

Decisión binaria para due-diligence B2B/B2G. Devuelve:

```json
{
  "rfc": "...",
  "puede_contratar_con_gobierno": false,
  "estado": "negativa",
  "advertencias": [
    "Opinión NEGATIVA: el contribuyente tiene incumplimientos fiscales..."
  ],
  "detalle": { ... }
}
```

## Estados posibles

| Estado | Significado | Acción |
|---|---|---|
| **positiva** | Al corriente — `alert-success` en HTML + PDF firmado | Puede contratar ✅ |
| **negativa** | Adeudos / incumplimientos — `alert-danger` en HTML + PDF | **No contratar** ⛔ |
| **no_autorizado** | Existe en padrón pero no autorizó publicación pública | Pedir al proveedor que active publicación en Buzón Tributario |
| **no_inscrito** | RFC no existe en el padrón SAT | Bloqueador — RFC erróneo o nunca activado |
| **error** | Respuesta inesperada del SAT | Reintentar |

## Configuración

| Env var | Default | Descripción |
|---|---|---|
| `PLUGINS_MX_MOCK` | (vacío = real) | `1` = respuestas simuladas determinísticas. |
| `SAT_EFIRMA_CERT` / `_KEY` / `_PASSWORD` | — | Solo para `descargar_propia`. |
| `PLUGINS_MX_CACHE_DIR` | `~/.cache/plugins-mx` | Cache local (TTL 7 días por consulta). |
| `PLUGINS_MX_BITACORA_DIR` | `~/.local/state/plugins-mx/bita` | Logs JSONL con identificadores hasheados. |

## Quickstart

```bash
# Real (default, golpea el SAT directo)
python -m mp_sat_opinion_32d.server

# Mock
PLUGINS_MX_MOCK=1 python -m mp_sat_opinion_32d.server
```

## Tests

```bash
pytest mcp-servers/mp_sat_opinion_32d/tests -v
```

## Lecciones del discovery

Documentadas en `docs/VALIDACION-MCPS-PRODUCCION-2026-06-15.md`:

1. El front-end usa **jQuery + handlers inline** con anti-bot cosmético
   (`onpaste="return false"`, `onkeydown="validarfc"`). El backend NO valida
   session ni CSRF — ideal para MCP HTTP-only.
2. **2 formatos de respuesta** discriminados por `Content-Type`: JSON con
   `MsjeIformativo` (no autorizado) o HTML con `alert-success`/`alert-danger`
   + PDF base64 embebido en `<div id="contenidoBase64">`.
3. El PDF es generado server-side con Apache FOP 2.11.

— Sesión 2026-06-15, descubierto con Playwright MCP.
