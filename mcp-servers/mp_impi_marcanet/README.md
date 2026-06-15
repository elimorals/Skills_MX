# mp_impi_marcanet

MCP standalone para búsqueda en el padrón del **IMPI ViDoc** (Instituto Mexicano
de la Propiedad Industrial).

> Aunque el MCP se llama `mp_impi_marcanet` por consistencia con la doc de
> priorización Top 15, el portal real es **ViDoc** — MARCANET fue descontinuado.

## Por qué importa

- **Universo**: legaltech, agencias creativas, startups, marketplaces.
- **Caso de uso**: validar si una denominación está registrada antes de gastar
  $5K-15K MXN en un trámite IMPI fallido.
- **Top 15 #7** del roadmap (alto valor, bajo esfuerzo original — quedó medio
  por reCAPTCHA v3).

## Portal

- **URL**: https://vidoc.impi.gob.mx/busc
- **Stack**: Angular SPA + ASP.NET Core backend + reCAPTCHA v3 + XSRF token
- **Endpoint backend**: `POST /api/BusquedaDocumentos/getBusquedaSimpleNdjson`
- **Respuesta**: `application/x-ndjson` (newline-delimited JSON, ~860 docs típicos)

## Tools

### `impi_buscar(query, limite=20, incluir_raw=False)`

Búsqueda libre. Devuelve marcas, patentes, diseños y asuntos contenciosos que
matchean el término. Cada resultado incluye denominación, titular, clase Niza,
fechas y ficha normalizada.

### `impi_verificar_denominacion(denominacion)`

Decisión de alto nivel para legaltech: ¿esta denominación parece ya estar
registrada? Devuelve `coincidencias_exactas` y `coincidencias_similares` con
advertencias contextuales.

**Importante**: IMPI evalúa similitud fonética/gráfica/conceptual. La ausencia
de coincidencias en texto NO garantiza registrabilidad — siempre validar con
un abogado de PI antes de operar.

## Modos de operación

| Modo | Trigger | Latencia | Costo |
|---|---|---|---|
| `mock` | Default | <10ms | $0 |
| `playwright` | `PLUGINS_MX_IMPI_LIVE=1` + Playwright instalado | 3-5s/query | $0 |
| `cache` | Hit | <5ms | $0 |

Cache 30 días por query.

## Configuración

| Env var | Default | Descripción |
|---|---|---|
| `PLUGINS_MX_MOCK` | `1` | `1` = mock determinístico, `0` = permite path real |
| `PLUGINS_MX_IMPI_LIVE` | unset | `1` para activar Playwright real (también requiere `MOCK=0` o sin set) |
| `PLUGINS_MX_CACHE_DIR` | `~/.cache/plugins-mx` | Storage local |

## Quickstart

### Modo mock (default — sin dependencias extra)

```bash
python -m mp_impi_marcanet.server
```

### Modo real (con browser)

```bash
pip install playwright
playwright install chromium

PLUGINS_MX_MOCK=0 PLUGINS_MX_IMPI_LIVE=1 python -m mp_impi_marcanet.server
```

## Schema de respuesta normalizado

```json
{
  "query": "TELMEX",
  "total_encontrados": 864,
  "devueltos": 20,
  "resultados": [
    {
      "expediente": "MA/M/1985/3502080",
      "numero_expediente": "3502080",
      "area": "MARCAS",
      "anio": 2025,
      "tipo_expediente": "MARCA",
      "denominacion": "RELLAMADO TELMEX",
      "titular": "TELEFONOS DE MEXICO, S.A.B. DE C.V.",
      "titular_nacionalidad": "MEXICO",
      "titular_estado": "CUAUHTEMOC, CIUDAD DE MEXICO",
      "clase_niza": "38",
      "tipo_descripcion": "DENOMINACION",
      "fecha": "2025-11-11T14:21:29"
    }
  ],
  "fuente": "https://vidoc.impi.gob.mx/busc",
  "modo": "playwright"
}
```

## Discovery + decisiones de diseño

Documentadas en `docs/DISCOVERY-MCPS-2026-06-15.md`. Highlights:

1. **MARCANET migró a ViDoc** — la URL del Top 15 original (`marcanet.impi.gob.mx`) ya no resuelve DNS.
2. **3 protecciones** (Angular + reCAPTCHA + XSRF) hacen imposible un cliente httpx-only sin un solver de reCAPTCHA v3 pago.
3. El **NDJSON streaming** NO pagina server-side — devuelve todos los matches en una sola respuesta de hasta 1MB.
4. Reutilizamos `shared/playwright_session.py` — same helper para futuros MCPs (CONDUSEF, COFEPRIS, REPUVE).

## Tests

```bash
PYTHONPATH=mcp-servers pytest mcp-servers/mp_impi_marcanet/tests -v
```
