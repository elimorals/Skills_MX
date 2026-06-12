# mp_telmex_facturacion

Telmex/Telcel para descargar facturas CFDI.

## Estado

- ✅ Mock-first
- ⏳ Path real pendiente — requiere implementar HTTP/API

## Credenciales (para path real)

- `TELMEX_RFC`
- `TELMEX_PASSWORD`

## Tools

- `telmex_fact_descargar_factura_mes` — mock-first
- `telmex_fact_listar_facturas` — mock-first

## Setup mock

```bash
.venv/bin/python -m mp_telmex_facturacion.server
```
