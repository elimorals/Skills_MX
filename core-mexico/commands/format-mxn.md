---
description: Normaliza y formatea un monto en pesos mexicanos al formato canónico, incluyendo conversión a letra.
argument-hint: "<monto>"
allowed-tools: Read, Bash
---

# /core:format-mxn

Formatea el monto: $ARGUMENTS

1. Invoca el skill `mxn-formato` con el monto recibido.
2. Si el input es ambiguo (ej. `1.234` puede ser europeo o decimal con 3 dígitos), pregúntalo antes de asumir.
3. Devuelve:
   - Monto normalizado (número)
   - Formato corto: `$1,234.56`
   - Formato largo con MXN: `$1,234.56 MXN`
   - En letra para contratos/CFDI: `UN MIL DOSCIENTOS TREINTA Y CUATRO PESOS 56/100 M.N.`
   - Alertas si hubo redondeo o ajuste
