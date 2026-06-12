# mp_cfe_facturacion

CFE para descargar facturas CFDI bidireccional.

## Estado

- ✅ Mock-first
- ⏳ Path real pendiente — requiere implementar HTTP/API

## Credenciales (para path real)

- `CFE_RPU`
- `CFE_PASSWORD`

## Tools

- `cfe_fact_descargar_factura_mes` — mock-first
- `cfe_fact_consumo_historico` — mock-first

## Setup mock

```bash
.venv/bin/python -m mp_cfe_facturacion.server
```
