# mp_clip_terminal — MCP para Clip (POS MX)

## Tools (6)

| Tool | Propósito |
|---|---|
| `clip_list_charges` | Lista de cobros con filtros |
| `clip_get_charge` | Detalle de un charge (comisión, neto) |
| `clip_refund_charge` | Refund total o parcial |
| `clip_terminal_status` | Status terminal (batería, señal, txs/24h) |
| `clip_get_settlement` | Liquidación T+1 a tu banco |
| `clip_listar_catalogos` | Terminales, comisiones, status |

## Configuración

| Variable | Propósito |
|---|---|
| `CLIP_API_KEY` | API key del Panel de Desarrollador de Clip |
| `CLIP_SECRET_KEY` | Clave secreta de la misma credencial (token `Basic base64(key:secret)`) |

Sin credenciales responde datos de ejemplo (`simulated: true`).

## Tests

```bash
.venv/bin/python -m pytest mp_clip_terminal/tests/ -q
```

## Estado real (2026-10-14)

- ✅ Reescrito contra la referencia oficial de [developer.clip.mx](https://developer.clip.mx/llms.txt):
  `GET api-gw.payclip.com/payments` y `/payments/receipt-no/{receipt_no}`, `POST api.payclip.com/refunds`,
  `GET api.payclip.io/f2f/pinpad/v1/devices/status` y `GET api-gw.payclip.com/settlements` (header `x-api-key`).
  Los endpoints anteriores (`/v1/charges`, `/v1/terminals`, `/v1/settlements/{fecha}`, auth `Bearer`) no existían.
- ⚠️ **Sin validar en vivo**: falta una credencial de pruebas de Clip.
- `charge_id` es el número de recibo de Clip. Reembolso sin monto = total del recibo.
