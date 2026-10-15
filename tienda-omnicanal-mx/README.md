# tienda-omnicanal-mx

Vertical para tiendas que venden en múltiples canales simultáneamente y necesitan sincronización en tiempo real.

> Extensión de `ecommerce-mx`. Score research: **8.5/10**. Mercado: 500k tiendas.

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install tienda-omnicanal-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Diferencia vs `ecommerce-mx`

| `ecommerce-mx` | `tienda-omnicanal-mx` |
|---|---|
| Tienda online individual | Múltiples canales sincronizados |
| 1 inventario | N inventarios sincronizados |
| 1 sistema de órdenes | Inbox unificado |
| Marketplace o tienda propia | Marketplaces + tienda propia + física |

## Skills

1. `dashboard-omnicanal` — ingresos consolidados + por canal
2. `sync-inventario-multicanal` — stock en tiempo real
3. `pricing-dinamico-por-canal` — margen objetivo + ajuste por canal
4. `ordenes-unificadas-inbox` — todas las plataformas en un solo lugar
5. `devoluciones-cruzadas-canal` — compré online, devuelvo en tienda

## Dependencias

- `core-mexico` (CFDI, RFC, etc.)
- `ecommerce-mx` (skills de ML, Shopify)
- MCPs: `mp_mercado_libre`, `mp_shopify_mx`, `mp_amazon_mx_seller`, `mp_facturama_extendido`
