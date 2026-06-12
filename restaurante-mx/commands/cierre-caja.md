---
description: Cierre diario de caja — consolida ventas (mesas + barra + delivery), comparativa con consumo teórico de inventario, detecta diferencias.
argument-hint: "[fecha opcional, default hoy]"
allowed-tools: Read, Write, Edit
---

# /restaurante:cierre-caja

Cierre del día: $ARGUMENTS

## Lo que hace

1. Consolida ventas mesas + barra + delivery (aggregators).
2. Compara con consumo teórico de inventario (skill `inventario-merma`).
3. Alerta merma anómala.
4. Genera reporte de cierre.

## Output esperado

```
✓ Cierre día — 2026-03-15

Ventas:
  Mesas:           $18,500  (47%)
  Barra:           $6,800   (17%)
  Rappi:           $7,200   (18%)
  UberEats:        $4,500   (12%)
  DiDi Food:       $2,400   (6%)
─────────────────────────────────
Total:           $39,400 MXN

Cobertura:
  Efectivo:        $14,200
  TDC:             $19,800
  Transferencia:   $5,400

Inventario:
  Consumo teórico: $13,600
  Consumo real:    $14,250
  Merma:           $650 (4.6% — dentro de rango)

⚠ Alertas:
  • Aguacate Hass merma 18% — investigar (esperado 12%)
```
