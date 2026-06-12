---
description: Sincroniza inventario entre todos los canales de venta (Mercado Libre, Shopify, tienda física) detectando discrepancias y aplicando safety stocks. Despacha workflow-sync-multicanal.
argument-hint: "[opcional: SKU específico o --force-canal=ml para sync solo un canal]"
allowed-tools: Read, Write, Edit, Bash, Task
---

# /ecommerce:sync-inventario

Sincroniza stock entre canales: $ARGUMENTS

## Lo que hace

1. **Lee fuente de verdad** (DB local, ERP Aspel/ContPAQi, o canal principal).
2. **Consulta cada canal** en paralelo (ML, Shopify, Amazon, tienda física).
3. **Detecta discrepancias** entre fuente y canales.
4. **Calcula safety stocks** dinámicos según velocidad de venta y delay de webhooks.
5. **Aplica ajustes** automáticamente para resolver sobre-publicación crítica.
6. **Genera alertas** de reposición para SKUs con stock crítico.
7. **Reporta** cambios aplicados, alertas y errores.

## Cómo lo ejecuta

Despacha al subagent `workflow-sync-multicanal` que procesa N canales × M SKUs sin inflar el contexto.

## Cuándo usar

- Cron horario (sync continuo)
- Inmediatamente después de venta importante
- Cuando un cliente reclama "ya no hay stock pero pagó"
- Antes de campaña fuerte (Hot Sale, Buen Fin, Black Friday)
- Audit semanal de salud de inventario

## Output esperado

```
✓ Sync inventario — 2026-06-11 14:30

Total SKUs auditados: 150
Discrepancias detectadas: 8
Ajustes aplicados: 6
  • ABC-123: ML 12→10 (overselling)
  • DEF-456: Shopify 5→2 (sobrepublicado)
  • ...

⚠ Reposición urgente (CRÍTICA):
  • XYZ-789: stock 4, velocidad 2.3/día (1.7 días)
  • GHI-321: stock 2, velocidad 1.8/día (1.1 días)

Errores:
  • Amazon API timeout — retry agendado en 30 min
```

## Filtros opcionales

```
/ecommerce:sync-inventario                      # todos los SKUs, todos los canales
/ecommerce:sync-inventario --sku=ABC-123        # solo un SKU
/ecommerce:sync-inventario --canal=ml           # solo Mercado Libre
/ecommerce:sync-inventario --dry-run            # reporte sin aplicar cambios
```

## Modo simulado

Sin credenciales reales ML/Shopify: el workflow simula 5 SKUs con discrepancias plausibles. Reporta lo que haría sin aplicar cambios.
