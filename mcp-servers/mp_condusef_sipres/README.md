# mp_condusef_sipres

MCP standalone para **CONDUSEF SIPRES** — padrón público de entidades
financieras autorizadas en México.

## Por qué importa

- **Top 15 #10** del roadmap. Tier 1 alto valor, bajo esfuerzo.
- **Universo**: KYC institucional, fintech, due-diligence aseguradoras/SOFOMes.
- Crítico antes de:
  - Contratar productos de una SOFOM (E.R. o E.N.R.)
  - Usar una IFPE/IFC fintech
  - Operar con casa de cambio
  - Suscribir póliza con aseguradora
  - Cualquier KYC institucional

## Portal

- **URL pública**: https://webapps.condusef.gob.mx/SIPRES/jsp/pub/index.jsp
- **Stack**: JSP tradicional + jQuery + Bootstrap + Typeahead
- **Endpoint backend** (descubierto con Playwright MCP 2026-06-15):
  `POST /SIPRES/jsp/pub/resulbusq.jsp` form-urlencoded
- **Sin CAPTCHA, sin XSRF, sin sesión** → httpx puro, latencia ~300ms.
- **Encoding response**: ISO-8859-1 ⚠️ (no UTF-8).

## Tools

### `sipres_buscar_institucion(nombre, sector, estado, estatus, limite=50)`

Búsqueda en el padrón. Devuelve hasta 200 resultados normalizados con:
clave de registro, denominación social, nombre corto, estatus, sector, estado,
fecha de actualización e `idins` (ID interno para consulta detalle).

### `sipres_verificar_autorizada(nombre)`

Decisión binaria para KYC institucional. Devuelve `autorizada_en_operacion: bool`
+ mejor match + advertencias contextuales.

**Importante**: SIPRES NO incluye sancionadas (la página dice literalmente que
si la institución no aparece, es porque "no es Institución Financiera o está
incumpliendo con la normatividad aplicable"). Validar también con CNBV (banca/
valores), CNSF (seguros) o CONSAR (AFORES) según el sector.

## Estados de la entidad (campo `estatus`)

- `En operación` — vigente, puede ofrecer productos al público ✅
- `Cancelado` — registro cancelado ⛔
- `Suspendido` — temporalmente impedida ⛔
- `Revocado` — autorización revocada ⛔
- `En trámite de inscripción` — pendiente autorización

## Sectores comunes

- Instituciones de banca múltiple
- SOFOM E.R. / SOFOM E.N.R.
- Aseguradoras
- AFORES
- Casas de Cambio
- Casas de Bolsa
- Instituciones de Fondos de Pago Electrónico (IFPE)
- Instituciones de Financiamiento Colectivo (IFC)

## Configuración

| Env var | Default | Descripción |
|---|---|---|
| `PLUGINS_MX_MOCK` | `1` | `1` = mock determinístico. `0` = httpx real. |
| `PLUGINS_MX_CACHE_DIR` | `~/.cache/plugins-mx` | Cache local (7 días). |
| `PLUGINS_MX_BITACORA_DIR` | `~/.local/state/plugins-mx/bita` | JSONL logs. |

## Quickstart

```bash
# Mock mode
python -m mp_condusef_sipres.server

# Real mode (httpx directo)
PLUGINS_MX_MOCK=0 python -m mp_condusef_sipres.server
```

## Tests

```bash
PYTHONPATH=mcp-servers pytest mcp-servers/mp_condusef_sipres/tests -v
```

## Lecciones del discovery

Documentado en `docs/DISCOVERY-MCPS-2026-06-15.md`:

1. **JSP tradicional ≠ SPA moderna**: jQuery + handlers inline + form HTML clásico.
2. **Trampa de encoding**: SIPRES responde `ISO-8859-1` — cliente debe decodificar
   explícitamente o los acentos aparecen como `�`.
3. **`idins` en `onclick`**: el ID interno para consulta detalle viene del
   `onclick="window.open('...?idins=NN'...)"` — habilita un segundo tool
   `sipres_consultar_detalle(idins)` en futuras versiones.
4. **El form `formBusins` está oculto en panel collapse** — `display:none` por
   default. Esto es solo cosmético (anti-bot por UX), el endpoint backend
   funciona sin necesidad de visitar la página pública primero.
