# mp_trustly_mx — MCP para Trustly MX (open banking)

Open banking en MX: pagos por transferencia bancaria directa autorizada por el cliente desde su banco (sin TDC).

## Tools (5)

| Tool | Propósito |
|---|---|
| `trustly_create_payment` | Crear solicitud de pago (link/QR para banco del cliente) |
| `trustly_get_payment` | Status actual (pending, completed, failed) |
| `trustly_list_payments` | Listar con filtros |
| `trustly_refund_payment` | Devolver fondos al pagador |
| `trustly_listar_catalogos` | Status, bancos soportados, webhook events |

## Configuración

| Variable | Propósito |
|---|---|
| `TRUSTLY_API_KEY` | API key (sandbox `key_test_*`, producción `key_live_*`) |
| `TRUSTLY_ENV` | `sandbox` (default) o `production` |

Mock-first sin credenciales.

## Casos de uso

- **Alternativa OXXO/SPEI manual**: cliente paga desde su banco sin teclear datos
- **B2B con cuentas empresariales**: transferencia automatizada
- **Reduce contracargos**: no hay TDC = no hay chargeback
- **Costo menor** que TDC (~1.5-2.5% vs 3.6%)

## Tests

```bash
cd /Users/elias/Documents/Trabajo/skills/mcp-servers
.venv/bin/python -m pytest mp_trustly_mx/tests/ -q
```

## Estado real (2026-10-14)

- ❌ **Trustly no opera en México.** Sus mercados documentados son Europa y Norteamérica, y los
  endpoints que usaba este cliente (`api.trustly.com/v1/...`) no existen.
- Con `TRUSTLY_API_KEY`, cada tool devuelve `ConfigError` `motivo: sin_api_publica`.
  Para cobros por SPEI usa Conekta o Mercado Pago, y valida transferencias con `mp_banxico_cep`.
- Sin credenciales responde datos simulados `simulated: true` (solo demos).
