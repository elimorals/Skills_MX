---
name: inventario-multicanal
description: Sincronización de inventario entre múltiples canales de venta (Mercado Libre, Shopify, Amazon MX, tienda física) para evitar overselling, detección de discrepancias entre canales, regla de safety stock por canal según velocidad de venta, y reposición automática. Útil para sellers operando en 2+ marketplaces. Usar cuando el usuario diga sincronizar inventario, stock multicanal, overselling, inventario ML Shopify, vendí lo mismo en dos lados, stock desincronizado, safety stock. NO usar para pricing (otro skill) ni para fulfillment individual (otro skill paqueteria-mx).
allowed-tools: Read, Write, Edit, Bash
---

# Inventario multicanal — sincronización para evitar overselling

Vender el mismo SKU en 2+ canales sin sync = overselling = cancelaciones = penalizaciones de plataforma.

## Problema base

Tienes 10 unidades del producto X:
- Mercado Libre publicado con stock=10
- Shopify publicado con stock=10
- Total publicado: 20 unidades (¡pero solo tienes 10!)

Si se venden 6 en ML y 5 en Shopify ese día: cancelación obligada de 1 venta → penalización + cliente molesto.

## Estrategias de sincronización

### Estrategia A: SKU centralizado (recomendada)
- Una fuente de verdad: tu base de datos local (o ERP, o sheet)
- Cada canal lee stock vía API y publica
- Cuando se vende en cualquier canal: webhook actualiza la fuente → propaga a otros canales

### Estrategia B: Split fijo por canal
- 50% stock en ML, 50% en Shopify
- Más simple, menos óptimo
- Útil si los canales venden a velocidades muy distintas

### Estrategia C: Canal principal + secundarios
- 100% del stock en ML (canal principal)
- Shopify publicado con stock 0 si ML tiene stock < N
- Útil cuando un canal vende 80%+ del volumen

## Safety stock por canal

Reservar buffer para evitar overselling por delays de webhook:

```
safety_stock(canal) = max(1, ventas_diarias_promedio × tiempo_delay_webhook_horas / 24)

Ejemplos:
- ML vende 5/día, webhook ~30s delay → safety stock = 1
- Shopify vende 2/día, webhook instant → safety stock = 1
- Tienda física vende 8/día, sync diario → safety stock = 8
```

## Reglas de propagación

Cuando se vende 1 unidad en ML:

```
nuevo_stock_real = stock_anterior - 1
publicado_ml = nuevo_stock_real - safety_stock_otros
publicado_shopify = max(0, nuevo_stock_real - safety_stock_ml)
publicado_amazon = max(0, nuevo_stock_real - safety_stock_ml - safety_stock_shopify)
```

Si `nuevo_stock_real <= sum(safety_stocks)`: **PAUSAR** todos los canales menos el principal.

## Detección de discrepancias

Periódicamente (diario o cada 6h):

```
para cada SKU:
  stock_real = leer_base_de_datos(sku)
  stock_ml = mp_mercado_libre.get_stock(sku)
  stock_shopify = mp_shopify_mx.get_stock(sku)

  discrepancia_ml = abs(stock_real - stock_ml) > 1
  discrepancia_shopify = abs(stock_real - stock_shopify) > 1

  si hay discrepancia: alerta + log para investigación manual
```

Causas comunes:
- Webhook perdido (timeout, error)
- Cancelación en un canal no propagada
- Devolución sin reingreso a stock
- Ajuste manual en un canal sin actualizar fuente

## Casos edge

### 1. Bundles (paquetes)
Producto B = 2× SKU X + 1× SKU Y. Vender bundle = restar 2 X y 1 Y. Validar disponibilidad ANTES de aceptar venta del bundle.

### 2. Variantes (talla, color)
Cada variante tiene su SKU independiente. Sync por variante, no por producto padre.

### 3. Stock virtual (dropshipping)
Tu proveedor maneja stock. Sincronizar vía API de proveedor o pull diario.

### 4. Devoluciones
Cliente devuelve → producto regresa al stock disponible (si está vendible). Validar estado del producto antes de reingresar.

### 5. Pre-órdenes
Producto sin stock real pero permitir compra con entrega futura. Marcar `available_for_preorder: true` y fecha estimada.

## Velocidad de venta y reposición

```
velocidad_diaria = promedio_ventas_ultimos_7_dias
dias_stock_disponible = stock_real / velocidad_diaria
dias_lead_time_proveedor = 14 (ejemplo)

si dias_stock_disponible < (dias_lead_time + safety_days):
  alerta_reposicion(sku, "ordenar AHORA")
```

## Output estructurado

```json
{
  "audit_inventario": {
    "fecha": "2026-06-11",
    "total_skus": 150,
    "canales_monitoreados": ["mercado_libre", "shopify", "tienda_fisica"],
    "skus_sincronizados": 142,
    "discrepancias": [
      {
        "sku": "ABC-123",
        "stock_real": 5,
        "stock_ml": 8,
        "stock_shopify": 5,
        "diff_ml": 3,
        "causa_probable": "webhook venta ML no procesado",
        "accion": "ajustar ML a 5 inmediatamente"
      }
    ],
    "alertas_reposicion": [
      {
        "sku": "XYZ-789",
        "stock_actual": 4,
        "velocidad_diaria": 2.3,
        "dias_disponible": 1.7,
        "lead_time_proveedor": 14,
        "urgencia": "CRITICA"
      }
    ],
    "overselling_riesgo": [
      {
        "sku": "DEF-456",
        "stock_real": 2,
        "stock_publicado_total": 8,
        "riesgo": "alto"
      }
    ]
  },
  "siguientes_pasos": [
    "Reconciliar SKU ABC-123 manual",
    "Pedir reposición XYZ-789 al proveedor HOY",
    "Reducir stock publicado de DEF-456 en Shopify"
  ]
}
```

## Comando relacionado

```
/ecommerce:sync-inventario
```

Despacha workflow que:
1. Lee stock real (DB o ERP)
2. Compara con cada canal vía MCPs (`mp_mercado_libre`, `mp_shopify_mx`, etc.)
3. Detecta discrepancias
4. Aplica ajustes considerando safety stocks
5. Reporta cambios y alertas de reposición

## Validación pendiente

- Velocidad de propagación real de webhooks por canal
- Comportamiento devoluciones cross-channel
- Testimonios con sellers MX operando 3+ canales
- Edge cases de bundles + variantes simultáneos

## Ver también

- `mercado-libre-listings`
- `shopify-mx`
- `paqueteria-mx`
- `mp_mercado_libre` y `mp_shopify_mx` MCPs
