# mp_telmex_facturacion

Telmex/Telcel para descargar facturas CFDI.

## Estado

- Sin credenciales: datos de ejemplo marcados `simulated: true`
- ⏳ Path real pendiente — requiere implementar HTTP/API

## Credenciales (para path real)

- `TELMEX_RFC`
- `TELMEX_PASSWORD`

## Tools

- `telmex_fact_descargar_factura_mes`
- `telmex_fact_listar_facturas`

## Setup mock

```bash
.venv/bin/python -m mp_telmex_facturacion.server
```
