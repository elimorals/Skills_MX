---
description: Recalcula precios en Mercado Libre y Shopify considerando comisión, margen objetivo, posición competitiva y reputación del vendedor. Aplica cambios o reporta sugerencias.
argument-hint: "[SKU específico o --todos para optimizar todo el catálogo]"
allowed-tools: Read, Write, Edit, Bash
---

# /ecommerce:optimizar-pricing

Optimiza precios del catálogo: $ARGUMENTS

## Lo que hace

1. Invoca skill `mercado-libre-pricing` para calcular precio óptimo por SKU.
2. Compara precio actual vs sugerido (con tolerancia de 1-3%).
3. Analiza posición competitiva contra mediana y P25/P75 de competidores.
4. Considera reputación actual del vendedor (MercadoLíder Platinum/Gold/Estándar).
5. Sugiere ajustes o aplica automáticamente con `--apply`.

## Cuándo usar

- Semanal: review de pricing del catálogo
- Cuando entra competidor agresivo
- Mensual: ajuste por inflación o cambio comisión ML
- Antes de campaña (Hot Sale): pricing competitivo

## Output esperado

```
✓ Análisis pricing — 150 SKUs

Sugerencias por categoría:
  Subir precio (margen bajo):  12 SKUs
  Bajar precio (no competitivo): 18 SKUs
  Mantener: 120 SKUs

Top 5 cambios sugeridos:
  • ABC-123: $399 → $445 (+11.5%, margen sube a 22%)
  • DEF-456: $720 → $649 (-9.9%, posición P25, mejor ranking)
  • ...

Total impacto estimado:
  Margen incremental mensual: +$8,500 MXN
  Visibilidad ranking: +15% en 8 SKUs

Para aplicar: /ecommerce:optimizar-pricing --apply
```

## Modo dry-run vs apply

```
/ecommerce:optimizar-pricing                # solo reporta (default)
/ecommerce:optimizar-pricing --apply        # aplica cambios automáticamente
/ecommerce:optimizar-pricing --umbral=5     # solo cambios > 5%
```
