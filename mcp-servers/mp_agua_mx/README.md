# mp_agua_mx

MCP unificado para consulta de adeudo de agua en organismos operadores MX.

## Cobertura v1

12 organismos top — **~30M usuarios** (50% pob urbana):

| Organismo | Estado | Cobertura | Consultable |
|---|---|---|---|
| SACMEX | CDMX | 9.2M | ✅ |
| SIAPA | JAL (GDL+ZMG) | 5M | ✅ |
| SADM | NL (Monterrey ZMM) | 4.5M | ✅ |
| CESPT | BC (Tijuana) | 1.9M | ✅ |
| SAPAL | GTO (León) | 1.8M | ✅ |
| Aguakan | QROO (Cancún+Playa) | 1.5M | ✅ |
| CEAQ | QRO | 1.5M | ✅ |
| JAPAC | SIN (Culiacán) | 1.2M | ✅ |
| CEAS | GTO (estatal) | 1.5M | ⏸ no_único |
| JAPAY | YUC | 1.0M | ⏸ pendiente |
| INTERAPAS | SLP | 800K | ⏸ pendiente |
| OAPAS | EdoMex (Tlalnepantla) | 700K | ⏸ pendiente |

## Tools

### `agua_consultar_adeudo(organismo, cuenta)`
Consulta adeudo + vencimiento + estatus.

### `agua_listar_organismos(solo_consultables=False)`
Lista los 12 organismos del catálogo.

### `agua_buscar_por_estado(estado)`
Filtra por entidad federativa.

### `agua_estadisticas()`
Stats agregadas (cobertura poblacional, % nacional, etc.).

## Estado v1

- ✅ Catálogo unificado con 12 organismos (URLs, identificadores, regex, método)
- ✅ Mock determinístico para los 12
- ✅ Auto-routing por clave del organismo
- ✅ Cache 14 días (recibos bimestrales)
- ⚠️ Scrapers Playwright reales: estructura lista, implementación por-organismo
  pendiente (requiere mapeo individual de selectores DOM de cada portal).

## Configuración

| Env | Default | Descripción |
|---|---|---|
| `PLUGINS_MX_MOCK` | `1` | Override mock. |
| `PLUGINS_MX_AGUA_LIVE` | unset | `1` activa Playwright real. |

## Roadmap implementación scrapers

Prioridad por usuarios:
1. SACMEX (9.2M) — ASP.NET WebForms, consulta pública sin login
2. SIAPA (5M) — portal con cuenta + plaza
3. SADM (4.5M) — captcha sencillo, múltiples métodos
4. CESPT (1.9M) — ASP.NET WebForms
5. SAPAL (1.8M) — oficina virtual
6. Aguakan (1.5M) — concesionario con UI moderna
