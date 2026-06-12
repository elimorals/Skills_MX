# mp_bitso — MCP para exchange Bitso (cripto-fiat MX)

Conecta con Bitso, el exchange dominante en México para operar MXN ↔ crypto.

## Tools (12)

### Públicos (sin auth)
| Tool | Propósito | Cache |
|---|---|---|
| `bitso_get_ticker` | Precio actual de un par (last, high, low, ask, bid) | 30s |
| `bitso_get_order_book` | Profundidad de mercado (bids + asks) | 5s |
| `bitso_list_available_books` | Lista de pares disponibles | — |

### Privados (HMAC auth)
| Tool | Propósito | Mock |
|---|---|---|
| `bitso_get_account_status` | Status, límites, verificación | Sí |
| `bitso_get_balance` | Balance por currency (MXN, BTC, ETH, USDT…) | Sí |
| `bitso_get_fees` | Comisiones por par | Sí |
| `bitso_get_ledger` | Historial movimientos (**clave para reporte fiscal**) | Sí |
| `bitso_list_fundings` | Depósitos (fiat SPEI + crypto on-chain) | Sí |
| `bitso_list_withdrawals` | Retiros | Sí |
| `bitso_list_open_orders` | Órdenes limit abiertas | Sí |

### Utility local (sin red)
| Tool | Propósito |
|---|---|
| `bitso_calcular_isr_cripto_mx` | Estima ISR sobre ganancias cripto Art. 142 LISR |

### Discovery
| Tool | Propósito |
|---|---|
| `bitso_listar_catalogos` | Pares, status, métodos depósito, **info fiscal MX** |

## Configuración

| Variable | Propósito |
|---|---|
| `BITSO_API_KEY` | API key (genera en Bitso > Profile > API) |
| `BITSO_API_SECRET` | API secret (hex string) |
| `BITSO_ENV` | `production` (default) o `sandbox` |
| `PLUGINS_MX_MOCK=1` | Forzar mock |

Sin credenciales → modo mock con datos demo plausibles.

## Auth HMAC

Bitso usa HMAC-SHA256 con nonce estrictamente creciente:

```
message = f"{nonce}{verb}{path}{body}"
signature = HMAC-SHA256(message, api_secret).hex()
Authorization: Bitso {api_key}:{nonce}:{signature}
```

Implementado en `auth.py`. `nonce` por default = `time.time() * 1000`.

## Casos de uso

### 1. Reporte fiscal anual cripto
```python
ledger = await bitso_get_ledger(
    operations="trades,fees,rewards",
    limit=100,
)
# Procesar para calcular ganancia/pérdida del ejercicio
```

### 2. Conciliar depósito SPEI
```python
fundings = await bitso_list_fundings(limit=50)
spei_recibidos = [f for f in fundings["fundings"] if f["method"] == "spei"]
# Cruzar con CFDIs emitidos PPD
```

### 3. Calcular ISR estimado
```python
isr = await bitso_calcular_isr_cripto_mx(
    ganancia_total_mxn=85_000.00,
    otros_ingresos_anuales_mxn=500_000.00,
    regimen="PFAE",
)
# isr["isr_aproximado_mxn"] — REFERENCIAL, validar con contador
```

## Implicaciones fiscales MX

⚠ **Cripto en MX es "otros ingresos"** (Art. 142 LISR), no ganancia de capital especial. Se acumula a los demás ingresos del ejercicio.

- Bitso **NO retiene ISR** — debes declarar
- Bitso reporta a UIF (Ley Antilavado) si > USD $56,000/mes
- Compra/venta de cripto **NO causa IVA** (Art. 14 LIVA)
- Para reporte: usar `bitso_get_ledger` con `operations=trades,fees`

## Validación pendiente

- Tarifa Art. 96 LISR 2026 vigente
- Tasas RESICO PF 2026
- Reglas UIF reporte 2026 (límites pueden cambiar)
- Testimonios con contador especializado en cripto MX

## Tests

```bash
cd /Users/elias/Documents/Trabajo/skills/mcp-servers
.venv/bin/python -m pytest mp_bitso/tests/ -q
```
