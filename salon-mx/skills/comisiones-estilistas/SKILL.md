---
name: comisiones-estilistas
description: Cálculo de comisiones para estilistas, barberos, esteticistas en salones mexicanos. Soporta modelos fijo (%), escalonado por volumen mensual, mixto (fijo + comisión sobre umbral), por tipo de servicio (color comisión distinta a corte), bonos por retención de clientes, y descuento por producto usado en exceso. Genera reporte mensual por estilista con detalle de servicios atendidos y propinas registradas. Incluye piso de salario mínimo, renta de silla vs empleado (riesgo de relación laboral) y retenciones si el estilista factura. Usar cuando el usuario diga calcular comisiones, pago estilista, sueldo barbero, cierre mes salón, propinas, bonos retención, renta de silla, estilista por honorarios. NO usar para tarifario (otro skill) ni agenda (otro skill).
allowed-tools: Read, Write, Edit, Bash
---

# Comisiones de estilistas

Estructura el pago variable de un equipo de salón.

## Modelos de comisión

### Modelo A: Fijo lineal
```
comision = ingresos_estilista × 0.30  # 30% de lo que generó
```

Simple pero no incentiva volumen.

### Modelo B: Escalonado por volumen mensual

El rango se determina con los **ingresos brutos** del mes; el porcentaje se aplica sobre la base que el contrato defina (brutos o netos de producto). Escríbelo en el contrato para evitar disputas.

```
si ingresos_mes <= $30,000  → 25%
si ingresos_mes $30,001-$60,000 → 32% sobre el TOTAL
si ingresos_mes $60,001-$100,000 → 38% sobre el TOTAL
si ingresos_mes > $100,000 → 42% sobre el TOTAL
```

Incentiva fuerte volumen. Cuidar el "salto" — un estilista que está cerca del umbral va a empujar.

### Modelo C: Mixto fijo + comisión sobre umbral

```
sueldo_base = $10,000 fijo mensual
si ingresos_mes > $20,000:
  bono = (ingresos_mes - $20,000) × 0.35
sueldo_total = sueldo_base + bono
```

Da estabilidad al estilista + incentivo claro. Más caro para el salón si no genera.

⚠ **Piso legal para empleados**: el salario (base + comisiones) nunca puede quedar debajo del mínimo (Art. 85 LFT). Salario mínimo 2026: $315.04 diarios general / $440.87 ZLFN → ≈ $9,577 al mes (×30.4) en zona general. Si un mes la comisión no alcanza, el salón paga la diferencia. Esto aplica a los modelos A, B, D y E cuando el estilista es empleado.

### Modelo D: Por tipo de servicio

```
corte_basico: 30% comisión
color_tinte: 40% (más complejo, premium)
mechas / decoloracion: 45% (alta especialización)
tratamiento: 35%
producto_vendido: 15% (recomendación retail)
```

Premia especialización. Requiere bitácora detallada por servicio.

### Modelo E: Bonos por retención

Bono mensual por clientes que regresan dentro de N días:

```
si cliente_regresa <= 45 días: +$30 MXN al estilista
si cliente_regresa 46-90 días: +$15 MXN
si NO regresa en 90 días: -$10 MXN (solo reduce el bono de ese mes; nunca baja de $0)
```

Premia retention, no solo volumen. Reduce churn.

## Variables que afectan la comisión

### Producto usado
Si el estilista usa más producto del estándar (cabello largo + tinte completo):
- Estándar: comisión normal
- 50%+ por encima: el % de comisión de ese servicio baja 5 puntos (debe estar pactado por escrito antes, no aplicarse retroactivo)
- 100%+ por encima: revisión con el encargado y capacitación

⚠ Si el estilista es **empleado**, el salón **no puede cobrarle el producto ni multarlo**: la LFT prohíbe las multas (Art. 107) y solo permite los descuentos al salario del Art. 110 (anticipos, pagos en exceso, errores/pérdidas con límites, etc.). "Que pague el excedente" como medida disciplinaria es ilegal para un trabajador.

### Propinas
Las propinas son del estilista (el salón no se queda con ellas ni comisiona sobre ellas):
- Propina en efectivo: va directo al estilista. Sigue siendo ingreso del estilista para efectos de ISR; el salón no la registra como venta.
- Propina con tarjeta/transferencia: entra a la cuenta del salón; regístrala por separado de la venta (no en el CFDI del servicio como ingreso del salón) y entrégala al estilista. Si el estilista es empleado, lo usual es dispersarla vía nómina como percepción gravada; el tratamiento para IMSS e ISN depende del caso — **validar con contador** (el Art. 346 LFT que integra propinas al salario es del capítulo de hoteles, restaurantes y bares; para salones no hay regla expresa).

⚠ Las propinas son **ingreso del estilista**, no del salón.

### Anti-fraude
- Cita registrada en sistema (no fuera de él)
- Pago capturado en POS (no en efectivo "off-the-books")
- Servicio reportado con duración y producto realizado
- Foto de antes/después si aplica (opcional para auditoria)

## Cierre mensual

```
para cada estilista:
  ingresos_brutos = sum(servicios_completados.precio del mes)
  costo_producto = sum(productos_usados.costo)
  ingresos_netos = ingresos_brutos - costo_producto

  según modelo: calcular comision
  sumar propinas registradas (no comisionables)
  restar adelantos / préstamos
  calcular ISR + IMSS si aplica

pago_neto_estilista = comisión + propinas - adelantos - ISR - IMSS
```

## Salón sub-arrenda silla vs empleado

Modelo distinto si el estilista renta silla:

| Modelo empleado | Modelo silla sub-arrendada |
|---|---|
| Salón fija el precio | Estilista fija el precio |
| Salón compra producto | Estilista compra propio |
| Comisión 25-40% | Salón cobra renta fija $5-15k/mes |
| Salón da prestaciones | Estilista paga sus propios IMSS/SAT |
| Salón retiene ISR | Estilista tributa por su cuenta (actividad empresarial/profesional o RESICO) |

Implicaciones fiscales:
- **Empleado**: salón timbra CFDI de nómina, retiene ISR (Art. 96 LISR), retiene la cuota obrera IMSS y paga cuotas patronales IMSS, INFONAVIT (5%) e ISN estatal. Comisiones, bonos y propinas que pasen por nómina son percepciones gravadas.
- **Silla sub-arrendada**: el **salón** factura la renta de la silla al estilista (CFDI de ingreso con IVA 16%); el estilista factura **directo al cliente** sus servicios. Si en vez de rentar silla el estilista le factura sus servicios al salón y el salón es **persona moral**, el salón retiene: ISR 10% (honorarios, Art. 106 LISR) o 1.25% si el estilista está en RESICO (Art. 113-J LISR), más 2/3 del IVA (10.6667%, Art. 1-A fr. II a) LIVA). Si el salón es persona física, no retiene. Ver `iva-retenciones-mx`.

⚠ **Riesgo de relación laboral encubierta**: la LFT presume relación de trabajo entre quien presta un trabajo personal y quien lo recibe (Art. 21 LFT); lo que cuenta es la subordinación (Art. 20), no el nombre del contrato. Si el salón fija horario, precios, agenda, uniforme y da el producto, el "estilista independiente" muy probablemente es trabajador, con riesgo de demanda laboral y de capitales constitutivos/omisiones IMSS. La renta de silla real implica que el estilista controla precio, agenda y clientela. **Validar con abogado laboral y contador.**

## Output estructurado

```json
{
  "cierre_mensual": {
    "estilista": "Ana",
    "mes": "2026-03",
    "modelo_comision": "escalonado",
    "ingresos_brutos_mxn": 65000.00,
    "costo_producto_mxn": 9500.00,
    "ingresos_netos_mxn": 55500.00,
    "rango_alcanzado": "brutos $65k (rango $60k-$100k) → 38% aplicado sobre netos de producto",
    "_nota": "ISR e IMSS de este ejemplo son ilustrativos; calcúlalos con la tarifa del Art. 96 LISR y el SBC real",
    "comision_calculada_mxn": 21090.00,
    "bonos_retencion_mxn": 1200.00,
    "propinas_registradas_mxn": 4800.00,
    "adelantos_descuento_mxn": 3000.00,
    "isr_retenido_mxn": 2100.00,
    "imss_retenido_mxn": 850.00,
    "pago_neto_estilista_mxn": 21140.00,
    "servicios_atendidos": 87,
    "clientes_recurrentes": 56,
    "tasa_retencion_clientes": 0.64
  }
}
```

## Validación pendiente

- Modelos de comisión típicos en MX por nivel/ciudad
- Tarifas de renta de silla en CDMX, GDL, MTY
- Cálculo exacto de ISR/IMSS por estilista (usar tarifa vigente y SBC; este skill no lo hace)
- Casos límite (estilista jr aprendiz, vacaciones, incapacidad)

⚠ Lo laboral y fiscal de este skill es orientativo: validar con contador y abogado laboral antes de pagar o firmar contratos.

## Ver también

- `agenda-citas-salon` — para tracking de servicios atendidos
- `servicios-tarifario` — para precios base
- `retencion-clientes-loyalty` — para bonos por retorno
