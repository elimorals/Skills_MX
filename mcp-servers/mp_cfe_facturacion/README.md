# mp_cfe_facturacion

CFE para descargar facturas CFDI bidireccional.

## Estado

- Sin credenciales: datos de ejemplo marcados `simulated: true`
- ⏳ Path real pendiente — requiere implementar HTTP/API

## Credenciales (para path real)

- `CFE_RPU`
- `CFE_PASSWORD`

## Tools

- `cfe_fact_descargar_factura_mes`
- `cfe_fact_consumo_historico`

## Setup mock

```bash
.venv/bin/python -m mp_cfe_facturacion.server
```
