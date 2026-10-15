---
name: cfdi-publico-global
description: Emisión de CFDI público global consolidado para ventas B2C de restaurantes mexicanos donde el cliente NO proporciona RFC (mayoría de casos en restaurante). Se emite una factura global (diaria, semanal, quincenal o mensual) a "PUBLICO EN GENERAL" con RFC genérico XAXX010101000 y nodo InformacionGlobal. Calcula el monto del periodo, qué forma de pago usar (efectivo, tarjeta, mixto), el llenado CFDI 4.0 y cómo tratar ventas por Rappi/Uber Eats/DiDi Food y sus retenciones. Usar cuando el usuario diga CFDI público general, factura sin RFC, cliente no pidió factura, cierre mensual ventas, factura global, XAXX010101000, tickets sin factura. NO usar para CFDI individual al cliente (cfdi-emision) ni para B2B.
allowed-tools: Read, Write, Edit
---

# CFDI Público Global (factura global) — restaurantes

## ¿Qué es y por qué emitirlo?

Toda venta debe ampararse con CFDI (Art. 29 CFF). Cuando el cliente no pide factura individual, el restaurante emite una **factura global** por las operaciones con público en general (regla 2.7.1.21 RMF; **verificar** numeración en la RMF 2026 vigente):
- RFC del receptor: `XAXX010101000` (genérico)
- Nombre: `PUBLICO EN GENERAL`
- Régimen fiscal receptor: `616`; UsoCFDI: `S01`; CP del receptor = CP del lugar de expedición del emisor
- Importe: ventas del periodo que no se facturaron de forma individual

## Periodicidad y plazo

El periodo va en el nodo `InformacionGlobal` (CFDI 4.0):
- `Periodicidad`: `01` diaria, `02` semanal, `03` quincenal, `04` mensual, `05` bimestral (bimestral solo para contribuyentes que la regla permite, p. ej. RESICO PF; **verificar**)
- `Meses`: `01`-`12` (para bimestral, `13`-`18`)
- `Año`: año del periodo
- Plazo: dentro de las **24 horas** siguientes al cierre del periodo elegido (regla 2.7.1.21 RMF; confianza media, verificar texto 2026)
- Mantén la misma periodicidad de forma consistente; los tickets/notas de venta se emiten primero y la global los ampara después

## Estructura del CFDI global (Guía de llenado SAT)

```json
{
  "tipo_comprobante": "I",
  "fecha": "2026-04-01T10:00:00",
  "moneda": "MXN",
  "metodo_pago": "PUE",
  "forma_pago": "01",
  "exportacion": "01",

  "informacion_global": {
    "periodicidad": "04",
    "meses": "03",
    "año": 2026
  },

  "emisor": {
    "rfc": "RDE200101AB1",
    "nombre": "RESTAURANTE DEMO",
    "regimen_fiscal": "601",
    "cp_lugar_expedicion": "06700"
  },

  "receptor": {
    "rfc": "XAXX010101000",
    "nombre": "PUBLICO EN GENERAL",
    "regimen_fiscal": "616",
    "cp_domicilio_fiscal": "06700",
    "uso_cfdi": "S01"
  },

  "conceptos": [
    {
      "clave_prod_serv": "01010101",
      "no_identificacion": "T-000123",
      "cantidad": 1,
      "clave_unidad": "ACT",
      "descripcion": "Venta",
      "valor_unitario": 862.07,
      "importe": 862.07,
      "objeto_imp": "02",
      "traslados": [{"impuesto": "002", "tipo_factor": "Tasa", "tasa_o_cuota": "0.160000", "base": 862.07, "importe": 137.93}]
    }
  ],

  "subtotal": 145000.00,
  "iva_trasladado": 23200.00,
  "total": 168200.00
}
```

Notas de llenado:
- `ClaveProdServ 01010101`, `ClaveUnidad ACT`, `Descripción "Venta"` y en `NoIdentificacion` el **folio del ticket/nota de venta**. La Guía de llenado pide identificar cada comprobante de operación (un concepto por ticket); algunos PAC aceptan agrupar — sigue lo que diga tu PAC y la guía vigente (ver `cfdi-emision` de `_shared`)
- La sección `conceptos` arriba muestra **un** ticket; el subtotal/total corresponden a la suma de todos los tickets del mes (145,000 + 16% = 168,200)
- No existe una "leyenda" obligatoria de factura global: el periodo se acredita con `InformacionGlobal`
- El RFC y nombre del emisor son de ejemplo

## Forma de pago cuando hubo varias

Con método `PUE`, en `FormaPago` se registra la forma con la que se recibió el **mayor importe** del periodo (Guía de llenado). Alternativa válida y más limpia para conciliar: emitir una global por cada forma de pago (`01` efectivo, `04` tarjeta de crédito, `28` tarjeta de débito, `03` transferencia). No uses `99` con PUE.

## Cómo calcular el monto de la global

```
ventas_totales_periodo   = ventas_salon + ventas_para_llevar + ventas_via_plataformas   (precio al cliente, con IVA)
ventas_con_cfdi_individual = ventas_b2b + ventas_con_rfc_solicitado
ventas_publico_global    = ventas_totales_periodo - ventas_con_cfdi_individual
```

Las ventas por Rappi / Uber Eats / DiDi Food son ventas **del restaurante al consumidor final**: van en la global (o en CFDI individual si el cliente lo pide), por el precio cobrado al cliente, **no** por el neto que deposita la plataforma. Verifica el contrato: si una plataforma opera como revendedora (te compra y revende), entonces sí se factura a la plataforma.

Ejemplo (mes de marzo):
- Ventas totales con IVA: $480,000 (incluye $65,000 vendidos vía plataformas)
- Clientes que pidieron factura: $48,000 (10% del monto)
- **Ventas a público en general**: $480,000 − $48,000 = **$432,000** con IVA
- Subtotal: $432,000 / 1.16 = $372,413.79; IVA 16%: $59,586.21

## Implicaciones para el restaurante

### ISR
- Todas las ventas son ingreso acumulable (con o sin factura individual). La global las documenta ante el SAT
- Comisiones de plataformas: gasto deducible con el CFDI que emite la plataforma al restaurante

### IVA trasladado
- 16% sobre alimentos preparados. 8% solo si el restaurante aplica el estímulo de región fronteriza (decreto vigente a 31-12-2026, con aviso al SAT)

### Retenciones de plataformas (si vendes por Rappi / Uber Eats / DiDi Food)
La plataforma te entrega un **CFDI de Retenciones e información de pagos**; las retenciones no reducen el monto de la global, se acreditan en tu declaración:
- **ISR**: 2.5% sobre ingresos sin IVA para enajenación de bienes/servicios, tanto persona física (sustituye el 1% del Art. 113-A fr. III LISR; 20% si no da RFC, Art. 113-C fr. IV) como persona moral (acreditable; 20% si la PM no da su RFC). Fuente: Art. 25 fr. VI Ley de Ingresos de la Federación 2026 (DOF 07-11-2025)
- **IVA**: 50% del IVA cobrado (Art. 18-J fr. II inciso a) LIVA para PF; Art. 25 fr. IX LIF 2026 lo extiende a PM). 100% si la PF no proporciona RFC
- PF con ingresos solo por plataformas ≤ $300,000 anuales pueden optar por que las retenciones sean pago definitivo (Art. 113-B LISR; IVA Art. 18-M LIVA)

### Conciliación
- Global + facturas individuales ≈ depósitos bancarios + efectivo en caja (+ retenciones y comisiones de plataformas)

## Casos edge

### Cliente pide factura después de emitida la global
- Emitir el CFDI individual y **no** dejar la misma venta en la global: o se cancela y re-emite la global sin ese ticket, o se ajusta conforme a la regla vigente de la RMF. No dupliques ingreso ni IVA
- Fija una política de "solicitud de factura dentro del mismo mes" en tus tickets

### Empleados que comen en el restaurante
- Si es prestación sin cobro: no es venta, no va a la global (registrar como costo)
- Si se les cobra: es venta y entra en la global

### Cliente con tarjeta corporativa que no pidió factura
- Entra en la global. Es problema del cliente no poder deducir; para el restaurante no hay ilegalidad

## Output estructurado

```json
{
  "cfdi_publico_global": {
    "periodo": "2026-03",
    "periodicidad": "04",
    "ventas_totales_mxn": 480000.00,
    "ventas_con_cfdi_individual_mxn": 48000.00,
    "de_las_cuales_via_plataformas_mxn": 65000.00,
    "cfdi_emitido": {
      "uuid": "ABCD-1234-...",
      "fecha_emision": "2026-04-01T10:00:00",
      "subtotal_mxn": 372413.79,
      "iva_mxn": 59586.21,
      "total_mxn": 432000.00,
      "forma_pago": "01",
      "criterio_forma_pago": "forma con mayor importe del periodo"
    },
    "retenciones_plataformas_a_conciliar": [
      {"plataforma": "rappi", "cfdi_retenciones_recibido": false}
    ],
    "siguientes_pasos": [
      "Descargar CFDI de retenciones y de comisiones de cada plataforma",
      "Conciliar global + individuales contra depósitos y caja"
    ]
  }
}
```

> Validación profesional: confirma periodicidad, tratamiento de plataformas y retenciones con tu contador antes de timbrar.

## Validación pendiente

- Numeración y texto de la regla de factura global en la RMF 2026 (plazo de 24 h, periodicidad bimestral)
- Guía de llenado vigente: un concepto por ticket vs agrupado
- Modelo contractual de cada plataforma (intermediaria vs revendedora)
