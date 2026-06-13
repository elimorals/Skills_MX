# mcp-servers — MCPs propios para plugins-mx

Servidores MCP (Model Context Protocol) construidos a medida para servicios mexicanos.

## 🆕 Actualización 2026-06-13: arquitectura unificada

Los 8 MCPs municipales individuales ahora son complementados por **MCPs unificados** que delegan al `shared/catalogo_municipios_mx.py` y `shared/plataformas_saas_mx.py`:

- **`mp_predial_mx`** (NUEVO): consulta predial de cualquier municipio del catálogo via 1 MCP. Reemplaza funcionalmente los 8 MCPs individuales (mantenidos por backward compat).
- **`mp_sacpi_michoacan`** (NUEVO): expone los 95 municipios MICH via SACPI como tools MCP.
- **`mp_multas_mx`** (NUEVO): unifica multas estatales de 8 estados (CDMX requiere CAPTCHA).
- **`shared/catalogo_municipios_mx.py`**: 209 municipios catalogados (33 validados con URL real, 17 con selectores DOM verificados).
- **`shared/plataformas_saas_mx.py`**: SACPI Michoacán (+95 muns extra) — hallazgo de mayor ROI.
- **`scripts/descubrir-portal-municipal.py`**: auto-discovery de URLs municipales con Playwright.

**Cobertura efectiva**: 33 directos + 95 via SACPI = **128 municipios consultables** + 209 catalogados con metadatos.

Ver `../docs/SESION-COMPLETA-2026-06-13.md` para el reporte completo.

## Estado

| MCP | Estado | Tests | Uso |
|---|---|---|---|
| **`mp_predial_mx`** 🆕 unificado | ✅ mock + real | 19 ✓ | Consulta predial de cualquier municipio del catálogo (4 tools) |
| **`mp_sacpi_michoacan`** 🆕 | ✅ mock + real | 13 ✓ | 95 muns MICH via SACPI (3 tools) |
| **`mp_multas_mx`** 🆕 unificado | ✅ mock + real | 8 ✓ | Multas estatales 8 estados (2 tools, CDMX con CAPTCHA) |
| `shared/` (utilidades) | ✅ producción | 51 ✓ | Cache + bitácora + mock + errores + **catálogo municipios + plataformas SaaS** |
| `mp_banxico` | ✅ producción (mock + real) | 60 ✓ | Tipos de cambio DOF, UMA, INPC, TIIE |
| `mp_facturama_extendido` | ✅ producción (mock + real) | 88 ✓ | CFDI 4.0: validación local + timbrado + cancelación + búsqueda + descargas |
| `mp_mercado_pago` | ✅ producción (mock + real) | 75 ✓ | Payment links + webhook HMAC validation + refunds + cancel |
| `mp_mercado_libre` | ✅ producción (mock + real) | 63 ✓ | Listings, precios, stock, órdenes, mensajes, preguntas, reputación |
| `mp_curp_renapo` | ✅ producción (estructural real, RENAPO mock) | 58 ✓ | Validación CURP estructural + dígito verificador + generación reversa + consulta RENAPO (mock) |
| `mp_banxico_cep` | ✅ producción (CLABE real, CEP mock) | 53 ✓ | Validación CLABE 18 dígitos + decodificación banco/plaza + parseo claves rastreo SPEI + CEP (mock) |
| `mp_sat_portal` | ✅ producción (públicos HTTP real + UUID estructural, auth mock) | — | Padrón SAT, 69-B EFOS, 69 incumplidos, verifica CFDI, CSF, Buzón, descarga masiva, citas, e.firma, acuse |
| `mp_conekta` | ✅ producción (mock + sandbox/prod por env var) | — | Pasarela MX: órdenes, charges TDC/OXXO/SPEI, refunds, customers, payment links, suscripciones, webhook HMAC |
| `mp_aspel_contpaqi` | ✅ producción (mock + parser CSV exports) | — | Pólizas, balanza, catálogo cuentas, P&L, Balance General — Aspel COI/ContPAQi sin API REST |
| `mp_shopify_mx` | ✅ producción (mock + Shopify Admin API real) | — | Wrapper específico MX: products, inventory, orders, fulfillment, customers + calculadora IVA región |
| `mp_bitso` | ✅ producción (mock + sandbox/prod real con HMAC auth) | — | Exchange cripto-fiat MX: ticker, order book, balance, ledger, fundings, retiros + calculadora ISR Art. 142 LISR |
| `mp_bancos_mx` | ✅ scaffolding mock (Playwright stub) | — | Portales bancarios MX: BBVA, Banamex, Santander, Banorte, HSBC (estado cuenta, movimientos, verificar pago) |
| `mp_imss_patronal` | ✅ scaffolding mock (Playwright stub) | — | IDSE: avisos, alta/baja, cédula autodeterminación, EMCR, SBC, padrón |
| `mp_infonavit_patronal` | ✅ scaffolding mock (Playwright stub) | — | Créditos trabajadores, EMIS, descuentos mensuales, avisos |
| `mp_cdmx_municipal` | ✅ refactor catálogo central (2026-06-13) — OVICA validado | — | Predial CDMX via OVICA (validado MCP), tenencia, hoy no circula. Recomendado usar `mp_predial_mx` para flujos nuevos. |
| `mp_edomex_municipal` | ✅ refactor catálogo central (2026-06-13) | — | 23 muns EdoMex (Toluca validado). Recomendado: `mp_predial_mx`. |
| `mp_monterrey_municipal` | ✅ refactor catálogo central | — | 6 muns NL (San Pedro GG y Apodaca validados). Multas NL estatal. |
| `mp_guadalajara_municipal` | ✅ refactor catálogo central | — | 6 muns JAL (GDL, Zapopan, Pto Vallarta validados). Multas JAL estatal. |
| `mp_merida_municipal` | ✅ refactor catálogo central | — | Mérida YUC (validado, busca por dirección). Multas YUC estatal. |
| `mp_puebla_municipal` | ✅ refactor catálogo central | — | Puebla (validado con CAPTCHA — humano-en-loop). |
| `mp_queretaro_municipal` | ✅ refactor catálogo central (2026-06-13) | — | Querétaro (URL validada). Multas QRO estatal. |
| `mp_tijuana_municipal` | ✅ refactor catálogo central | — | Tijuana BC (pendiente verificar URL real). Multas BC estatal. |
| `mp_inmuebles24` | ✅ scaffolding mock (Playwright stub) | — | Búsqueda inmuebles, detalle, comparables zona, publicar listing |
| `mp_vivanuncios` | ✅ scaffolding mock (Playwright stub) | — | Búsqueda multi-categoría, detalle, publicar anuncio |
| `mp_buro_credito_personal` | ⚠ scaffolding mock + compliance | — | Score, reporte completo, alertas — REQUIERE autorización formal del titular |
| `mp_trustly_mx` | ✅ producción (mock + API REST) | — | Open banking MX: pagos por transferencia directa con autorización del banco del cliente |
| `mp_clip_terminal` | ✅ producción (mock + API REST) | — | POS Clip MX: charges, refunds, status terminal, settlement T+1 |
| `mp_cabify_business` | ✅ producción (mock + API REST) | — | Movilidad B2B: agendar viajes, listar, cancelar, factura mensual |
| `mp_amazon_mx_seller` | ✅ scaffolding mock (LWA+AWSSigV4 no implementado) | — | Amazon MX SP-API: listings, inventory, orders, fees |
| `mp_softrestaurant` | ✅ scaffolding mock + parser CSV | — | POS Soft Restaurant: corte Z, ventas, platillos, meseros, inventario |

Roadmap completo: `../Downloads/plugins-mx-planeacion-mcps-agentica.md`.

## 🆕 Cómo agregar un municipio nuevo

A partir de 2026-06-13, NO se crea un MCP por municipio. Se agrega entry al catálogo central:

### Opción 1: discovery automatizado (recomendado)
```bash
# 1. Agregar municipio a lista de pendientes (si no está en top500)
echo '{"estado": "yuc", "mun": "tizimin", "nombre": "Tizimín"}' >> scripts/municipios-pendientes.json

# 2. Correr discovery
python3 ../scripts/descubrir-portal-municipal.py \
    --input scripts/municipios-pendientes.json \
    --output hallazgos.json --workers 5

# 3. Aplicar resultados al catálogo
python3 ../scripts/aplicar-hallazgos-al-catalogo.py hallazgos.json
```

### Opción 2: manual (cuando ya sabes URL + selectores)
Editar `shared/catalogo_municipios_mx.py` agregando entry al dict `MUNICIPIOS[<estado>]`:

```python
'mi_municipio': MunicipioConfig(
    nombre='Mi Municipio',
    estado_clave='xxx',
    portal_predial_url='https://...',
    selectores_predial={
        'input': ["input[name='cuenta']"],
        'submit': ["button:has-text('Consultar')"],
        'result': 'table',
    },
    poblacion_aprox=N,
    validado=True,
    notas='Validado manualmente YYYY-MM-DD',
),
```

Ver `../docs/PATRONES-MCP-MUNICIPAL.md` para los 5 stacks identificados (ASP.NET, Angular, PHP, ASP clásico, IP+puerto).

### Opción 3: plataforma SaaS estatal
Si descubres un SACPI-like (1 URL cubre múltiples municipios), agregar a `shared/plataformas_saas_mx.py`:

```python
NUEVA_PLATAFORMA = PlataformaSaaS(
    nombre="NombrePlataforma",
    operador="Gobierno del Estado de XXX",
    url_consulta="https://...",
    estados_cubiertos=["xxx"],
    municipios_soportados={"001": "MUN_A", "002": "MUN_B"},
    selectores={...},
    requiere_seleccionar_municipio=True,
    validado=True,
)
```

## Setup

```bash
cd mcp-servers
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Correr tests

```bash
.venv/bin/python -m pytest          # todos
.venv/bin/python -m pytest mp_banxico/tests/  # solo banxico
.venv/bin/python -m pytest -k holiday  # filtro por nombre
```

## Estructura

```
mcp-servers/
├── pyproject.toml
├── shared/                    # Utilidades reutilizadas por todos los MCPs
│   ├── cache.py               # File-based cache con TTL
│   ├── bitacora.py            # Audit log JSONL append-only
│   ├── mock.py                # Detección de modo mock + simulación
│   ├── errors.py              # Tipos de error estandarizados
│   └── tests/
├── mp_banxico/                # Tipos de cambio Banxico
│   ├── server.py              # FastMCP entry point
│   ├── client.py              # HTTP client + cache
│   ├── series.py              # Códigos SIE de series
│   ├── holidays.py            # Días hábiles mexicanos
│   └── tests/
└── (próximos MCPs)
```

## Convenciones

### Naming
- Directorios: `mp_<nombre>` (underscore — Python no acepta hyphen)
- Server name FastMCP: `<nombre>_mcp` (convención del MCP SDK)
- Tools: `<nombre>_<verbo>` (ej. `banxico_get_tc_dof`)

### Capa shared/
Todos los MCPs importan de `shared.*`:
- `shared.cache.FileCache` para cache persistente con TTL
- `shared.bitacora.Bitacora` para audit log
- `shared.mock.is_mock_mode` y `mark_simulated` para fallback sin credenciales
- `shared.errors.handle_httpx_error` para errores estandarizados

### Modo mock
Cada MCP soporta modo mock que produce respuestas plausibles sin red:
- Se activa cuando NO hay credenciales (env var de auth ausente)
- Forzable con `PLUGINS_MX_MOCK=1`
- Las respuestas llevan `simulated: true` para que skills downstream no confíen ciegamente

### Cache
- Storage en `~/.cache/plugins-mx/<mcp_name>/`
- Override con `PLUGINS_MX_CACHE_DIR=/tmp/test-cache`
- TTL explícito por entrada — el MCP decide qué tan fresco necesita cada dato

### Bitácora
- Storage en `~/.local/share/plugins-mx/audit-log/<mcp_name>/YYYY-MM.jsonl`
- Override con `PLUGINS_MX_AUDIT_DIR=...`
- Un JSON por línea, append-only
- Datos sensibles (RFC, CURP, cuentas) se hashean con `Bitacora.hash_sensitive()`

### Errores
Todos los MCPs retornan respuestas con la misma forma cuando hay error:
```json
{ "error": true, "code": "auth_error", "message": "...", "details": {...} }
```
Códigos: `validation_error`, `auth_error`, `rate_limit_error`, `upstream_error`,
`not_found`, `timeout`, `config_error`, `mcp_error`.

## Cómo usar un MCP en Claude Code

Agrega al `.mcp.json` de un plugin (ej. `core-mexico/.mcp.json`):

```json
{
  "mcpServers": {
    "banxico": {
      "command": ".venv/bin/python",
      "args": ["-m", "mp_banxico.server"],
      "cwd": "/Users/elias/Documents/Trabajo/skills/mcp-servers",
      "env": {
        "BANXICO_TOKEN": "${BANXICO_TOKEN:-}"
      },
      "disabled": false
    }
  }
}
```

Sin `BANXICO_TOKEN` el MCP corre en modo mock — útil para desarrollo.

## Cómo agregar un MCP nuevo

1. `mkdir mp_nuevo/tests`
2. Crear `mp_nuevo/server.py` con tools FastMCP
3. Crear `mp_nuevo/client.py` con lógica de red (httpx) + uso de `shared/`
4. Crear `mp_nuevo/tests/conftest.py` con isolación de cache/audit
5. Escribir tests en `mp_nuevo/tests/test_*.py`
6. Agregar `mp_nuevo/tests` a `testpaths` en `pyproject.toml`
7. Correr `pytest -q` y verificar todo verde
8. Documentar en este README

## Verificación vigencia

Los datos hardcodeados en cada MCP (catálogos SAT, series Banxico, calendarios)
pueden quedar desactualizados. Cada archivo crítico tiene una nota `⚠` indicando
qué verificar contra fuente oficial antes de uso productivo.
