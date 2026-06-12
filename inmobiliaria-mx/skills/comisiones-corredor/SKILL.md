---
name: comisiones-corredor
description: Cálculo de comisiones de corredor inmobiliario en México. Venta: típico 3-7% del precio venta (50/50 entre corredor cliente y corredor dueño). Renta: 1 mes de renta como honorario one-time. Comisión de administración (5-10% mensual si el corredor administra la propiedad). Considera implicaciones fiscales (PFAE) y retenciones si el cliente es PM. Usar cuando el usuario diga comisión corredor, honorarios broker, cuánto cobro venta, cuánto cobro renta, comisión inmobiliaria. NO usar para screening (otro skill) ni contratos (otro skill).
allowed-tools: Read, Write, Edit
---

# Comisiones de corredor inmobiliario

## Modelos típicos

### Venta de inmueble

**Comisión total** (sobre precio venta):
- Inmueble residencial: 5-7% (depende ciudad)
- Inmueble premium ($10M+): 4-5%
- Terreno o nave industrial: 5-7%
- Inmueble vacante: 3-5%

**Distribución típica entre 2 corredores**:
- 50% corredor del vendedor (representa al dueño)
- 50% corredor del comprador (representa al interesado)

Si solo hay 1 corredor (representa a ambos): cobra el total pero debe declararlo.

⚠ Es ilegal cobrar a ambos sin declararlo (dual agency).

### Renta de inmueble

**Comisión típica**: 1 mes de renta como honorario one-time
- 5,000 MXN/mes → comisión $5,000
- 25,000 MXN/mes → comisión $25,000

**Distribución**:
- 100% corredor que cierra la operación (modalidad típica MX)
- A veces 50/50 si hubo intermediación de otra inmobiliaria

### Administración de propiedad (property management)

**Comisión recurrente**: 5-10% de la renta mensual
- Tareas incluidas: cobranza, mantenimiento, comunicación inquilino, declaración fiscal
- 10,000 MXN/mes × 8% = $800/mes recurrente

## Implicaciones fiscales

### Si corredor es Persona Física (PFAE)
- CFDI tipo I por servicios profesionales
- IVA 16%
- Retención del 10% ISR + 2/3 IVA si cliente es PM (Art. 1-A LIVA)
- Régimen: 626 (RESICO PF) o 612 (Honorarios)

### Si corredor es Persona Moral
- CFDI tipo I por servicios profesionales
- IVA 16%
- Sin retención por el cliente

### IVA y comisión en venta
- Si vende inmueble destinado a casa-habitación → IVA exento (Art. 9-II LIVA)
- Comisión del corredor sí está sujeta a IVA (servicios profesionales)

## Cálculo de ejemplo

### Caso 1: Venta de casa $5,400,000 MXN

```
Comisión total: 6% = $324,000 MXN
Distribución:
  - Corredor vendedor: 3% = $162,000 + IVA = $187,920 (más retenciones si PM)
  - Corredor comprador: 3% = $162,000 + IVA = $187,920

CFDI del corredor del vendedor:
  Subtotal: $162,000
  IVA 16%: $25,920
  Total: $187,920
  Si cliente es PM:
    Retención ISR 10%: $16,200
    Retención IVA 2/3: $17,280
    Pago neto al corredor: $154,440
```

### Caso 2: Renta departamento $18,500 MXN/mes

```
Honorario one-time: $18,500 + IVA = $21,460
Si cliente es PM:
  Retención ISR 10%: $1,850
  Retención IVA 2/3: $1,966.67
  Pago neto: $17,643.33
```

### Caso 3: Administración propiedad $20,000 MXN/mes

```
Comisión mensual: 8% × $20,000 = $1,600 + IVA = $1,856

Por año: $1,600 × 12 = $19,200 + IVA = $22,272
```

## Cobro de comisiones

### Cuándo se cobra
- **Venta**: a la escritura (cuando el cliente firma protocolo notarial)
- **Renta**: a la firma del contrato
- **Administración**: mensual (puede ser quincenal en algunos casos)

### Métodos de pago aceptados
- Transferencia SPEI (preferido)
- Cheque certificado
- Tarjeta de crédito (con comisión adicional 3-5%)
- Efectivo (limitado por Ley Antilavado a $200,000 MXN — Art. 32 LFPLF)

⚠ Reportar a SAT operaciones > $645,000 MXN (Art. 17 LFPL)

## Comisiones inusuales

### Comisión por listings vencidos
- Si dueño retira propiedad antes de cerrar: cobrar gastos directos (fotos, marketing, tiempo invertido)
- Típico: $5,000-15,000 según gastos reales

### Comisión por referido
- Si corredor refiere a colega y este cierra: 25-30% de la comisión del que cerró

### Doble entrega de tarjeta de pago (vender + administrar)
- Si vendes y luego administras la propiedad: comisión completa + servicio recurrente
- Sin descuento por "ya conoces al cliente"

## Output estructurado

```json
{
  "calculo_comision": {
    "operacion": "venta",
    "inmueble": {
      "precio_mxn": 5_400_000,
      "tipo": "departamento_residencial",
      "ubicacion": "Polanco, CDMX"
    },
    "comision_porcentaje": 0.06,
    "comision_total_mxn": 324_000,
    "distribucion": {
      "corredor_vendedor": {
        "porcentaje": 0.50,
        "monto_pre_iva_mxn": 162_000,
        "iva_mxn": 25_920,
        "total_mxn": 187_920
      },
      "corredor_comprador": {
        "porcentaje": 0.50,
        "monto_pre_iva_mxn": 162_000,
        "iva_mxn": 25_920,
        "total_mxn": 187_920
      }
    },
    "retenciones_si_cliente_pm": {
      "isr_10_porcentaje": 16_200,
      "iva_2_tercios": 17_280,
      "pago_neto_a_corredor_mxn": 154_440
    },
    "cfdi_requerido": true,
    "metodo_pago_recomendado": "transferencia_spei",
    "fecha_pago_estimada": "a la escritura notarial",
    "alertas": [
      "Si pago en efectivo > $200k MXN debe reportarse SAT (Ley Antilavado)"
    ]
  }
}
```

## Validación pendiente

- Comisiones reales por ciudad MX 2026
- Acuerdos típicos entre corredor + vendedor (exclusividad)
- Casos en que dueño no quiere pagar (estrategias)
- Software de tracking comisiones (Inmobile, Sumaprop)

## Ver también

- `iva-retenciones-mx` para retenciones detalladas
- `cfdi-emision` para emitir factura del honorario
- `contrato-arrendamiento-mx` para casos de renta
