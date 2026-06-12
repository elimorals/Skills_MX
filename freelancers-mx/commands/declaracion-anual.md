---
description: Genera borrador de declaración anual ISR para Persona Física (PFAE / RESICO PF). Descarga año completo de CFDIs, calcula deducciones personales Art. 151, aplica tarifa, compara contra pagos provisionales.
argument-hint: "[ejercicio fiscal, ej. '2025']"
allowed-tools: Read, Write, Edit, Bash, Task
---

# /freelancers:declaracion-anual

Declaración anual: $ARGUMENTS

## Lo que hace

Despacha `workflow-pf-anual-completa` que orquesta:
1. Descarga masiva CFDIs emitidos+recibidos del año (12 meses)
2. Cruce con estados de cuenta bancarios
3. Identificación de deducciones personales (Art. 151 LISR)
4. Cálculo ISR anual según régimen
5. Comparativa con pagos provisionales acumulados
6. Generación de borrador

## Cuándo usar

- Antes del **30 abril** (deadline obligatorio)
- Para revisar año anterior antes de presentar
- Para PF con ingresos por honorarios, arrendamiento, RESICO

## Output esperado

```
✓ Declaración Anual 2025 — Persona Física (PFAE)

Ingresos acumulables:      $1,240,000 MXN
Deducciones acumulables:    $285,000
Deducciones personales:     $145,000
─────────────────────────────────────
Utilidad fiscal:            $810,000

ISR anual calculado:        $165,000
Pagos provisionales:       -$145,000
Retenciones ISR:           -$24,000
─────────────────────────────────────
Diferencia:                 -$4,000  (SALDO A FAVOR)

Fecha límite: 30 abril 2026

⚠ Validar con contador certificado antes de presentar al SAT.
   Tarifa Art. 96 LISR usada es la publicada en RMF 2025.
```
