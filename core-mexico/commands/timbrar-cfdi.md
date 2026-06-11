---
description: Construye el payload de un CFDI 4.0 con validaciones SAT y simula timbrado contra mock (o PAC real si está configurado).
argument-hint: "[descripción breve del comprobante a emitir]"
allowed-tools: Read, Write, Edit, Bash
---

# /core:timbrar-cfdi

Construye y timbra un CFDI 4.0: $ARGUMENTS

1. Invoca el skill `cfdi-emision`.
2. Recopila datos faltantes preguntando al usuario:
   - Emisor: RFC, razón social, régimen fiscal, CP
   - Receptor: RFC, nombre, régimen, uso CFDI, CP
   - Conceptos: descripción, claveProdServ, cantidad, valor unitario, objeto imp
   - Método y forma de pago
3. Invoca `rfc-validacion` sobre RFC emisor y receptor.
4. Invoca `iva-retenciones-mx` para calcular impuestos correctos según escenario.
5. Aplica todas las validaciones críticas locales (consistencia método/forma, totales, fechas, etc.).
6. Muestra al usuario el payload JSON intermedio para confirmación.
7. Si está aprobado, manda al PAC (mock por default) y devuelve UUID + sello + cadena original.
8. Guarda XML en `cfdi/<UUID>.xml` y, si se pide, PDF de representación impresa.
9. Si MétodoPago es PPD, agrega recordatorio explícito de emisión de CFDI tipo P al recibir pago.
