---
name: delivery-aggregators
description: Integración con plataformas de delivery en México (Rappi, DiDi Food, UberEats, Mercado Libre Envíos) considerando comisiones distintas (25-35% según aggregator y categoría), promesa de tiempo (express vs estándar), gestión de pedidos pendientes, conciliación de pagos semanales, devoluciones (cliente equivocado, calidad pobre, no entregado), y emisión de CFDI consolidado a nombre del aggregator. Usar cuando el usuario diga Rappi, DiDi Food, UberEats, aggregator, comisión delivery, conciliar pagos, devoluciones delivery. NO usar para ingeniería menú (otro skill) ni inventario.
allowed-tools: Read, Write, Edit
---

# Delivery aggregators — México

## Las 4 plataformas principales 2026

| Aggregator | Comisión típica | Sucursales | Pago semanal |
|---|---|---|---|
| **Rappi** | 28-32% | Variable por categoría | Cada miércoles |
| **DiDi Food** | 25-30% | Más competitivo en suscripción | Cada lunes |
| **UberEats** | 30-35% | Premium en CDMX | Cada lunes |
| **Mercado Libre Envíos** | 5-15% (logística solo) | Restaurantes selectos | Diario |

⚠ Comisiones varían por:
- Tipo de cocina (italiana, mexicana, sushi distintas)
- Volumen del restaurante (descuentos por escala)
- Promociones activas (a veces +5% por exposure)
- Programa Rappi/DiDi/UberEats Plus (a veces +3%)

## Estructura del pedido

```json
{
  "id_pedido": "RAP-2026-0042",
  "aggregator": "rappi",
  "fecha_hora": "2026-03-15T14:32:00",
  "cliente_anonimo": true,
  "items": [
    {"plato": "Tacos al pastor 3pz", "cantidad": 2, "precio_carta_mxn": 290},
    {"plato": "Quesadilla", "cantidad": 1, "precio_carta_mxn": 75}
  ],
  "subtotal_mxn": 365.00,
  "comision_aggregator_porcentaje": 0.30,
  "comision_mxn": 109.50,
  "ingreso_neto_restaurante_mxn": 255.50,
  "tarifa_cliente_envio_mxn": 45.00,
  "propina_cliente_mxn": 35.00,
  "total_cliente_pago_mxn": 445.00,
  "estado": "entregado",
  "tiempo_promesa_min": 35,
  "tiempo_real_min": 32,
  "rating_cliente": 5
}
```

## Diferencias clave por aggregator

### Rappi
- Comisión más alta (28-32% típica)
- Restaurante absorbe costo de envío (cliente solo paga "service fee")
- Mejor para alto volumen + precios premium
- App Rappi Prime: -5% comisión por restaurante

### DiDi Food
- Comisión más competitiva (25-30%)
- Suelen ofrecer mejores promociones
- Más fuerte en MTY, GDL, Querétaro
- Tiempos a veces más largos

### UberEats
- Comisión más alta (30-35%)
- Mejor exposure en CDMX premium
- App pulida + UX cliente
- Servicio al cliente más responsive

### Mercado Libre Envíos
- Solo logística (5-15%)
- Restaurante mantiene relación con cliente final
- Útil para pedidos B2B grandes
- Menos común en restaurantes pequeños

## Cálculo de margen real

```
margen_carta_directo = precio_carta - food_cost
margen_via_aggregator = precio_carta × (1 - comision) - food_cost
diferencia = margen_carta_directo - margen_via_aggregator
```

Ejemplo:
- Taco $145 con food cost $35
- Margen directo: $110 (76%)
- Margen Rappi 30%: $145 × 0.70 - $35 = $101.5 - $35 = $66.5 (46%)
- Margen UberEats 35%: $145 × 0.65 - $35 = $94.25 - $35 = $59.25 (41%)

**Conclusión**: cada pedido de delivery genera ~40% menos margen.

## Estrategias

### A. Solo carta directo (sin aggregators)
- Mayor margen, pero menos volumen
- Requiere delivery propio (motor, conductor, app, etc.)
- Mejor para restaurantes con marca fuerte y zona muy específica

### B. Precio diferente en aggregator
- Subir 10-15% el precio en aggregators para compensar comisión
- Riesgo: cliente puede comparar precios en menú físico vs aggregator
- Más común que se piense

### C. Aggregator-only (dark kitchen)
- Operar sin sucursal física
- Renta solo cocina industrial
- 100% comisiones aggregators
- Margen menor pero costo fijo bajo

### D. Mix balanceado (recomendado para mayoría)
- 60-70% directo + 30-40% aggregators
- Mantiene marca + alcance ampliado
- Permite negociar mejores términos con aggregators

## Conciliación de pagos

Cada aggregator paga semanalmente con reporte detallado:

```
reporte_aggregator = sum(pedidos_semana × (subtotal - comision - chargebacks - devoluciones))
```

⚠ Verificar:
- Comisión cobrada vs contrato (a veces aggregator "aumenta" sin avisar)
- Devoluciones aplicadas correctamente (no doble cobro)
- Chargebacks por contracargos del banco al aggregator (raros pero ocurren)
- Promos activas (descuentos asumidos correctamente)

## Devoluciones

| Tipo | Responsable | Acción |
|---|---|---|
| Plato no entregado / desaparecido | Aggregator | Reembolso 100% al cliente, restaurante NO pierde |
| Plato frío / mal estado / equivocado | Restaurante | Restaurante absorbe costo |
| Cliente cancela post-preparado | Cliente | Pierde el pedido (cobro completo) |
| Driver no encontró cliente | Aggregator | Restaurante a veces conserva pago |

Bitácora trazable por pedido devuelto.

## CFDI con aggregators

### Modelo más común
- Aggregator factura al cliente final
- Restaurante factura al **aggregator** consolidado mensual
- CFDI: RFC del aggregator, UsoCFDI G03

Ejemplo:
- Rappi RFC: REP170913U41
- DiDi RFC: DDI170915AA1
- UberEats RFC: UBE150313QA1 (verificar 2026)

### Detalle del CFDI mensual
- Una factura mensual por aggregator
- Concepto: "Servicios de alimentos y bebidas vía plataforma {{aggregator}}"
- Total: suma de ingresos netos (ya descontada comisión)

## Output estructurado

```json
{
  "analisis_aggregators": {
    "periodo": "2026-03",
    "total_pedidos": 487,
    "distribucion_canal": {
      "directo": {"pedidos": 312, "ingreso_mxn": 145000},
      "rappi": {"pedidos": 95, "ingreso_neto_mxn": 28000, "comision_mxn": 12000},
      "ubereats": {"pedidos": 52, "ingreso_neto_mxn": 14500, "comision_mxn": 7800},
      "didi": {"pedidos": 28, "ingreso_neto_mxn": 8200, "comision_mxn": 3500}
    },
    "ingreso_total_neto_mxn": 195700,
    "comisiones_pagadas_mxn": 23300,
    "comision_efectiva_porcentaje": 0.11,
    "alertas": [
      "UberEats subió comisión 2% en últimos 7 días — revisar contrato",
      "DiDi tiempo promesa 38 min vs 32 real — bueno para SLA"
    ],
    "recomendaciones": [
      "Negociar con UberEats por volumen creciente",
      "Considerar pausar promo Rappi que no genera ROI"
    ]
  }
}
```

## Validación pendiente

- Comisiones reales 2026 por contrato (varían enormemente)
- Cláusulas de devolución específicas por aggregator
- Casos en que aggregator no paga el reporte (resolución legal)
- Impacto fiscal de "cliente final" vs "cliente intermediario" (aggregator)
