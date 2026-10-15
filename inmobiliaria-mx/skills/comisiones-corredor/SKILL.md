---
name: comisiones-corredor
description: Cálculo de comisiones de corredor inmobiliario en México. Venta: típico 3-7% del precio venta (50/50 entre corredor cliente y corredor dueño). Renta: 1 mes de renta como honorario one-time. Comisión de administración (5-10% mensual si el corredor administra la propiedad). Considera implicaciones fiscales (PF actividad empresarial o RESICO, PM), retenciones si el cliente es PM y obligaciones antilavado (LFPIORPI) en intermediación inmobiliaria. Usar cuando el usuario diga comisión corredor, honorarios broker, cuánto cobro venta, cuánto cobro renta, comisión inmobiliaria. NO usar para screening (otro skill) ni contratos (otro skill).
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

Si solo hay 1 corredor (representa a ambos): cobra el total.

⚠ Conflicto de interés: si cobras a ambas partes, transpárentalo por escrito con las dos.

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

### Si corredor es Persona Física
- CFDI tipo I; IVA 16%
- La comisión mercantil es actividad empresarial (régimen 612 o RESICO 626)
- Si el cliente es PM: retiene 2/3 del IVA (Art. 1-A fr. II a) LIVA, comisiones). ISR: sin retención en 612 (el Art. 106 LISR solo aplica a servicios profesionales); 1.25% si el corredor es RESICO (Art. 113-J). Consistente con `iva-retenciones-mx`

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
  - Corredor vendedor: 3% = $162,000 + IVA = $187,920 (menos retenciones si PM)
  - Corredor comprador: 3% = $162,000 + IVA = $187,920

CFDI del corredor del vendedor:
  Subtotal: $162,000
  IVA 16%: $25,920
  Total: $187,920
  Si cliente es PM (corredor PF régimen 612):
    Retención IVA 2/3: $17,280
    Pago neto al corredor: $170,640
  Si el corredor es RESICO PF: además ISR 1.25% = $2,025 → neto $168,615
```

### Caso 2: Renta departamento $18,500 MXN/mes

```
Honorario one-time: $18,500 + IVA $2,960 = $21,460
Si cliente es PM (corredor PF 612):
  Retención IVA 2/3: $1,973.33
  Pago neto: $19,486.67
Si el corredor es RESICO PF: además ISR 1.25% = $231.25 → neto $19,255.42
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
- Efectivo: evitarlo. La LFPIORPI (Art. 32 fr. I) prohíbe pagar en efectivo la transmisión de inmuebles por 8,025 UMA o más (UMA 2026 $117.31 → $941,412.75)

⚠ Antilavado (LFPIORPI Art. 17 fr. V, intermediación en transmisión de inmuebles): identificar siempre al cliente; aviso a la UIF vía portal SAT cuando la operación alcance 8,025 UMA ($941,412.75). La reforma DOF 16-07-2025 modificó esta ley: **verificar** umbral y fracción vigentes antes de asesorar

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
      "isr_retenido_612": 0,
      "iva_2_tercios": 17_280,
      "pago_neto_a_corredor_mxn": 170_640
    },
    "cfdi_requerido": true,
    "metodo_pago_recomendado": "transferencia_spei",
    "fecha_pago_estimada": "a la escritura notarial",
    "alertas": [
      "Operación de $5.4M supera 8,025 UMA: identificar cliente y presentar aviso LFPIORPI (verificar umbral tras reforma 2025)"
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
