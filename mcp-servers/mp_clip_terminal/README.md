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
| `CLIP_API_KEY` | API key del dashboard Clip |

Mock-first sin credenciales.

## Tests

```bash
.venv/bin/python -m pytest mp_clip_terminal/tests/ -q
```
