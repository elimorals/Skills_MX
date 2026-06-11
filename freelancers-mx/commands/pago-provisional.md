---
description: Calcula el pago provisional ISR del mes para RESICO PF o PFAE, con proyección anual.
argument-hint: "[mes] [año]"
allowed-tools: Read, Write, Edit, Bash
---

# /freelancers:pago-provisional

Pago provisional del periodo: $ARGUMENTS

1. Invoca el skill `freelance-tax-mx`.
2. Detecta el régimen del usuario (RESICO 626 o PFAE 612). Si no está configurado, pregúntalo.
3. Pide o lee:
   - CFDIs emitidos del mes (ingresos cobrados — base flujo)
   - CFDIs recibidos del mes (gastos, solo si PFAE)
   - Retenciones recibidas del mes
   - Pagos provisionales del ejercicio acumulados (solo PFAE)
4. Aplica la fórmula correcta según régimen.
5. Genera reporte en `fiscal/YYYY-MM-pago-provisional.md` con:
   - Cálculo paso a paso
   - Monto a pagar al SAT
   - Plazo límite (día 17 del mes siguiente)
   - Alertas (retenciones no acreditadas, depósitos efectivo dudosos, gastos sin CFDI)
6. Estima saldo anual proyectado (a favor o cargo) si está a media del año o después.
7. Recomienda acciones si detecta optimización fiscal (ej. deducción personal pendiente de captura).
