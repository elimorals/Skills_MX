---
description: Workflow completo de cierre fiscal mensual (descarga CFDIs SAT, cruza con bancos, calcula pago provisional ISR/IVA, detecta alertas críticas como 69-B). Despacha workflow-cierre-fiscal-mensual.
argument-hint: "[mes y año, ej. 'marzo 2026' o '2026-03']"
allowed-tools: Read, Write, Edit, Bash, Task
---

# /freelancers:cierre-fiscal

Cierra fiscalmente el mes: $ARGUMENTS

## Lo que hace

1. **Descarga datos** del SAT en paralelo:
   - CFDIs emitidos del mes
   - CFDIs recibidos del mes
   - Buzón Tributario (notificaciones pendientes)
   - TCs DOF + UMA + INPC del mes
2. **Cruza ingresos**: CFDIs emitidos vs depósitos bancarios → cartera vencida + depósitos sin facturar
3. **Cruza gastos**: CFDIs recibidos vs cargos bancarios → deducibles vs no deducibles
4. **Detecta alertas críticas**:
   - Proveedores en lista 69-B (no deducibles)
   - Retenciones sin acreditar
   - Depósitos en efectivo > $15k
   - Multimoneda con TC anómalo
5. **Calcula pago provisional** ISR + IVA según régimen (RESICO_PF, PFAE, PM)
6. **Reporte ejecutivo** con total a pagar y lista de acciones requeridas

## Cómo lo ejecuta

Despacha al subagent `workflow-cierre-fiscal-mensual` (en `core-mexico/agents/`) que coordina 5 MCPs y procesa potencialmente cientos de CFDIs sin inflar el contexto.

## Cuándo usar

- Día 14 del mes (cron sugerido) — cierre del mes anterior
- Antes de presentar declaración mensual
- Auditoría retroactiva de un mes específico
- Después de cambio de régimen para validar primer cierre

## Output esperado

```
✓ Cierre fiscal — marzo 2026 (RESICO_PF)

Ingresos cobrados:       $220,000 MXN
Gastos deducibles:        $85,000 MXN
Pago provisional ISR:      $4,400 MXN (1.5%)
Pago provisional IVA:     $12,000 MXN
─────────────────────────────────────
TOTAL A PAGAR:            $16,400 MXN
Fecha límite:           17 abr 2026

⚠ Alertas críticas:
  • RFC proveedor en 69-B PRESUNTO: $15,000 no deducibles
  • Buzón Tributario: requerimiento vence 5 abr
  • 2 CFDIs PPD sin REP — emitir o cancelar
  • Cartera vencida: $30,000 en 3 clientes

Siguientes pasos:
  1. Generar línea de captura en portal SAT
  2. Resolver requerimiento Buzón
  3. /freelancers:cobranza-mensual para los morosos
  4. Refacturar o cancelar gastos con proveedor 69-B
```

## Filtros opcionales

```
/freelancers:cierre-fiscal marzo 2026
/freelancers:cierre-fiscal --mes=2026-03 --incluir-buzon=false
/freelancers:cierre-fiscal Q1-2026  # cierre trimestral
```

## Validación pendiente

⚠ Las tarifas de ISR y RESICO usadas por el workflow pueden estar desactualizadas. El reporte llevará marca `vigencia_validada: false` hasta que un contador certifique los valores 2026 contra portal SAT.

**No pagar al SAT basándose solo en este cálculo sin validación humana.**

## Modo simulado

Sin credenciales reales SAT/Banxico/Facturama: el workflow genera reporte con datos demo plausibles. Útil para ver el shape del cierre antes de conectar.
