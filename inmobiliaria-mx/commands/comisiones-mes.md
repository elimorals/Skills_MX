---
description: Calcula comisiones del mes para venta/renta/administración con desglose por operación + retenciones si cliente es PM.
argument-hint: "[mes y año]"
allowed-tools: Read, Write, Edit
---

# /inm:comisiones-mes

Comisiones del mes: $ARGUMENTS

Skill `comisiones-corredor` calcula:
- Venta: % sobre precio (3-7%)
- Renta: 1 mes honorario
- Administración: 5-10% mensual

Aplica retenciones ISR + 2/3 IVA si cliente es PM.
