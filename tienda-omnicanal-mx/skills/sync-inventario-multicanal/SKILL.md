---
name: sync-inventario-multicanal
description: Sincroniza inventario entre Mercado Libre, Amazon MX, Shopify, y tienda física en tiempo real (o batch periódico). Cuando se vende una unidad en cualquier canal, descuenta del stock real y propaga a los otros canales para evitar overselling. Útil para tiendas con < 5,000 SKUs (mayor escala requiere ERP/WMS dedicado). Usar cuando el usuario diga sincronizar inventario, stock multicanal, evitar overselling, sync canales. NO usar para inventario único (eso es ecommerce-mx tradicional).
allowed-tools: Read, Write
---

# Sync inventario multicanal

## Patrón típico

```
Stock_real = max(0, Stock_inicial - ventas_acumuladas_todos_canales)

Por cada canal:
  if stock_publicado_canal != stock_real:
      actualizar_canal(sku, stock_real - safety_stock_otros_canales)   # ver inventario-multicanal
```

## Frecuencia

- **Tiempo real** vía webhooks/notificaciones de cada canal (ML y Shopify los ofrecen; Amazon vía SP-API Notifications). Los MCPs del repo no reciben webhooks: hace falta un endpoint propio
- **Batch** cada 15-30 min via cron como fallback

## Output del sync run

```json
{
  "fecha_run": "2026-06-12T10:30:00Z",
  "skus_procesados": 245,
  "skus_actualizados": 12,
  "skus_omitidos_sincronizados": 233,
  "errores": [],
  "alertas": [
    {"sku": "SKU-005", "stock_real": 3, "stock_publicado_ml": 35, "diferencia_critica": true}
  ],
  "duracion_ms": 4250
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Venta simultánea en 2 canales (race condition) | Lock con reserva temporal + reconciliar |
| Stock negativo por sobreventa | Marcar oversold, contactar cliente |
| Canal con stock desactualizado > 6h | Re-sync forzoso |
| Producto descontinuado en 1 canal | Marcar fuera de venta en todos |
| Reposición física (entrada nueva mercancía) | Update batch de todos |

## Dependencias

- Tools: `mercadolibre_update_stock`, `amazon_mx_update_inventory`, `shopify_update_inventory_level` (lectura: `mercadolibre_get_item`, `amazon_mx_get_listing`, `shopify_get_inventory_level`). Los tres MCPs están "real sin validar (requieren credenciales)"; sin ellas, genera el archivo de carga masiva de cada canal para que el usuario lo suba
- Tracker maestro de SKUs en local
