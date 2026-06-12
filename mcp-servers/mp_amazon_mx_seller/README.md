# mp_amazon_mx_seller — MCP para Amazon MX SP-API

⚠ Mock-first. Path real (LWA + AWS Sig V4) requiere ~80-120h dev — NO implementado.

## Tools (7)

| Tool | Propósito |
|---|---|
| `amazon_mx_list_listings` | Listings con filtros |
| `amazon_mx_get_listing` | Detalle SKU + comisión + neto |
| `amazon_mx_update_inventory` | Cambiar stock SKU |
| `amazon_mx_list_orders` | Órdenes con filtros |
| `amazon_mx_get_order` | Detalle orden |
| `amazon_mx_get_fees_estimate` | Estimación comisión + FBA antes de pricing |
| `amazon_mx_listar_catalogos` | Marketplace ID, status, comisiones |

## Marketplace MX

- ID: `A1AM78C64UM0Y8`
- Comisiones referral: 6-17% según categoría
- FBA fees: $25-245+ según peso/dimensión
- Storage fee FBA: ~$12/m por unidad estándar

## Tests

```bash
.venv/bin/python -m pytest mp_amazon_mx_seller/tests/ -q
```
