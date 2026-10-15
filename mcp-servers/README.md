# mcp-servers — MCPs propios para plugins-mx

Servidores MCP (Model Context Protocol) construidos a medida para servicios mexicanos.

## Estado

83 MCPs (`mp_*`) con 417 tools, en Python + FastMCP. El estado de cada uno (real validado en vivo, real sin validar, entrega a humano, sin API pública, cálculo normativo, bloqueado, sin verificar) está en [`CATALOGO.md`](CATALOGO.md), que se genera desde la sección "Estado real" del README de cada MCP con `scripts/generar-estado-mcps.py`. No se mantiene una tabla de estado a mano aquí.

**Regla común:** sin credenciales, un MCP responde datos de ejemplo marcados `simulated: true`; con credenciales, cualquier error del proveedor se propaga como error tipado (`AuthError`, `UpstreamError`, `NotFoundError`…), nunca hay fallback silencioso a datos de ejemplo. `PLUGINS_MX_MOCK=1` fuerza el modo de ejemplo. Decisión en [ADR 008](../docs/adrs/008-estado-real-sin-fallback-silencioso.md).

Utilidades en `shared/`: `portal_handoff.py` (entrega a humano cuando el portal exige CAPTCHA o login), `captcha_solver.py` (solver opt-in con `PLUGINS_MX_CAPTCHA_SOLVER=2captcha` + `TWOCAPTCHA_API_KEY`), `errors.py`, `bitacora.py`, `cache.py`, `mock.py`, `catalogo_municipios_mx.py`, `plataformas_saas_mx.py` y helpers por portal.

Los MCPs municipales delegan al catálogo central (`shared/catalogo_municipios_mx.py`) y a las plataformas SaaS estatales (`shared/plataformas_saas_mx.py`, p. ej. SACPI Michoacán); `mp_predial_mx` y `mp_multas_mx` son los puntos de entrada unificados.

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

Ver [`docs/architecture/PATRONES-MCP-MUNICIPAL.md`](../docs/architecture/PATRONES-MCP-MUNICIPAL.md) para los 5 stacks identificados (ASP.NET, Angular, PHP, ASP clásico, IP+puerto).

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
uv venv .venv --python 3.12
uv pip install -e ".[dev]"            # más extras según el MCP: sat-ws, sat-portal, publicos-federales, estatal-centro…
```

## Correr tests

```bash
.venv/bin/pytest -q                                    # unitarios, sin red
.venv/bin/pytest -q mp_banxico/tests/                  # solo banxico
PLUGINS_MX_LIVE=1 .venv/bin/pytest -q -m live <ruta>   # contra el portal real
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
└── mp_*/                     # 83 MCPs, cada uno con README (sección "Estado real") y example.mcp.json
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
- `shared.mock.is_mock_mode` y `mark_simulated` para datos de ejemplo cuando no hay credenciales
- `shared.errors.handle_httpx_error` para errores estandarizados

### Datos de ejemplo (sin credenciales)
- Solo cuando NO hay credenciales (env var de auth ausente) o con `PLUGINS_MX_MOCK=1`
- Las respuestas llevan `simulated: true` para que las skills no confíen ciegamente
- Con credenciales configuradas, un error del proveedor se propaga; nunca se cae a datos de ejemplo

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

Cada `mp_*/example.mcp.json` trae la configuración lista para copiar. No depende de dónde esté el repo: `uv` descarga el paquete desde GitHub la primera vez.

```json
{
  "mcpServers": {
    "banxico": {
      "command": "uv",
      "args": ["run", "--no-project", "--quiet", "--with",
               "plugins-mx-mcp-servers @ git+https://github.com/elimorals/Skills_MX@main#subdirectory=mcp-servers",
               "python", "-m", "mp_banxico.server"],
      "env": {
        "BANXICO_TOKEN": "${BANXICO_TOKEN:-}",
        "PLUGINS_MX_MOCK": "${PLUGINS_MX_MOCK:-}"
      }
    }
  }
}
```

Para MCPs con dependencias opcionales, el paquete lleva extras: `plugins-mx-mcp-servers[sat-ws,sat-portal] @ git+…`. Sin `BANXICO_TOKEN` el MCP responde datos de ejemplo marcados `simulated: true`. `scripts/mcp-config-portable.py --check` verifica que ninguna config tenga rutas locales ni mock forzado.

## Cómo agregar un MCP nuevo

1. `mkdir mp_nuevo/tests`
2. Crear `mp_nuevo/server.py` con tools FastMCP
3. Crear `mp_nuevo/client.py` con lógica de red (httpx) + uso de `shared/`
4. Crear `mp_nuevo/tests/conftest.py` con isolación de cache/audit
5. Escribir tests en `mp_nuevo/tests/test_*.py`
6. Agregar `mp_nuevo/tests` a `testpaths` en `pyproject.toml`
7. Correr `pytest -q` y verificar todo verde
8. Escribir `mp_nuevo/README.md` con su sección "Estado real" y un `example.mcp.json`, y correr `python3 scripts/generar-estado-mcps.py`

## Verificación vigencia

Los datos hardcodeados en cada MCP (catálogos SAT, series Banxico, calendarios)
pueden quedar desactualizados. Cada archivo crítico tiene una nota `⚠` indicando
qué verificar contra fuente oficial antes de uso productivo.
