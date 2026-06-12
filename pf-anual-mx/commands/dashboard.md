---
description: Muestra dashboard del año fiscal en curso (ingresos, deducciones, ISR estimado, saldo).
---

Invoca el skill `dashboard-anual-fiscal` para mostrar el status del ejercicio fiscal en curso.

Si no se indica ejercicio: usa el año en curso si estamos en periodo de declaración (enero-abril), o el año previo si ya cerró.

Output esperado: tabla resumida + JSON estructurado + alertas si hay items pendientes (CFDIs sin clasificar, depósitos sin facturar, etc.).
