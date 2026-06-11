# mp_banxico

Cliente MCP para la API SIE (Sistema de Información Económica) de Banxico.

## Para qué sirve

- Obtener **tipos de cambio oficiales DOF** (USD/EUR/GBP/CAD/JPY contra MXN) para emitir CFDIs en moneda extranjera (SAT exige el TC del día hábil anterior al comprobante)
- Obtener **UMA** vigente (referencia para multas, deducciones, créditos)
- Obtener **INPC** (indexación inflacionaria de rentas, contratos)
- Obtener **TIIE 28** (referencia créditos comerciales)
- Conversión de monto entre MXN y otras monedas con TC aplicable

## Setup

### 1. Obtener token gratuito de Banxico

Ve a https://www.banxico.org.mx/SieAPIRest/service/v1/token y registra tu email. Recibirás el token por correo. Es gratis, sin caducidad, sin rate limits agresivos.

### 2. Exportar el token

```bash
export BANXICO_TOKEN="xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

### 3. (Opcional) Probar sin token

Si no exportas `BANXICO_TOKEN`, el MCP corre en **modo mock** con valores plausibles fijos (USD/MXN ~18.50, etc.). Útil para desarrollo.

```bash
# Forzar mock incluso con token configurado (testing)
export PLUGINS_MX_MOCK=1
```

## Correr el servidor

```bash
cd mcp-servers
.venv/bin/python -m mp_banxico.server
```

El servidor habla stdio (default FastMCP). Para integrarlo a Claude Code, agrega a `.mcp.json` del plugin que lo necesite.

## Configurar en Claude Code

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

## Tools disponibles

### `banxico_get_tc_dof`
TC oficial para una fecha específica. Si la fecha no es día hábil, ajusta al anterior.

```python
{
  "moneda": "USD",
  "fecha": "2026-03-15"
}
# →
{
  "moneda_origen": "USD",
  "moneda_destino": "MXN",
  "tipo_cambio": 18.5432,
  "fecha_consultada": "2026-03-15",
  "fecha_aplicable": "2026-03-13",     # ajustada (mar 15 = domingo)
  "fecha_ajustada": true,
  "razon_ajuste": "fin_de_semana",
  "serie": "SF63528",
  "fuente": "Banxico (DOF)",
  "simulated": false,
  "valido_para_cfdi": true,
  "advertencias": []
}
```

### `banxico_get_tc_dia_habil_anterior`
La regla SAT para CFDI: TC del día hábil ESTRICTAMENTE anterior a la fecha de referencia (típicamente la fecha del comprobante).

```python
{
  "moneda": "USD",
  "fecha_referencia": "2026-03-16"  # opcional, default hoy
}
# → TC del 13 de marzo (viernes hábil anterior al lunes 16)
```

### `banxico_convertir_monto`
Convierte un monto entre MXN y otra moneda con TC aplicable.

```python
{
  "monto": 10000,
  "de_moneda": "USD",
  "a_moneda": "MXN",
  "fecha": "2026-03-13"   # opcional
}
# → monto_convertido ~185,000 MXN
```

Reglas:
- Solo soporta conversiones contra MXN (no cross-currency USD→EUR)
- Acepta cualquier dirección: USD→MXN y MXN→USD
- Sin `fecha`, usa el día hábil anterior a hoy

### `banxico_get_uma`
Valor de UMA diaria + mensual + anual. Sin `fecha` retorna el último publicado.

### `banxico_get_inpc`
Índice Nacional de Precios al Consumidor. Mensual.

### `banxico_get_tiie_28`
TIIE a 28 días, referencia créditos.

### `banxico_listar_monedas_soportadas`
Lista todos los pares disponibles. No requiere parámetros ni red.

## Modos de operación

| Estado | Cuándo | Comportamiento |
|---|---|---|
| **Real** | `BANXICO_TOKEN` set | Llama a la API, cachea respuesta 24h |
| **Mock** | Sin token o `PLUGINS_MX_MOCK=1` | Valores plausibles fijos con `simulated: true` |
| **Cache hit** | Después de 1 llamada | Sirve desde `~/.cache/plugins-mx/banxico_mcp/` |

## Cache

- TTL por default: 24h para TC, 30 días para UMA/INPC, 6h para "oportuno"
- Storage: `~/.cache/plugins-mx/banxico_mcp/`
- Override: `PLUGINS_MX_CACHE_DIR=/tmp/test-cache`
- Limpieza manual: `rm -rf ~/.cache/plugins-mx/banxico_mcp/`

## Bitácora

Cada llamada se registra en `~/.local/share/plugins-mx/audit-log/banxico_mcp/YYYY-MM.jsonl`.

Una línea por llamada:
```json
{"ts":"2026-03-15T10:30:00+00:00","namespace":"banxico_mcp","tool":"get_serie_value","success":true,"duration_ms":234,"params":{"serie":"SF63528","fecha":"2026-03-13"},"result":{"value":18.5432}}
```

## Manejo de días no hábiles

Mexicano bancario incluye:
- **Fijos**: 1 ene, 16 sep, 12 dic, 25 dic
- **Movibles**: 1er lunes feb (Constitución), 3er lunes mar (Juárez), 3er lunes nov (Revolución), Jueves Santo, Viernes Santo
- **Fines de semana**: sábado y domingo

Cuando consultas un TC para un día no hábil, el MCP automáticamente regresa al día hábil anterior y te lo indica con `fecha_ajustada: true` + `razon_ajuste`.

## Errores típicos

Si algo falla, el MCP retorna un objeto con `error: true`:

```json
{
  "error": true,
  "code": "auth_error",
  "message": "Authentication failed (HTTP 401). Check API credentials.",
  "details": {"status_code": 401}
}
```

Códigos posibles:
- `validation_error`: input rechazado (fecha mal formada, moneda no soportada, montos negativos, etc.)
- `config_error`: token faltante en modo real
- `auth_error`: token inválido (401/403)
- `rate_limit_error`: demasiadas requests (429)
- `upstream_error`: Banxico respondió 5xx o con shape inesperado
- `timeout`: red lenta o caída
- `not_found`: serie no existe (404)

## ⚠ Datos que requieren verificación vigente

Los códigos de series Banxico hardcodeados en `series.py` provienen de mi training data. Validar contra https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do antes de uso productivo. En 20+ años Banxico raramente renombra series, pero ha agregado/depreciado algunas.

El calendario de feriados bancarios en `holidays.py` cubre las reglas estándar (fijos + lunes movibles + Semana Santa). Validar contra el calendario oficial Banxico anual antes de usar para CFDIs con valor legal.

## Tests

```bash
cd mcp-servers
.venv/bin/python -m pytest mp_banxico/tests -v
```

Cobertura actual: **60 tests** cubriendo holidays, client (mock + cache + parseo), y tools (validación + flujos felices + errores).
