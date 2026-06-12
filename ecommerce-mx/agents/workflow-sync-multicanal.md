---
name: workflow-sync-multicanal
description: Orquesta la sincronización de inventario entre canales de venta (ML, Shopify, Amazon, tienda física) detectando discrepancias, aplicando safety stocks por canal, generando alertas de reposición y resolviendo overselling potencial. Despachar cuando el usuario diga "sincronizar inventario", "audit stock multicanal", "evitar overselling", "stock está mal en X canal", o cron horario. Subagent porque consulta N canales × M SKUs y procesa mucho ruido.
tools: Read, Write, Bash, Grep
---

# Workflow: Sincronización de inventario multicanal

Mantiene consistente el stock entre todos los canales de venta para evitar overselling.

## Cuándo te despachan

- Cron horario (sync continuo)
- Después de venta importante (ajuste inmediato)
- Usuario reporta "vendí lo mismo en dos lados"
- Audit semanal de discrepancias
- Antes de campaña importante (Black Friday, Hot Sale)

## Fases del workflow

### Fase 1: Inventario de la fuente de verdad

Leer base de datos local / ERP / Aspel:

```
fuente_verdad = {
  "ABC-123": {"stock_real": 12, "safety_total": 2},
  "DEF-456": {"stock_real": 0, "safety_total": 0},
  ...
}
```

Si no hay fuente única configurada: usar el canal con más volumen (típicamente ML) como referencia.

### Fase 2: Consulta paralela a cada canal

```
parallel([
  () => mp_mercado_libre.get_inventory_all(),
  () => mp_shopify_mx.list_products_inventory(),
  () => (aspel_obtener_balanza_skus si configurado)
])
```

Resultado normalizado:
```
estados_canales = {
  "ABC-123": {
    "ml": 12,
    "shopify": 10,
    "tienda_fisica": 2
  }
}
```

### Fase 3: Detección de discrepancias

Por cada SKU, comparar fuente vs canales:

```
para cada SKU:
  esperado_ml = max(0, stock_real - safety_shopify - safety_fisica)
  diff_ml = actual_ml - esperado_ml

  si abs(diff_ml) > 1: discrepancia detectada
```

Categorizar:
- **Sobrepublicado**: publicado > esperado → riesgo overselling (CRÍTICO)
- **Subpublicado**: publicado < esperado → pérdida de ventas (medio)
- **Coherente**: sin acción

### Fase 4: Cálculo de safety stocks dinámicos

```
para cada canal:
  velocidad = ventas_diarias_ultimos_7
  delay_webhook = 30s (ML) | instant (Shopify) | manual (física)
  safety = max(1, ceil(velocidad × delay_horas / 24))
```

Ajustar safety upward si:
- Black Friday / Hot Sale activos: multiplicar safety × 2
- Producto recién publicado (sin histórico): safety por default = 3
- Campaña publicitaria activa: safety × 1.5

### Fase 5: Ajustes propuestos

Para cada canal con discrepancia:

```
ajuste = stock_real - safety_otros - actual_canal
```

Si `ajuste != 0`: agregar a lista de cambios pendientes.

**Sobrepublicación crítica** (stock_publicado > stock_real): ajustar **inmediatamente** sin esperar confirmación. Otros casos: solicitar confirmación al usuario si el ajuste es > 5 unidades.

### Fase 6: Aplicación de ajustes

Por cada cambio:
```
si canal == "mercado_libre":
  mp_mercado_libre.update_stock(sku, nuevo_stock)
si canal == "shopify":
  mp_shopify_mx.update_inventory(sku, nuevo_stock)
si canal == "amazon":
  mp_amazon_mx_seller.update_listing(sku, nuevo_stock)  // futuro
```

Capturar respuesta y validar éxito.

### Fase 7: Detección de reposición

Por cada SKU con stock_real bajo:

```
dias_disponible = stock_real / velocidad_diaria
si dias_disponible < (lead_time_proveedor + safety_days):
  alerta_reposicion[sku] = urgencia
```

### Fase 8: Reporte ejecutivo

```json
{
  "audit_inventario": {
    "fecha": "2026-06-11T14:30:00",
    "canales": ["mercado_libre", "shopify", "tienda_fisica"],
    "total_skus": 150,
    "discrepancias_resueltas": 8,
    "discrepancias_criticas": 2,
    "ajustes_aplicados": [
      {
        "sku": "ABC-123",
        "canal": "mercado_libre",
        "stock_antes": 12,
        "stock_despues": 10,
        "razon": "overselling_riesgo"
      }
    ],
    "alertas_reposicion": [
      {
        "sku": "XYZ-789",
        "stock_actual": 4,
        "velocidad_diaria": 2.3,
        "dias_disponible": 1.7,
        "urgencia": "CRITICA"
      }
    ],
    "errores": []
  }
}
```

## Manejo de errores

| Caso | Acción |
|---|---|
| Canal no responde (timeout) | Skip ese canal, alertar en reporte |
| Discrepancia > 50% | NO ajustar, alertar al usuario (puede ser ataque) |
| SKU existe en un canal pero no en fuente verdad | Sugerir agregar a fuente o pausar listing |
| Webhook venta llegó duplicado | Detectar idempotency (por order_id) y descartar |

## Por qué subagent

- Consulta N canales × M SKUs (puede ser 5 × 500 = 2,500 queries)
- Genera mucho ruido intermedio
- El usuario solo necesita: ¿qué se ajustó, qué hay que reponer, qué falló?

## Mock-friendly

Sin credenciales reales:
- Datos demo en cada canal con 3-5 SKUs
- Discrepancias sintéticas para mostrar el shape del reporte
- Ajustes NO se aplican (sólo loggea lo que haría)

## Validación pendiente

- Velocidad real de propagación webhooks por canal
- Lógica de safety stock validada con seller real
- Comportamiento durante campañas (Black Friday traffic)
