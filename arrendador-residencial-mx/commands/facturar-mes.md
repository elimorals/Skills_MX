---
description: Emite CFDI mensual a todos los inquilinos del mes en curso.
---

Invoca `cfdi-arrendamiento-mensual` para cada propiedad rentada con pago confirmado.

Calcula automáticamente caso (A/B/C/D) según régimen del emisor + tipo de inquilino (PF/PM). Aplica retenciones ISR si aplica.

Output: UUIDs + paths XML+PDF por cada CFDI emitido + resumen del mes.
