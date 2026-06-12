---
name: comisiones-estilistas
description: Cálculo de comisiones para estilistas, barberos, esteticistas en salones mexicanos. Soporta modelos fijo (%), escalonado por volumen mensual, mixto (fijo + comisión sobre umbral), por tipo de servicio (color comisión distinta a corte), bonos por retención de clientes, y descuento por producto usado en exceso. Genera reporte mensual por estilista con detalle de servicios atendidos y propinas registradas. Usar cuando el usuario diga calcular comisiones, pago estilista, sueldo barbero, cierre mes salón, propinas, bonos retención. NO usar para tarifario (otro skill) ni agenda (otro skill).
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

```
si ingresos_mes <= $30,000  → 25%
si ingresos_mes $30,001-$60,000 → 32% sobre el TOTAL
si ingresos_mes $60,001-$100,000 → 38% sobre el TOTAL
si ingresos_mes > $100,000 → 42% sobre el TOTAL
```

Incentiva fuerte volumen. Cuidar el "salto" — un estilista que está cerca del umbral va a empujar.

### Modelo C: Mixto fijo + comisión sobre umbral

```
sueldo_base = $8,000 fijo
si ingresos_mes > $20,000:
  bono = (ingresos_mes - $20,000) × 0.35
sueldo_total = sueldo_base + bono
```

Da estabilidad al estilista + incentivo claro. Más caro para el salón si no genera.

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
si NO regresa en 90 días: -$10 MXN (deduce de bono)
```

Premia retention, no solo volumen. Reduce churn.

## Variables que afectan la comisión

### Producto usado
Si el estilista usa más producto del estándar (cabello largo + tinte completo):
- Estándar: comisión normal
- 50%+ por encima: comisión -5%
- 100%+ por encima: estilista debe pagar excedente (medida disciplinaria)

### Propinas
Las propinas son del estilista 100% (no comisionables para el salón). Sin embargo:
- Si propina en efectivo: directo al estilista, no se reporta
- Si propina vía pago electrónico: se acumula y se paga en nómina (puede o no ser deducible)

⚠ Las propinas en CFDI/SAT son **ingreso del estilista**. El salón NO las suma a sus ingresos.

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
| Salón retiene ISR | Estilista declara como honorarios |

Implicaciones fiscales:
- **Empleado**: salón retiene ISR + IMSS + INFONAVIT
- **Silla sub-arrendada**: el estilista factura sus servicios al salón (CFDI honorarios) o directo al cliente

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
    "rango_alcanzado": "$60k+ → 38% comisión sobre total",
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
- Implicaciones fiscales precisas (empleado vs honorarios)
- Casos límite (estilista jr aprendiz, vacaciones, incapacidad)

## Ver también

- `agenda-citas-salon` — para tracking de servicios atendidos
- `servicios-tarifario` — para precios base
- `retencion-clientes-loyalty` — para bonos por retorno
