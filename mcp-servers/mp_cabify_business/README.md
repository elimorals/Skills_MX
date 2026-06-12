# mp_cabify_business — Movilidad corporativa MX

## Tools (6)

| Tool | Propósito |
|---|---|
| `cabify_schedule_ride` | Agendar viaje con centro de costos |
| `cabify_list_rides` | Listar con filtros |
| `cabify_get_ride` | Detalle (driver, distancia, precio) |
| `cabify_cancel_ride` | Cancelar (fee según razón) |
| `cabify_generate_invoice` | CFDI mensual consolidado |
| `cabify_listar_catalogos` | Vehículos, status, ciudades |

## Tests

```bash
.venv/bin/python -m pytest mp_cabify_business/tests/ -q
```
