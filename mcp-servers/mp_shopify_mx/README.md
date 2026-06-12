# mp_shopify_mx — MCP wrapper Shopify específico MX

Conecta con Shopify Admin API con utilidades específicas para mercado mexicano (cálculo IVA por región, paqueterías MX, gateways de pago locales).

## Tools (11)

### Productos e inventario
| Tool | Propósito | Mock |
|---|---|---|
| `shopify_list_products` | Lista productos con paginación | Sí |
| `shopify_get_product` | Detalle de producto (cache 10 min) | Sí |
| `shopify_get_inventory_level` | Stock de SKU en sucursal | Sí |
| `shopify_update_inventory_level` | Setea stock (absoluto, idempotente) | Sí |

### Órdenes
| Tool | Propósito | Mock |
|---|---|---|
| `shopify_list_orders` | Lista órdenes con filtros | Sí |
| `shopify_get_order` | Detalle de orden (cache 2 min) | Sí |

### Fulfillment
| Tool | Propósito | Mock |
|---|---|---|
| `shopify_create_fulfillment` | Marca orden como enviada con tracking | Sí |

### Customers + webhooks
| Tool | Propósito | Mock |
|---|---|---|
| `shopify_get_customer` | Datos del cliente (cache 15 min) | Sí |
| `shopify_list_webhooks` | Webhooks configurados | Sí |

### Utility MX (local, sin red)
| Tool | Propósito |
|---|---|
| `shopify_calculate_tax_mx` | IVA según región (general 16%, frontera 8%, exento 0%) |

### Discovery
| Tool | Propósito |
|---|---|
| `shopify_listar_catalogos` | Status órdenes, paqueterías MX, gateways, webhook topics |

## Configuración

| Variable | Propósito |
|---|---|
| `SHOPIFY_SHOP` | Tienda (ej. `mitienda.myshopify.com`) |
| `SHOPIFY_ACCESS_TOKEN` | Access token de custom app (empieza con `shpat_`) |
| `SHOPIFY_API_VERSION` | Versión API (default `2024-10`) |
| `PLUGINS_MX_MOCK=1` | Forzar mock |

## Cómo obtener access token

1. Login a Shopify Admin como owner
2. Settings → Apps and sales channels → Develop apps
3. Create an app → Configure Admin API scopes
4. Permisos necesarios: `read_products`, `write_products`, `read_inventory`, `write_inventory`, `read_orders`, `write_orders`, `read_customers`, `read_fulfillments`, `write_fulfillments`
5. Install app → Reveal access token once → guardar

## Casos de uso

### Sync inventario tras venta ML
```python
# Cuando se vende algo en Mercado Libre, restar de Shopify:
await shopify_update_inventory_level(
    inventory_item_id="123",
    location_id="456",
    available=current_stock - 1,
)
```

### Marcar orden Shopify como enviada
```python
# Después de generar guía de Estafeta:
await shopify_create_fulfillment(
    order_id="1000001",
    tracking_number="9320XXX",
    tracking_company="Estafeta",
    notify_customer=True,
)
```

### Calcular IVA antes de mostrar precio
```python
tax = await shopify_calculate_tax_mx(
    subtotal_mxn=1000.00,
    region="frontera_norte",  # 8% en lugar de 16%
)
# tax["total_mxn"] = 1080.00
```

## Notas MX

- **NO usar Shopify Payments** (no opera en MX). Usar Conekta o MercadoPago.
- **`tax_inclusive=true`** en Shopify Settings (precios deben incluir IVA en MX).
- **CFDI**: Shopify NO emite. Usar app Facturama Shopify o webhook → `mp_facturama_extendido`.
- **Paqueterías**: integrar Estafeta, DHL MX, FedEx MX, 99 Minutos. Lista completa en `shopify_listar_catalogos`.

## Tests

```bash
cd /Users/elias/Documents/Trabajo/skills/mcp-servers
.venv/bin/python -m pytest mp_shopify_mx/tests/ -q
```
