---
name: cfdi-colegiaturas-deducibles
description: Emite CFDI de colegiaturas con los requisitos específicos para que el padre pueda deducir conforme al Art. 151 LISR fracción VIII (deducciones personales por pagos de servicios educativos en preescolar, primaria, secundaria y media superior; NO universidad). Aplica catálogo ClaveProdServ 86111600-86111900 según nivel, UsoCFDI D10 obligatorio, valida que la forma de pago sea electrónica (efectivo NO califica para deducción), respeta topes de deducción por nivel (preescolar $14,200, primaria $12,900, secundaria $19,900, prepa técnica $17,100, prepa general $24,500 — verificar vigentes), y emite la "constancia de servicios educativos" obligatoria para que la deducción proceda. Usar siempre que el usuario diga facturar colegiatura, CFDI colegio, factura escuela, deducible D10, comprobante deducible educación, school tuition CFDI. NO usar para servicios extracurriculares de paga (deportes, talleres después del horario — distinta clave) ni para universidad (no es deducible en LISR personal).
allowed-tools: Read, Write, Edit
---

# CFDI de colegiaturas — deducibilidad correcta

Si el CFDI sale mal, el padre no puede deducir. Si no puede deducir, el colegio queda mal frente al padre y baja la satisfacción.

## Requisitos Art. 151 LISR fracción VIII

La deducción por colegiaturas aplica para:
- Educación preescolar
- Educación primaria
- Educación secundaria
- Profesional técnico (bachillerato técnico)
- Bachillerato general (prepa)

**NO aplica para**:
- Universidad / posgrado (no es deducible vía Art. 151)
- Cursos no curriculares (idiomas extras, deportes, música) salvo que sean parte del programa académico oficial
- Inscripciones (la inscripción no es deducible, solo colegiaturas mensuales)
- Materiales educativos
- Transporte escolar (eso es otra fracción del Art. 151 distinta — IX)

## Topes de deducción por nivel (verificar vigentes)

Topes anuales por alumno:

| Nivel | Tope anual |
|---|---|
| Preescolar | $14,200 |
| Primaria | $12,900 |
| Secundaria | $19,900 |
| Profesional técnico | $17,100 |
| Bachillerato general | $24,500 |

**Importante**: estos topes se actualizan periódicamente. Verificar el ejercicio fiscal vigente. El padre solo deduce hasta el tope; el colegio puede emitir CFDI por cualquier monto, pero advierte al padre sobre el tope si el monto anual lo excede.

## Estructura del CFDI

```
TipoDeComprobante: I
Emisor:
  RFC: del colegio
  Razón Social
  Régimen Fiscal: 603 si es AC, 601 si es SC/SA, 626 si RESICO PM
  Lugar de Expedición: CP del colegio
Receptor:
  RFC: del padre/madre/tutor (el que va a deducir)
  Nombre completo del receptor
  Régimen Fiscal del receptor
  CP del domicilio fiscal del receptor (obligatorio en 4.0)
  Uso CFDI: D10 (Pagos por servicios educativos - colegiaturas)
Moneda: MXN
MétodoPago: PUE
FormaPago: 03 (SPEI) | 04 (TDC) | 28 (TDD) | 02 (Cheque nominativo)
  - NO USAR: 01 Efectivo (efectivo NO califica para deducción Art. 151)
Conceptos:
  - ClaveProdServ:
    - 86111600 Servicios de educación preescolar
    - 86111700 Servicios de educación primaria
    - 86111800 Servicios de educación secundaria
    - 86111900 Servicios de educación profesional técnico
    - 86121500 Servicios de educación profesional (preparatoria general)
  - Descripción: ej. "Colegiatura del mes de Marzo 2026 — alumno [Nombre] — [grado] [grupo]"
  - ClaveUnidad: E48 (unidad de servicio) o ACT (actividad)
  - Cantidad: 1
  - ValorUnitario: monto de la colegiatura
  - Importe: igual a ValorUnitario × Cantidad
  - ObjetoImp: 02 (sí objeto del impuesto) — Servicios educativos están exentos de IVA, pero el campo va.
  - Impuestos: no aplica IVA en educación de planes oficiales SEP (exento por LIVA Art. 15 fracción IV)

Complemento "InsEduc" (obligatorio para deducibilidad):
  - nombreAlumno
  - CURP del alumno
  - nivelEducativo
  - autoRVOE (número de RVOE del colegio)
  - rfcPago (RFC del padre que paga, mismo que receptor)
```

## El complemento InsEduc

**Sin este complemento, el CFDI NO sirve para deducir**. Es lo que el SAT usa para validar la deducción del padre al cierre del ejercicio.

Estructura:
```xml
<iedu:instEducativas
  Version="1.0"
  nombreAlumno="Diego Pérez Rodríguez"
  CURP="PERD150301HDFRZG02"
  nivelEducativo="Primaria"
  autoRVOE="20060123"
  rfcPago="PERA800101ABC"
/>
```

Donde:
- `nombreAlumno`: exactamente como aparece en acta de nacimiento.
- `CURP`: del alumno (no del padre).
- `nivelEducativo`: "Preescolar" | "Primaria" | "Secundaria" | "Profesional técnico" | "Bachillerato o su equivalente".
- `autoRVOE`: número de RVOE del colegio (validar que esté vigente).
- `rfcPago`: RFC del receptor del CFDI (típicamente padre, madre o tutor que paga).

## Validaciones críticas

Antes de timbrar:

1. **Forma de pago electrónica**: si el padre pagó en efectivo, advertirle que NO podrá deducir. Ofrecer recibirle por transferencia para futuras colegiaturas.

2. **RFC del padre coincide con quien paga**: importante porque solo el padre que efectivamente pagó (y a cuyo RFC se emite el CFDI) puede deducir. Si pagan ambos padres, hay que dividir y emitir CFDIs por separado a cada uno (o todo a uno solo, según acuerdo familiar y conveniencia fiscal).

3. **Nombre del alumno consistente**: debe coincidir entre CFDI y constancia de servicios educativos. SAT puede cruzar datos.

4. **CURP del alumno válido**: estructural y registrado en RENAPO. Si captura mal el CURP, deducción rechazada.

5. **RVOE vigente del colegio**: si el RVOE está vencido o no autorizado para el nivel, el CFDI no sustenta deducción aunque tenga el complemento.

6. **Concepto descriptivo**: incluir mes, alumno, grado. Vago "Colegiatura" no es suficiente para auditoría.

## Constancia de servicios educativos (anual)

Adicional al CFDI mensual, el colegio debe emitir al cierre del ciclo escolar (o ejercicio fiscal) una **constancia anual de servicios educativos** que confirma los montos pagados durante el año por cada padre, por cada alumno. Esta constancia el padre la conserva como respaldo.

Estructura:
```markdown
# CONSTANCIA DE SERVICIOS EDUCATIVOS
# Ejercicio fiscal [Año]

[Membretado del colegio]

Por este medio se hace constar que el C. **[Nombre del padre]**, con RFC [RFC], realizó pagos por servicios educativos durante el ejercicio fiscal [año] por concepto de colegiaturas del alumno **[Nombre del alumno]**, con CURP [CURP], inscrito en el [grado] de [nivel] en este plantel.

## Resumen de pagos

| Mes | Concepto | Folio fiscal CFDI | Monto |
|---|---|---|---|
| Enero | Colegiatura | abc-1234-... | $X,XXX |
| Febrero | Colegiatura | def-5678-... | $X,XXX |
| ... | | | |

**Total pagado en el ejercicio**: $XX,XXX MXN

Esta constancia se emite para los fines fiscales del receptor conforme a la Ley del Impuesto sobre la Renta, Artículo 151 fracción VIII.

ATENTAMENTE

________________________
[Nombre del Director]
[Razón social del colegio]
RVOE: [número y fecha]
CCT: [CCT]

[Fecha de emisión]
[Sello]
```

## Casos edge

### Padres divorciados que comparten gastos escolares
- Cada padre puede recibir CFDI parcial proporcional al pago efectivo (50/50 o el % acordado).
- O todo el CFDI a uno solo y ese lo deduce (el otro padre no deduce).
- El convenio familiar determina; el colegio acomoda.

### Alumno con beca parcial
- Solo el monto efectivamente cobrado se CFDI'a.
- La beca no se factura.

### Pago de colegiatura por la abuela/abuelo
- Solo deduce quien efectivamente pagó y a cuyo nombre se emitió el CFDI.
- Abuelos pueden recibir CFDI a su RFC si pagan, pero solo deducen si tienen ingreso fiscal (típicamente jubilados con ingresos bajos no se benefician mucho de la deducción).

### Pago atrasado (varios meses pagados juntos)
- Emitir CFDI individuales por cada mes (no uno solo agrupado), para que la constancia anual tenga el detalle correcto.

### Cambio de colegio a mitad de ciclo
- Cada colegio emite CFDIs de los meses que cobró.
- El padre suma deducción de ambos (hasta tope por nivel).

## Salida esperada

Cuando el usuario pide "facturar colegiatura de [familia] de [mes]":

1. Lee datos del alumno y padre desde `clientes/[familia]/ficha.json`.
2. Valida RFCs (padre receptor + colegio emisor) con `rfc-validacion`.
3. Aplica `iva-retenciones-mx` para confirmar exención de IVA en educación oficial.
4. Aplica `cfdi-emision` con datos específicos + complemento InsEduc.
5. Emite CFDI (mock por default) y guarda XML + PDF.
6. Alerta:
   - Si forma de pago = efectivo: el padre no podrá deducir.
   - Si está cerca del tope anual: estimación de cuánto le falta para topar.
7. Si es el último mes del ciclo o fin de ejercicio: ofrecer generar la constancia anual.

## Integración

- `cfdi-emision`: base del timbrado.
- `iva-retenciones-mx`: confirmar exención de IVA.
- `rfc-validacion`: validar receptor.
- `cobranza-colegiaturas`: el CFDI se emite contra cobro efectivo.
- `comunicacion-padres-wa`: notificar al padre que su CFDI ya está listo.
