---
description: Cotiza una boda completa con desglose por capítulos (banquete, locación, decoración, etc.) en rangos low/mid/high.
argument-hint: "[invitados, ciudad, día semana, temporada]"
allowed-tools: Read, Write, Edit
---

# /wedding:cotizar-boda

Cotiza boda: $ARGUMENTS

## Lo que hace

1. Skill `cotizacion-boda-mxn` para desglose por 12 capítulos.
2. Aplica ajustes por día, temporada, ciudad.
3. Genera 3 escenarios: low, mid, high.
4. Suma buffer de imprevistos (10% recomendado).

## Output esperado

```
✓ Cotización boda — 200 invitados, CDMX, sábado abril 2027

Mid-tier estimado: $1,250,000 MXN ($6,250/persona)

Por capítulo:
  Banquete + bebidas:  $480k  (38%)
  Locación:            $180k  (14%)
  Decoración:           $90k  (7%)
  Música DJ:            $60k  (5%)
  Fotografía + video:   $70k  (6%)
  ...

Buffer imprevistos:    $125k  (10%)
─────────────────────────────────
Total presupuesto:    $1,375k

Comparativa:
  Low:    $628k  ($3,140/persona)
  Mid:   $1,250k  ($6,250/persona)
  High: $2,900k+ ($14,500/persona)
```
