---
name: cfdi-estimacion-obra
description: Emite CFDI 4.0 por estimación de avance de obra civil con desglose por concepto contratado (ClaveProdServ del segmento 72, servicios de construcción), avance medido contra el catálogo de conceptos del contrato, anexo con el cálculo de unidades ejecutadas, aplicación del anticipo con el procedimiento de anticipos del Anexo 20 (CFDI relacionado tipo 07), retención de garantía contractual (típicamente 5%, que no es impuesto y se cobra después vía complemento de pago), y saldo del contrato (ejecutado acumulado vs total). Cubre IVA exento en construcción de casa habitación con materiales (Art. 9 fr. II LIVA, Art. 29 RLIVA). Diferencia precio alzado vs administración (costo real + honorario). Usar cuando el usuario diga "estimación obra", "facturar avance construcción", "CFDI obra civil", "factura constructora", "valuación obra", "estimación contrato precio alzado". NO usar para CFDI de venta de materiales ni para facturación de flete.
allowed-tools: Read, Write, Edit
---

# CFDI por estimación de avance de obra

## Conceptos clave

- **Catálogo de conceptos**: actividades con unidad y precio unitario del contrato
- **Volumen ejecutado**: cantidad hecha en el periodo
- **Estimación**: documento de medición y cálculo, base del CFDI
- **Retención de garantía**: pacto contractual (típico 5%) que el cliente no paga hasta la entrega o el fin del periodo de vicios ocultos. **No es un impuesto**: no va como retención en el CFDI
- **Anticipo**: se factura al recibirlo y se aplica en cada estimación con el procedimiento del Anexo 20

## Estructura del CFDI de la estimación

```
Concepto (uno por concepto del catálogo):
  Descripcion: "Excavación a cielo abierto material clase II — Estimación 3"
  ClaveProdServ: clave específica del segmento 72 en c_ClaveProdServ (verificar en el catálogo)
  ClaveUnidad: "MTQ" (metro cúbico)
  Cantidad: 850.5
  ValorUnitario: 145.00
  Importe: 123,322.50
  ObjetoImp: 02

Subtotal:        $123,322.50
IVA 16%:         $ 19,731.60
Total:           $143,054.10
MetodoPago: PPD (el cobro llega después y parte queda retenida en garantía)
```

### Aplicación del anticipo (ejemplo: anticipo de 30% ya facturado)

Sigue el procedimiento de anticipos de la Guía de llenado del Anexo 20 (Apéndice 6):
- CFDI de la estimación relacionado al CFDI del anticipo con `TipoRelacion 07`, y
- CFDI de egreso por la aplicación del anticipo: 30% × 123,322.50 = $36,996.75 + IVA $5,919.48 = **$42,916.23**, también relacionado con tipo 07.

### Garantía y cobro

- Garantía 5% del importe sin IVA: 123,322.50 × 5% = **$6,166.13**
- Cobro ahora: 143,054.10 − 42,916.23 − 6,166.13 = **$93,971.74** → complemento de pago por ese monto
- Saldo insoluto $6,166.13 → segundo complemento de pago cuando se libere la garantía

## Casa habitación

Construir casa habitación aportando materiales y mano de obra está exento de IVA (Art. 9 fr. II LIVA, Art. 29 RLIVA). Si solo se presta mano de obra, o la obra no es casa habitación, causa 16%. Para servicios parciales de construcción de casa habitación existe el complemento "Servicios parciales de construcción" (verificar cuándo es obligatorio en la RMF 2026).

## Validaciones

1. Cantidad ejecutada acumulada ≤ cantidad contratada (excedentes solo con orden de cambio)
2. Suma de estimaciones previas + actual ≤ monto del contrato (+ órdenes de cambio)
3. Anticipo aplicado proporcionalmente y relacionado con tipo 07
4. Anexo de cálculo coherente con las cantidades del CFDI
5. Si el cliente es PM y te pone personal a disposición, revisa si aplica la retención de 6% de IVA (ver `retenciones-repse`)

## ⚠ Compliance

- Valida el procedimiento de anticipos y la clave de producto con tu contador o PAC antes de timbrar.
- Timbrado vía `facturama_timbrar_cfdi` (MCP `mp_facturama_extendido`) solo con credenciales del usuario.
