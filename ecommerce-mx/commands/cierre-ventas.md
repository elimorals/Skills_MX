---
description: Cierre diario o mensual de ventas (consolidar ventas todos los canales, generar CFDI público global B2C, verificar reconciliación con pagos, reportar ranking de productos top).
argument-hint: "[periodo: 'hoy', 'ayer', 'marzo 2026', '2026-03']"
allowed-tools: Read, Write, Edit, Bash, Task
---

# /ecommerce:cierre-ventas

Cierre de ventas del periodo: $ARGUMENTS

## Lo que hace

1. **Consolida ventas** de todos los canales del periodo:
   - Mercado Libre (`mp_mercado_libre.list_orders`)
   - Shopify (`mp_shopify_mx.list_orders`)
   - Tienda física (si Aspel/ContPAQi configurado)
2. **Cruza con pagos** (`mp_mercado_pago.list_payments` + `mp_conekta.list_orders`).
3. **Identifica ventas sin CFDI**: lista órdenes que requieren factura B2B o público global.
4. **Genera CFDI público global** B2C (mensual) si aplica.
5. **Detecta cancelaciones / reembolsos** pendientes.
6. **Calcula métricas**:
   - Total facturado
   - Ticket promedio
   - Productos top
   - Canal con mejor conversión
   - Margen estimado

## Cuándo usar

- Cierre diario al cierre de operaciones
- Cierre mensual para declaración fiscal
- Auditoría retroactiva
- Revisión semanal de performance

## Output esperado

```
✓ Cierre de ventas — marzo 2026

Ingresos consolidados:
  Mercado Libre:    $124,800 MXN (48 órdenes)
  Shopify:          $87,500 MXN (32 órdenes)
  Tienda física:    $35,200 MXN (15 órdenes)
  ─────────────────────────────────
  TOTAL:           $247,500 MXN (95 órdenes)

Ticket promedio:   $2,605 MXN
Productos top:
  1. iPhone 15 Pro 256GB:   12 vendidos ($299,880)
  2. AirPods Pro 2da gen:    8 vendidos ($28,000)
  3. iPad Air M2 11":        5 vendidos ($60,000)

CFDI status:
  ✓ B2B emitidos individualmente: 22
  ✓ B2C consolidados (público global): 1 CFDI por $189,500
  ⚠ 3 órdenes Shopify pendientes de CFDI (cliente no proporcionó RFC)

Cancelaciones:
  ML: 2 ($5,400)
  Shopify: 1 ($1,200)

Siguientes pasos:
  • Cobrar 4 órdenes en cartera
  • Emitir CFDI a 3 clientes que sí dieron RFC tras checkout
  • /freelancers:cierre-fiscal para pago provisional
```

## Filtros

```
/ecommerce:cierre-ventas hoy
/ecommerce:cierre-ventas ayer
/ecommerce:cierre-ventas marzo 2026
/ecommerce:cierre-ventas --canal=ml --periodo=mes
```
