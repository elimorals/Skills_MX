---
name: dashboard-omnicanal
description: Dashboard consolidado de tienda omnicanal con ingresos del día/semana/mes desglosados por canal (Mercado Libre, Amazon MX, Shopify propio, tienda física), top productos cross-channel, conversión por canal, y semáforo de items críticos (stock bajo en algún canal, ventas anómalas, devoluciones por arriba del baseline). Usar cuando el usuario diga dashboard tienda, ventas multicanal, como van mis canales, status omnicanal. NO usar para vista de un solo canal (eso es skills específicos de ecommerce-mx).
allowed-tools: Read, Write
---

# Dashboard omnicanal

## Output

```
═══════════════════════════════════════════════════════════════
  Dashboard omnicanal — 2026-06-12 (semana en curso)
═══════════════════════════════════════════════════════════════

💰 Ingresos consolidados semana: $145,800 MXN (+12% vs anterior)

📊 Por canal:
  Mercado Libre    $58,200  40% — 142 órdenes — conv 3.2%
  Amazon MX        $32,400  22% —  68 órdenes — conv 2.1%
  Shopify propio   $42,100  29% —  95 órdenes — conv 4.8%
  Tienda física    $13,100   9% —  31 órdenes

🏆 Top 5 productos cross-channel:
  1. SKU-001 — vendido en 4 canales — 89 unidades
  2. SKU-007 — vendido en 3 canales — 64 unidades
  ...

⚠ Alertas:
  • SKU-005: stock < 5 en Shopify (ML+Amazon en 50+) → desincronizado
  • SKU-012: devoluciones 18% (baseline 4%) → revisar calidad
  • Amazon: 2 órdenes con tiempo respuesta > 24h → impacta rating
```

## Data sources

- `mp_mercado_libre`, `mp_amazon_mx_seller`, `mp_shopify_mx`
- POS/tracker tienda física (CSV manual o API si existe)

## Métricas clave

- Ingreso total + por canal
- Conversión (visitantes → orden)
- ROAS por canal (si hay ads)
- Stock sincronizado vs desincronizado
- Devoluciones vs baseline
