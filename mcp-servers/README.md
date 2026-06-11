# mcp-servers — MCPs propios para plugins-mx

Servidores MCP (Model Context Protocol) construidos a medida para servicios mexicanos.

## Estado

| MCP | Estado | Tests | Uso |
|---|---|---|---|
| `shared/` (utilidades) | ✅ producción | 51 ✓ | Cache + bitácora + mock + errores |
| `mp_banxico` | ✅ producción (mock + real) | 60 ✓ | Tipos de cambio DOF, UMA, INPC, TIIE |
| `mp_facturama_extendido` | ✅ producción (mock + real) | 88 ✓ | CFDI 4.0: validación local + timbrado + cancelación + búsqueda + descargas |
| `mp_mercado_libre` | 🚧 pendiente | — | Listings, orders, mensajes |
| `mp_mercado_pago` | 🚧 pendiente | — | Payment links, webhooks, refunds |
| `mp_curp_renapo` | 🚧 pendiente | — | Validación CURP estructural + RENAPO |
| `mp_banxico_cep` | 🚧 pendiente | — | CEP para conciliación SPEI |
| `mp_sat_portal_playwright` | 🚧 pendiente | — | CSF, padrón, 69-B, Buzón |

Roadmap completo: `../Downloads/plugins-mx-planeacion-mcps-agentica.md`.

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
