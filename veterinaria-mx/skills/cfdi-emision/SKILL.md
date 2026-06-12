---
name: cfdi-emision
description: Emite Comprobantes Fiscales Digitales por Internet (CFDI) versión 4.0 conforme a las reglas vigentes del SAT en México. Cubre tipos I/E/T/N/P, catálogos UsoCFDI, FormaPago, MétodoPago (PUE/PPD), RegimenFiscal, ClaveProdServ, complementos comunes, cancelación con motivos 01-04, y casos edge (RFC genérico XAXX010101000, factura global de público en general, exportación, operaciones con extranjeros). Usar SIEMPRE cuando el usuario diga facturar, emitir factura, CFDI, comprobante fiscal, timbrar, pre-factura, refacturar, cancelar factura, generate invoice, issue tax invoice, o pida un comprobante para una venta/servicio en México. NO usar para facturas de otros países (Argentina AFIP, Colombia DIAN, España AEAT) ni para órdenes de compra/cotizaciones (esas no se timbran).
allowed-tools: Read, Write, Edit, Bash
---

# Emisión de CFDI 4.0

Este skill conoce las reglas de emisión de CFDI 4.0 vigentes en México (versión obligatoria desde abril 2023, con anexos actualizados periódicamente por el SAT). Tu trabajo al usarlo: recopilar datos válidos, aplicar las reglas correctas, producir el payload que el PAC firmará, y nunca dejar pasar un error fiscal silencioso.

## Cuándo usar este skill

Triggers obvios: el usuario pide facturar, timbrar, emitir CFDI, hacer comprobante fiscal, refacturar, sustituir factura, cancelar.

Triggers menos obvios pero que también lo activan:
- "Me pidieron CFDI por el servicio que vendí" → usa este skill
- "El cliente quiere factura, no remisión" → usa este skill
- "Necesito que el comprobante sea deducible" → usa este skill (probablemente requiere uso correcto del CFDI)
- "Reembolso de viáticos" → usa este skill (CFDI tipo Egreso con uso CN01 o nota de crédito)

## Cuándo NO usar

- Cotizaciones, propuestas comerciales, órdenes de compra: NO se timbran. Usar el skill `cotizacion-mxn` del vertical correspondiente.
- Remisiones internas / vales de mostrador sin valor fiscal: si el usuario explícitamente dice "remisión sin CFDI" no metas el flujo de timbrado.
- Facturación en otros países (Argentina, Chile, Colombia, España): no aplica este skill.
- Recibo simple de pago no fiscal: si el usuario quiere "constancia de pago" personal sin valor SAT, no actives el flujo CFDI.

## Conocimiento base obligatorio

### Versión vigente
- **CFDI 4.0** obligatorio desde el 1 de abril de 2023 (Resolución Miscelánea Fiscal).
- Versiones anteriores (3.3) no se aceptan en producción. Si alguien menciona 3.3, hay que advertirlo.

### Tipos de comprobante (campo `TipoDeComprobante`)
- `I` — Ingreso: factura por venta de bien o servicio.
- `E` — Egreso: nota de crédito, devolución, descuento, bonificación.
- `T` — Traslado: movimiento de mercancía sin transferencia de propiedad (requiere complemento Carta Porte).
- `N` — Nómina: timbrado de recibos de nómina (requiere complemento Nómina 1.2).
- `P` — Pago: complemento de pago (REP), obligatorio cuando un CFDI de Ingreso fue con `MétodoPago = PPD`.

### Régimen fiscal del emisor (campo `RegimenFiscalEmisor`)
Los más comunes en operación pequeña/mediana:
- `601` Persona Moral Régimen General de Ley
- `603` Personas Morales con Fines no Lucrativos
- `605` Sueldos y Salarios e Ingresos Asimilados a Salarios
- `612` Personas Físicas con Actividades Empresariales y Profesionales (PFAE)
- `621` Incorporación Fiscal (este régimen ya está fuera, solo migraciones)
- `625` Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas
- `626` Régimen Simplificado de Confianza (RESICO) — el más relevante hoy para PyMEs y freelancers

Si no sabes el régimen del emisor, **pregúntalo antes de timbrar**. Es campo obligatorio y un error invalida el CFDI.

### Uso CFDI del receptor (campo `UsoCFDI`)
Catálogo `c_UsoCFDI` del SAT. Los más comunes:
- `G01` Adquisición de mercancías
- `G02` Devoluciones, descuentos o bonificaciones (usar con CFDI de egreso)
- `G03` Gastos en general — **el más usado por empresas**
- `P01` Por definir — válido pero el SAT recomienda no usarlo (señal de pereza fiscal)
- `S01` Sin efectos fiscales — para CFDI a público en general (factura global)
- `D01` Honorarios médicos, dentales y gastos hospitalarios
- `D02` Gastos médicos por incapacidad o discapacidad
- `D10` Pagos por servicios educativos (colegiaturas)
- `CP01` Pagos — uso obligatorio para CFDI tipo P (complemento de pago)
- `CN01` Nómina — uso obligatorio para CFDI tipo N

Regla crítica: el **UsoCFDI debe ser compatible con el régimen fiscal del receptor**. El SAT publica una matriz de compatibilidad — un cliente RESICO no puede usar G03, por ejemplo. Si el sistema PAC rechaza por incompatibilidad, ofrecer alternativas válidas según el régimen del receptor.

### Forma de pago (campo `FormaPago`)
Catálogo `c_FormaPago`. Los relevantes:
- `01` Efectivo (con tope de $2,000 MXN por ley antilavado para deducibilidad)
- `02` Cheque nominativo
- `03` Transferencia electrónica de fondos (SPEI)
- `04` Tarjeta de crédito
- `28` Tarjeta de débito
- `99` Por definir — **solo válido cuando MétodoPago = PPD**

### Método de pago (campo `MétodoPago`)
- `PUE` Pago en Una sola Exhibición — el cliente paga al recibir el bien/servicio.
- `PPD` Pago en Parcialidades o Diferido — el cliente paga después (crédito, plazo). Obliga a emitir posteriormente CFDI tipo P (complemento de pago) por cada cobro.

**Regla crítica que muchos sistemas equivocan**: si `MétodoPago = PUE`, el campo `FormaPago` debe ser específico (01, 02, 03, etc., NUNCA 99). Si `MétodoPago = PPD`, `FormaPago` debe ser obligatoriamente `99`.

### Objeto del impuesto (`ObjetoImp` por concepto)
Campo obligatorio en 4.0 a nivel de cada concepto:
- `01` No objeto del impuesto
- `02` Sí objeto del impuesto (lo más común; obliga a desglosar IVA)
- `03` Sí objeto del impuesto y no obligado al desglose
- `04` Sí objeto del impuesto y no causa impuesto (tasa 0 distinta de exento)

### Exportación (`Exportacion`)
Campo obligatorio en 4.0:
- `01` No aplica (lo más común para operaciones nacionales)
- `02` Definitiva (clave A1 en Carta Porte de exportación)
- `03` Temporal
- `04` No objeto del impuesto

## Datos mínimos que debes recopilar antes de timbrar

Si falta alguno, **pídelo antes de generar el payload**:

**Emisor (quien factura):**
- RFC válido (12 caracteres PM, 13 caracteres PF)
- Razón Social (debe coincidir exactamente con la registrada en SAT)
- Régimen Fiscal (601, 612, 626, etc.)
- Domicilio fiscal: al menos el CP (código postal de 5 dígitos)

**Receptor (cliente):**
- RFC válido
- Nombre o Razón Social
- Régimen Fiscal del receptor
- Uso CFDI
- Domicilio fiscal: **CP obligatorio en CFDI 4.0** (esto es nuevo respecto a 3.3 y rompe sistemas viejos)

**Comprobante:**
- TipoDeComprobante (I, E, T, N, P)
- Moneda (MXN, USD, EUR, etc.; si distinta de MXN se requiere TipoCambio)
- Conceptos (al menos uno): ClaveProdServ del SAT (catálogo c_ClaveProdServ, 8 dígitos), descripción, cantidad, ClaveUnidad, ValorUnitario, Importe, ObjetoImp
- MétodoPago (PUE/PPD) y FormaPago consistente
- Si IVA aplica: tasa (0.16 estándar, 0.08 fronterizo, 0.00 tasa 0) y desglose

## Reglas críticas de validación (antes de mandar al PAC)

Ejecuta estas validaciones contra el payload. Si una falla, **no llames al PAC** — corrige y regenera:

1. **RFC genérico**: si receptor es público en general, RFC debe ser `XAXX010101000` (nacional) o `XEXX010101000` (extranjero). En estos casos, UsoCFDI debe ser `S01`.

2. **Consistencia MétodoPago vs FormaPago**:
   - `PUE` → FormaPago debe ser específico (01, 02, 03, 04, etc.). Si es 99 → ERROR.
   - `PPD` → FormaPago debe ser obligatoriamente `99`. Cualquier otro → ERROR.

3. **Subtotal y Total**: la suma de importes de los conceptos debe coincidir con Subtotal. Total = Subtotal + impuestos trasladados − impuestos retenidos. Sin diferencias de redondeo > $0.01.

4. **Moneda**: si Moneda ≠ MXN, debe incluirse TipoCambio con valor positivo. Si Moneda = MXN, TipoCambio no debe existir (algunos sistemas lo mandan en 1 y el PAC los rechaza).

5. **Impuestos**: si ObjetoImp = 02 en cualquier concepto, el nodo de Impuestos a nivel concepto y a nivel comprobante es obligatorio. Si ObjetoImp = 01 en todos, no debe haber nodo Impuestos.

6. **Fecha**: máximo 72 horas hacia el pasado y 0 hacia el futuro. Formato `YYYY-MM-DDTHH:MM:SS` zona horaria del domicilio fiscal del emisor.

7. **Lugar de Expedición**: CP de 5 dígitos del domicilio fiscal del emisor. Debe ser válido (existir en catálogo c_CodigoPostal).

## Flujo de emisión (resumido)

```
1. Recopilar datos (validar contra checklist anterior)
2. Construir payload JSON intermedio (estructura legible)
3. Aplicar validaciones críticas locales
4. Convertir payload a XML CFDI 4.0 (o pasar al SDK del PAC)
5. Enviar al PAC para timbrado
6. PAC devuelve XML timbrado con UUID, sello y cadena original del SAT
7. Guardar XML + PDF representación impresa
8. (Si MétodoPago = PPD) recordar emitir CFDI tipo P cuando se reciba el pago
```

Mientras no haya PAC configurado, este skill genera el **payload JSON intermedio** y un **mock del XML timbrado** con UUID simulado, marcando el response como `simulated: true` para que el código upstream distinga producción de mock.

## Manejo de cancelación

Desde 2022 el SAT exige especificar **motivo de cancelación**:
- `01` Comprobante emitido con errores con relación — requiere indicar el UUID del CFDI que sustituye (folio sustituto).
- `02` Comprobante emitido con errores sin relación.
- `03` No se llevó a cabo la operación.
- `04` Operación nominativa relacionada en una factura global.

Si el CFDI tiene más de 72 horas o el monto supera $1,000 MXN, la cancelación **requiere aceptación del receptor** (proceso asíncrono vía buzón tributario del receptor). Plazo de respuesta: 3 días hábiles; si no responde, se considera aceptada.

## Casos edge importantes

**Factura global a público en general**: cuando vendes en mostrador a clientes que no piden CFDI individual, debes emitir una **factura global periódica** (diaria, semanal, mensual, según volumen) con RFC genérico XAXX010101000, UsoCFDI S01, y los conceptos agrupados o detallados según política. El periodo se indica en `InformacionGlobal`.

**Cliente extranjero sin RFC mexicano**: usar RFC genérico `XEXX010101000`, y agregar el nodo `<cfdi:Receptor>` con `ResidenciaFiscal` (código ISO del país) y `NumRegIdTrib` (identificación tributaria del país de origen).

**Operación a tasa 0% IVA (exportación de servicios)**: TipoFactor = "Tasa", TasaOCuota = "0.000000", el monto del impuesto debe ser 0.00 pero **el nodo IVA sí debe existir**. Esto es distinto de "exento" (TipoFactor = "Exento", sin TasaOCuota).

**Anticipos**: si el cliente paga un anticipo antes de definir el servicio final, hay un esquema específico del SAT (CFDI de Ingreso por el anticipo + CFDI de Egreso al finalizar el servicio + CFDI de Ingreso final por el total). No confundir con PPD. Si el usuario pregunta por anticipos, explicar el flujo antes de emitir cualquier cosa.

**Servicios profesionales PFAE → Persona Moral**: retención obligatoria de ISR (10%) e IVA (10.6667%). Estas retenciones DEBEN venir en el nodo `Impuestos > Retenciones` del comprobante. El subtotal NO se reduce por las retenciones — se desglosan aparte y el cliente las entera al SAT.

## Salida esperada

Cuando termines, presenta al usuario:

1. **Payload JSON intermedio validado** (legible, mostrar al usuario para confirmar antes de timbrar).
2. **Resultado del timbrado**:
   - Si hay PAC real configurado: UUID, fecha de timbrado, sello del SAT, cadena original.
   - Si está en mock: estructura simulada con `simulated: true`, UUID generado con formato válido (8-4-4-4-12 hex), y nota clara de que es mock.
3. **Archivos generados**: ruta del XML, ruta del PDF (si se solicitó representación impresa).
4. **Alertas pendientes**: si MétodoPago = PPD, recordatorio de emitir CFDI tipo P al recibir pago.

## Referencias bundleadas

Para datos detallados de catálogos, consulta:
- `references/catalogos-sat.md` — UsoCFDI, FormaPago, RegimenFiscal, TipoDeComprobante, ObjetoImp, Exportacion, ClaveUnidad, ClaveProdServ patrones por giro, Moneda, TipoRelacion
- `references/casos-edge-cfdi.md` — anticipos (3 CFDIs), exportación servicios, factura global, refacturación, REP, honorarios médicos, nota de crédito, redondeo

## ⚠ Datos que requieren verificación vigente antes de producción

Este skill cita información del SAT que puede haber sido actualizada después de la fecha de mi training data. **NO usar en producción sin verificar contra el portal SAT actual**:

1. **Catálogos SAT** (`references/catalogos-sat.md`): el SAT actualiza claves periódicamente. Validar contra:
   - https://www.sat.gob.mx (catálogos descargables del Anexo 20 vigente)
   - Validador del proveedor PAC que uses (Facturama, SW Sapien, etc. mantienen catálogos actualizados)

2. **Reglas de cancelación**: los motivos 01-04 y plazos (72h sin aceptación / >$1,000 con aceptación) pueden haber cambiado en Resolución Miscelánea Fiscal vigente.

3. **Versión del Anexo 20**: confirmar que la versión activa sigue siendo CFDI 4.0 (vigente desde abr 2023). Cambios a 4.1+ requieren actualizar este skill.

4. **Complementos**: si el caso de uso requiere un complemento específico (Pagos2.0, Nómina1.2, Carta Porte 3.0, INE, Comercio Exterior, etc.), verificar versión vigente del complemento. **Este skill cubre el CFDI base; los complementos requieren skills adicionales o referencias específicas.**

5. **Forma de pago**: la clave 99 "Por definir" puede tener restricciones nuevas en la RMF actual.

**Antes de exponer este skill a cliente real**: descargar los catálogos del Anexo 20 vigente, actualizar `catalogos-sat.md`, y correr al menos un timbrado de prueba contra PAC sandbox (Facturama tiene sandbox gratuito).

## Tono de comunicación con el usuario final

Si el usuario es contador o tiene jerga fiscal, habla técnico con códigos directamente. Si el usuario es dueño de PyME o freelancer, traduce: en vez de "tu MétodoPago es PPD" di "como te van a pagar después, esto se emite en modalidad de crédito y tendrás que mandar un comprobante adicional cuando cobres". El SAT es opaco para muchos usuarios; tu trabajo es no agregar opacidad.
