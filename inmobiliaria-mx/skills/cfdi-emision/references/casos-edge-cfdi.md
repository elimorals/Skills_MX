# Casos edge de CFDI 4.0

Patrones complejos que vienen en operación real y rompen sistemas mal diseñados. Documentados con el flujo paso a paso.

## 1. Anticipos

El SAT tiene un esquema específico de 3 CFDIs cuando un cliente paga antes de definir el servicio/bien final. **No confundir con PPD** (parcialidades): aquí ni siquiera sabes qué se va a vender al cierre.

### Flujo
```
Paso 1: Recibo del anticipo
   → CFDI tipo I (Ingreso)
   → Concepto: "Anticipo del bien o servicio"
   → ClaveProdServ: 84111506 (Servicios de facturación)
   → MétodoPago: PUE
   → FormaPago: la efectivamente recibida (03, 04, etc.)
   → Subtotal = monto del anticipo
   → Si aplica IVA, desglosar normal

Paso 2: Al definirse el bien/servicio final
   → CFDI tipo E (Egreso) por el monto del anticipo
   → Concepto: "Aplicación de anticipo"
   → TipoRelacion: 07 ("CFDI por aplicación de anticipo")
   → CfdiRelacionados: UUID del CFDI del paso 1
   → Total = monto del anticipo (en negativo conceptual)

Paso 3: CFDI final por el monto total
   → CFDI tipo I por el monto total del bien/servicio
   → MétodoPago: depende (si ya cobró todo, PUE; si queda saldo, PPD)
```

Resultado neto: el cliente paga 1 monto, recibe 3 CFDIs, y la sumatoria fiscal cuadra correctamente.

### Cuándo NO es anticipo
- Si el servicio/bien YA está definido y solo el pago se difiere: eso es PPD, no anticipo.
- Si es una parcialidad de algo ya facturado: PPD + complemento de pago.
- Si es enganche de un producto específico ya identificado: puede ser un primer CFDI por el enganche con MétodoPago PPD del total, y luego complementos de pago. Consultar con contador.

## 2. Exportación de servicios (tasa 0%)

Cuando un freelancer/empresa mexicana presta servicios a un cliente en el extranjero, la operación puede ir a tasa 0% IVA si cumple los requisitos del Art. 29 LIVA.

### Requisitos
1. El servicio se aprovecha **en el extranjero**.
2. El cliente reside en el extranjero.
3. Se cobra en moneda extranjera (preferentemente) o por transferencia bancaria identificable.

### Estructura del CFDI
```
Receptor: RFC XEXX010101000
ResidenciaFiscal: código ISO del país (USA, ESP, etc.)
NumRegIdTrib: identificación fiscal del cliente en su país (EIN, NIF, etc.)
UsoCFDI: S01 (sin efectos fiscales para el receptor extranjero)
Moneda: USD (o la que aplique) con TipoCambio del DOF
Exportacion: 02 (definitiva)

Concepto:
  TasaOCuota: 0.000000
  TipoFactor: Tasa
  Importe: 0.00 (sí debe existir el nodo IVA aunque sea cero)
```

### Diferencia con "exento"
- **Tasa 0%**: el nodo IVA existe con valor 0.00. El emisor sí acumula IVA acreditable de sus gastos.
- **Exento**: el nodo IVA no existe (TipoFactor = "Exento", sin TasaOCuota). El emisor NO acumula IVA acreditable.

Para exportación es **siempre tasa 0%**, no exento.

## 3. Factura global de público en general

Cuando vendes en mostrador (refaccionaria, tienda física, restaurante) y la mayoría de clientes no piden CFDI, debes emitir una **factura global periódica** con los montos no facturados individualmente.

### Periodicidad
- Diaria, semanal, quincenal o mensual. Definir política consistente.
- Mensual es lo más común para PyMEs.

### Estructura
```
TipoDeComprobante: I
RFC receptor: XAXX010101000
Nombre receptor: PUBLICO EN GENERAL
UsoCFDI: S01
RegimenFiscalReceptor: 616 (Sin obligaciones fiscales)

InformacionGlobal:
  Periodicidad: 01 (Diaria), 02 (Semanal), 03 (Quincenal), 04 (Mensual), 05 (Bimestral)
  Meses: clave del mes del período
  Año: año del período

Conceptos:
  - Puede ser un solo concepto con ClaveProdServ 01010101 (No existe en el catálogo - identifier para venta agrupada)
    y descripción "Venta de público en general"
  - O conceptos detallados por SKU si el ERP lo permite (mejor para auditoría)
  - Cantidad y valor unitario reflejan la agrupación del período
```

### Errores comunes
- Mezclar ventas con CFDI individual y ventas a público en general en un mismo período sin separar.
- No emitir la global y esperar que "no le pase nada" — sí pasa, queda diferencia con la contabilidad.
- Usar UsoCFDI distinto de S01 (rechazo del PAC).

## 4. Refacturación (sustitución por error)

CFDI emitido con datos incorrectos (RFC equivocado, monto mal, descripción confusa). El cliente lo necesita correcto para deducción.

### Flujo
```
Paso 1: Cancelar el CFDI original
   → Motivo de cancelación: 01 ("Comprobante emitido con errores con relación")
   → Folio sustituto: UUID del CFDI nuevo (que aún no existe — emitir paso 2 primero
     y luego cancelar paso 1 referenciando el nuevo UUID)

Paso 2: Emitir CFDI nuevo
   → Datos correctos
   → CfdiRelacionados:
     TipoRelacion: 04 ("Sustitución de los CFDI previos")
     UUID: UUID del CFDI original

Paso 3: Cancelar el CFDI original (orden real):
   → En realidad muchos PACs requieren cancelar primero y emitir después.
     Verificar el flujo específico del PAC.
   → La cancelación necesita aceptación del receptor si pasaron >72h o monto >$1,000 MXN.
```

### Buenas prácticas
- Antes de timbrar un CFDI, validar datos contra checklist del usuario (no asumir).
- Si refacturas mucho, hay un problema upstream — revisar captura.

## 5. Cliente extranjero con RFC mexicano

Algunos extranjeros (residentes en MX con visa, casa habitación, propiedades) sí tienen RFC. En ese caso se tratan como contribuyentes regulares, NO como genérico extranjero.

Identificar por:
- RFC con estructura normal (no XEXX010101000).
- Tienen domicilio fiscal en MX.

CFDI normal, sin ResidenciaFiscal ni NumRegIdTrib.

## 6. Operación con Persona Moral del Régimen 603 (no lucrativa)

Ej: facturarle a una asociación civil, fundación, AC.

Diferencias:
- Régimen 603 puede usar UsoCFDI: G01, G02, G03, I01-I08, D04 (donativos).
- Si es un donativo, requiere que la AC tenga autorización vigente del SAT para recibir donativos deducibles (lista publicada).
- En donativos, la deducción del donante depende de esa autorización.

## 7. Servicios profesionales facturados a través de plataforma tecnológica (Uber, Rappi, etc.)

Régimen 625 — Plataformas Tecnológicas. La plataforma retiene ISR e IVA. El contribuyente:
- Si opta por considerar las retenciones como pago definitivo: no presenta declaración anual ni provisionales.
- Si opta por acumular ingresos: presenta declaraciones normales y las retenciones son a cuenta.

CFDI emitido por el contribuyente (no por la plataforma) lleva las retenciones que la plataforma efectuó.

## 8. Complemento de pago (REP) — el caso PPD

Cuando emitiste un CFDI con MétodoPago = PPD, al recibir cada pago real, emite:

```
TipoDeComprobante: P (Pago)
UsoCFDI: CP01 (obligatorio)
Sin Conceptos económicos (un solo concepto con clave 84111506, importe 0)
Sin IVA en conceptos

Complemento Pagos2.0:
  Pago:
    FechaPago: fecha real del pago
    FormaDePagoP: la forma realmente usada (03, 04, etc.)
    MonedaP: moneda
    Monto: monto del pago
    DoctoRelacionado:
      IdDocumento: UUID del CFDI original
      Serie/Folio del CFDI original
      MonedaDR
      MetodoDePagoDR: PPD
      NumParcialidad: 1, 2, 3...
      ImpSaldoAnt: saldo anterior al pago
      ImpPagado: monto aplicado de este pago
      ImpSaldoInsoluto: saldo después de este pago
      ObjetoImpDR: 01-04 según corresponda
      ImpuestosDR:
        # Trasladados y retenidos prorrateados del pago
```

### Plazo SAT
El REP debe emitirse a más tardar el día **10 del mes siguiente** al pago recibido.

### Caso edge: anulación de pago (cheque devuelto, contracargo)
- Emitir CFDI tipo E (egreso) que cancele el REP.
- Volver a emitir cuando el cobro sea real.

## 9. CFDI para honorarios médicos (deducción del paciente)

Para que el paciente lo deduzca personalmente (Art. 151 LISR):

```
TipoDeComprobante: I
Receptor: persona física con su RFC real
UsoCFDI: D01 (honorarios médicos)
FormaPago: solo medios electrónicos (03 transferencia, 04 crédito, 28 débito)
  → CRÍTICO: efectivo NO califica para deducción de honorarios médicos.
RegimenFiscalReceptor: el del paciente
Concepto:
  ClaveProdServ: 85121500 (medicina general), 85121800 (dental), etc.
  Descripción: detallar el servicio
```

Si el paciente paga en efectivo y luego pide CFDI deducible: explicar que SAT no permite deducción. Ofrecer transferencia.

## 10. Sustitución de CFDI con Saldo de Crédito (Egreso por bonificación)

Cliente devuelve mercancía o pide descuento posterior:

```
CFDI tipo E (Egreso)
TipoRelacion: 01 ("Nota de crédito de los documentos relacionados")
CfdiRelacionados: UUID del CFDI de Ingreso original
UsoCFDI: G02 (Devoluciones, descuentos o bonificaciones)
Concepto:
  Descripción del descuento/bonificación
  Importe en positivo (no negativo)
Total en positivo
```

El SAT lo procesa restándolo del ingreso del emisor en la contabilidad.

## Caso transversal: redondeo y centavos perdidos

Cuando un CFDI tiene muchos conceptos con porcentajes (descuentos prorrateados, etc.), la suma de los conceptos redondeados puede no cuadrar con el total redondeado en ±0.01.

Solución estándar: agregar un concepto final de "Ajuste por redondeo" con valor ±0.01 si la diferencia ocurre. Los PACs serios validan que cuadre exactamente.

## Bibliografía mínima

- Anexo 20 de la Resolución Miscelánea Fiscal (vigente).
- Guía de llenado del CFDI versión 4.0 publicada por SAT.
- Reglas de la Miscelánea Fiscal aplicables a CFDI (Capítulo 2.7).
