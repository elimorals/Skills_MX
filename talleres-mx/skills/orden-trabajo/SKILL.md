---
name: orden-trabajo
description: Genera la Orden de Trabajo (OT) formal del taller automotriz con datos del vehículo, propietario, trabajos autorizados específicamente con desglose de mano de obra + refacciones + insumos, asignación de mecánico, plazo comprometido, costo total con IVA, política de garantía aplicada, condiciones de pago y firmas. La OT es el documento legal que respalda el trabajo realizado y es prueba en caso de disputa PROFECO. Cubre OT inicial (al recibir autorización), OT modificada (cuando se descubre trabajo adicional con autorización), y OT cerrada (al entregar con check final). Incluye check-out con devolución de refacciones reemplazadas si el cliente lo solicita (derecho del consumidor). Usar cuando el usuario diga orden de trabajo, OT, work order, abrir orden, cerrar orden, OT firmada. NO usar para cotizaciones previas a autorización (otro skill).
allowed-tools: Read, Write, Edit
---

# Orden de Trabajo formal del taller

La OT es el documento principal del taller. Sin OT bien hecha, no hay defensa legal en caso de queja.

## Estructura de la OT

```markdown
# Orden de Trabajo OT-XXXX

**Taller**: [Razón social]
RFC: [RFC]
Dirección: [...]
Teléfono: [...]

**Fecha de apertura**: DD/MM/AAAA HH:MM
**Vinculada a diagnóstico**: DIAG-XXXX
**Mecánico asignado**: [Nombre]

---

## Datos del propietario

- Nombre: [Nombre completo]
- Teléfono / WhatsApp: [...]
- Email: [...]
- ¿Requiere CFDI?: Sí/No
  - Si sí: RFC, razón social, régimen, uso CFDI, CP

## Datos del vehículo

- Marca: [...]
- Modelo: [...]
- Año: [...]
- VIN: [...]
- Placas: [...]
- Color: [...]
- Kilometraje al ingreso: [km]
- Nivel de gasolina al ingreso: [marca en imagen / fracción]
- Condiciones generales: [estado al recibir, descripción + fotos]

### Inventario de objetos personales (si el cliente dejó cosas)
- [Item 1]
- [Item 2]
[Foto del interior si hay items]

---

## Trabajos autorizados

### Servicios contratados

| # | Trabajo | Mano de obra (hrs) | Tarifa | Subtotal MO |
|---|---|---|---|---|
| 1 | [Trabajo 1] | X | $XXX/h | $XXX |
| 2 | [Trabajo 2] | X | $XXX/h | $XXX |
| **Subtotal MO** | | | | **$X,XXX** |

### Refacciones e insumos

| # | Refacción / Insumo | Marca / Parte # | Cant. | Precio unit. | Subtotal |
|---|---|---|---|---|---|
| 1 | Balata delantera | Brembo PD7589 | 1 | $1,200 | $1,200 |
| 2 | Rotor delantero | Brembo 08.5181.21 | 2 | $1,200 | $2,400 |
| **Subtotal refacciones** | | | | | **$X,XXX** |

### Resumen económico

- Subtotal: $X,XXX
- IVA 16%: $X,XXX
- **Total**: $X,XXX MXN

## Plazo comprometido

- Inicio de trabajos: DD/MM/AAAA HH:MM
- Entrega estimada: DD/MM/AAAA HH:MM
- Cualquier retraso se notifica al cliente vía WhatsApp.

## Política de garantía

- Mano de obra: 30 días
- Refacciones: 90 días (o garantía del fabricante, lo que sea mayor)
- Términos detallados: ver certificado de garantía al cierre.

## Política de devolución de refacciones reemplazadas

Conforme al derecho del consumidor, el cliente puede solicitar las refacciones reemplazadas para revisarlas. **Marcar al inicio**:

- [ ] El cliente solicita las refacciones reemplazadas (se entregan al cierre).
- [ ] El cliente NO requiere las refacciones (el taller las desecha o vende).

## Política de auto detenido

Si el cliente no recoge el auto en los 5 días posteriores a la fecha de entrega:
- A partir del día 6: cargo de almacenamiento de $XXX/día.
- A partir del día 30: notificación formal con base en Ley Federal del Consumidor.
- A partir del día 60+: procedimiento de auto en abandono.

## Forma de pago

- Efectivo
- Transferencia SPEI a: [CLABE]
- Tarjeta (con terminal en taller)
- Mercado Pago / Stripe link al teléfono

CFDI se emite al recibir el pago efectivo.

---

## Firmas

**Por el taller**:
[Nombre] [Cargo]
Firma: ____________

**Por el cliente**:
He leído y autorizo los trabajos descritos:
[Nombre]
Firma: ____________
Fecha: DD/MM/AAAA HH:MM
```

## Tipos de OT

### OT-Inicial (al recibir autorización)

Contiene todos los trabajos autorizados desde el inicio según `autorizacion-cliente-wa`. Cliente firma física o digitalmente.

### OT-Modificación (cuando se descubre trabajo adicional)

Si durante el trabajo se descubre algo más y el cliente autoriza:
- Generar OT-MOD-XXXX vinculada a la OT original.
- Describir el nuevo trabajo, costo, plazo adicional.
- Cliente autoriza por WhatsApp con texto explícito (registrado por `autorizacion-cliente-wa`) o firma adicional si vuelve al taller.

### OT-Cierre (al entregar el auto)

Cuando se completa el servicio:
- Marcar trabajos como completados.
- Adjuntar reporte de check-out (estado al entregar).
- Generar CFDI al cobrar (con `cfdi-emision`).
- Entregar certificado de garantía (de `garantia-servicio`).
- Si cliente pidió refacciones reemplazadas, entregarlas con etiqueta del trabajo.

## Check-out al entregar

Documento al entregar:

```markdown
# Check-out OT-XXXX

Fecha de entrega: DD/MM/AAAA HH:MM
Kilometraje al entregar: [km]
Nivel de gasolina al entregar: [marca / fracción]

## Trabajos completados ✅
1. [Trabajo 1] — completado
2. [Trabajo 2] — completado

## Inventario verificado
- [Items entregados al cliente]
- Refacciones reemplazadas: entregadas / no aplica

## Pruebas finales realizadas
- Test drive: [resultado]
- Verificación de funcionamiento: [resultado]

## Pagado
- Monto total: $X,XXX
- Forma de pago: [...]
- CFDI emitido: Sí/No (folio: ...)
- Certificado de garantía entregado: Sí

## Firma del cliente al recibir

Recibí mi vehículo en las condiciones descritas, con el trabajo completado conforme a la OT.

Firma cliente: ____________
Fecha: DD/MM/AAAA HH:MM
```

## Insights operativos

- **Firma autógrafa o digital al inicio Y al cierre**. Dos momentos de firma reducen disputa.
- **Foto del auto al ingreso desde 4 ángulos** + interior, especialmente con autos premium. Documenta el estado.
- **Inventario de objetos personales** evita el "se me perdió el reloj que dejé en la guantera".
- **Nivel de gasolina marcado** evita el "me lo entregaron en reservas".
- **Refacciones reemplazadas a disposición del cliente** es derecho del consumidor según PROFECO. Honrarlo.

## Validaciones

- RFC del cliente si requiere CFDI: validar con `rfc-validacion`.
- IVA correcto en el desglose: `iva-retenciones-mx`.
- Cálculos cuadran (subtotales suman al total).
- Plazo razonable (no comprometer 2 horas para un trabajo de 6).

## Salida esperada

Cuando el usuario invoca:

### "Abrir OT para [auto/cliente]"
1. Lee diagnóstico vinculado.
2. Lee autorización registrada.
3. Genera OT-Inicial completa.
4. Sugiere imprimir + firmar (o flujo digital con tablet en taller).

### "Cerrar OT-XXXX"
1. Lee OT original.
2. Genera check-out.
3. Dispara `cfdi-emision` para CFDI del trabajo.
4. Dispara `garantia-servicio` para certificado de garantía.
5. Genera mensaje WhatsApp al cliente confirmando entrega.

## Integración

- `diagnostico-cotizacion`: input.
- `autorizacion-cliente-wa`: input.
- `cfdi-emision`: output al cierre.
- `garantia-servicio`: output al cierre.
- `whatsapp-business-mx`: notificación al cliente.
- `compliance-lfpdppp`: tratamiento de datos del expediente.
