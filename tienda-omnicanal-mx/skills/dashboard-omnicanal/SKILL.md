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

- Órdenes: `mercadolibre_list_orders`, `amazon_mx_list_orders`, `shopify_list_orders`; stock: `mercadolibre_get_item`, `amazon_mx_get_listing`, `shopify_get_inventory_level`
- Los tres MCPs están "real sin validar (requieren credenciales)": sin credenciales, pide exportaciones CSV de cada panel
- Tienda física: CSV del POS (si usa Soft Restaurant u otro POS, su exportación)
- Conversión (visitas → orden) no la entregan estos MCPs: tómala del panel de cada canal o de GA4 si el usuario la tiene

## Métricas clave

- Ingreso total + por canal (aclarar si es bruto con IVA o neto)
- Ingreso neto por canal = venta sin IVA − cargos del canal − envío absorbido
- Retenciones de plataformas (ML, Amazon) como anticipo, aparte del margen: ISR 2.5% PF/PM con RFC en 2026 (LIF 2026 Art. 25 fr. VI) y 50% del IVA a PF (Art. 18-J LIVA). Cuadra contra el CFDI de retenciones de cada plataforma
- Conversión (visitantes → orden)
- ROAS por canal (si hay ads)
- Stock sincronizado vs desincronizado
- Devoluciones vs baseline
