# mp_rappi_partners

MCP para comercios / restaurantes operando en Rappi México.

## Estado

- ✅ Mock-first completo (6 tools)
- ⏳ Path real pendiente — Rappi no tiene API pública. Requiere ser Partner activo y solicitar credenciales (proceso comercial humano).

## Tools

| Tool | Descripción |
|---|---|
| `rappi_listar_ordenes` | Órdenes recientes filtradas por estado |
| `rappi_consultar_orden` | Detalle de una orden |
| `rappi_listar_productos_menu` | Menú actual del comercio |
| `rappi_actualizar_disponibilidad` | Marcar/desmarcar producto disponible |
| `rappi_consultar_ranking_zona` | Posición vs competencia en zona |
| `rappi_estimar_comisiones_mes` | Comisiones del mes (típico 30% gross) |

## Setup mock (default)

```bash
# Sin credenciales → mock-first
.venv/bin/python -m mp_rappi_partners.server
```

## Setup real (humano)

1. Onboarding como Partner Rappi → https://partners.rappi.com
2. Solicitar credenciales API a tu account manager
3. Setear env vars:
   ```bash
   export RAPPI_PARTNERS_TOKEN="..."
   export RAPPI_STORE_ID="..."
   ```
4. Implementar HTTP cliente real en `client.py` (reemplazar los `raise McpError` en cada tool)

## ⚠ Limitaciones

- Comisión 30% es aproximada (varía por zona y categoría)
- Datos mock NO reflejan tu operación real
- Sin webhook real (Rappi no expone webhooks oficiales)
