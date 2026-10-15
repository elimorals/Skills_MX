---
name: delivery-aggregators
description: Operación con plataformas de delivery en México (Rappi, DiDi Food, Uber Eats): margen real con la comisión de tu contrato, gestión de pedidos, conciliación de pagos contra estados de cuenta, devoluciones (pedido equivocado, calidad, no entregado), retenciones ISR/IVA de plataformas 2026 (Art. 113-A LISR, 18-J LIVA, LIF 2026) y cómo facturar esas ventas. Usar cuando el usuario diga Rappi, DiDi Food, UberEats, Uber Eats, aggregator, plataforma de delivery, retención Rappi, comisión delivery, conciliar pagos, devoluciones delivery. NO usar para ingeniería menú (otro skill) ni inventario.
allowed-tools: Read, Write, Edit
---

# Delivery aggregators — México

## Las 3 plataformas principales

| Plataforma | Comisión de referencia | Pago al restaurante |
|---|---|---|
| **Rappi** | 25-35% (verificar en tu contrato) | según contrato |
| **DiDi Food** | 25-35% (verificar en tu contrato) | según contrato |
| **Uber Eats** | 25-35% (verificar en tu contrato) | según contrato |

⚠ **Confianza baja**: ninguna de las tres publica una tabla oficial de comisiones para México; cada restaurante negocia la suya y cambia por plan (con o sin entrega propia), promociones y zona. Los rangos son referencia de mercado. **Siempre toma la comisión del contrato o del estado de cuenta del restaurante**, nunca de esta tabla.

Mercado Libre no opera delivery de comida preparada; no lo uses como canal de restaurante.

## Datos desde los MCP (qué sí existe)

| MCP | Estado | Qué puedes pedir |
|---|---|---|
| `mp_rappi_partners` | Real sin validar; credenciales solo para aliados aprobados por Rappi | `rappi_listar_ordenes` (solo órdenes nuevas, sin histórico), `rappi_consultar_orden`, `rappi_listar_productos_menu`, `rappi_actualizar_disponibilidad`. `rappi_consultar_ranking_zona` y `rappi_estimar_comisiones_mes` devuelven `ConfigError` (`sin_endpoint`) con credenciales |
| `mp_didi_food_partners` | Sin API pública | Con credenciales devuelve `ConfigError`; sin ellas, datos simulados |
| `mp_uber_eats_partners` | Sin API pública | Con credenciales devuelve `ConfigError`; sin ellas, datos simulados |

Reglas:
- Si una respuesta trae `simulated: true`, no la uses para conciliar ni para decidir: dilo al usuario
- Si recibes `ConfigError`, pide al usuario el **estado de cuenta / reporte de liquidación** exportado del portal de la plataforma (CSV o PDF) y concilia sobre ese archivo
- Las comisiones reales salen del estado de cuenta, no de un endpoint

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
  "comision_contrato_porcentaje": 0.30,
  "comision_mxn": 109.50,
  "ingreso_antes_iva_comision_y_retenciones_mxn": 255.50,
  "tarifa_cliente_envio_mxn": 45.00,
  "propina_cliente_mxn": 35.00,
  "total_cliente_pago_mxn": 445.00,
  "estado": "entregado",
  "tiempo_promesa_min": 35,
  "tiempo_real_min": 32,
  "rating_cliente": 5
}
```

## Diferencias a revisar por plataforma

No hay datos públicos confiables que permitan afirmar cuál cobra más o paga más rápido. Compara con tus propios contratos:
- Comisión por pedido y si cambia con entrega propia vs repartidor de la plataforma
- Costo de promociones (quién absorbe el descuento)
- Calendario de pagos y retenciones aplicadas
- Política de contracargos y pedidos no entregados
- Exclusividad y penalizaciones

## Cálculo de margen real

```
margen_carta_directo = precio_carta - food_cost
margen_via_aggregator = precio_carta × (1 - comision) - food_cost
diferencia = margen_carta_directo - margen_via_aggregator
```

Ejemplo:
- Orden de tacos $145 con food cost $35 (comisiones ilustrativas, usa las de tu contrato)
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
- Si lo haces, que el precio publicado en la app sea el que se cobra (LFPC: precio total visible)

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

Cada plataforma liquida en el calendario de tu contrato con un reporte detallado:

```
deposito_esperado = sum(pedidos_periodo × (subtotal - comision_con_IVA - chargebacks - devoluciones)) - retenciones_ISR - retenciones_IVA
```

⚠ Verificar:
- Comisión cobrada vs contrato (a veces aggregator "aumenta" sin avisar)
- Devoluciones aplicadas correctamente (no doble cobro)
- Chargebacks por contracargos del banco al aggregator (raros pero ocurren)
- Promos activas (descuentos asumidos correctamente)

## Devoluciones

| Tipo | Responsable | Acción |
|---|---|---|
| Plato no entregado / desaparecido | Según contrato (usualmente la plataforma) | Revisar el estado de cuenta: que no te lo descuenten |
| Plato frío / mal estado / equivocado | Restaurante | Restaurante absorbe costo |
| Cliente cancela post-preparado | Cliente | Pierde el pedido (cobro completo) |
| Repartidor no encontró al cliente | Según contrato | Documentar con el ID del pedido |

Bitácora trazable por pedido devuelto.

## CFDI y retenciones con plataformas

### Quién factura a quién (modelo intermediario, el usual)
- La venta es **del restaurante al consumidor**: se ampara con CFDI individual si el cliente lo pide o dentro de la **factura global** (skill `cfdi-publico-global`) por el precio cobrado al cliente
- La plataforma emite al restaurante un CFDI por su **comisión** (gasto deducible) y un **CFDI de Retenciones e información de pagos**
- Si tu contrato dice que la plataforma te **compra** y revende, entonces sí facturas a la plataforma. Revisa el contrato; no asumas
- No uses RFC de plataformas "de memoria": tómalos del CFDI que te emiten

### Retenciones 2026 (las aplica la plataforma sobre el precio sin IVA)
| Concepto | Persona física | Persona moral | Fuente |
|---|---|---|---|
| ISR | 2.5% (sustituye el 1% del Art. 113-A fr. III LISR); 20% sin RFC (Art. 113-C fr. IV) | 2.5%, acreditable; 20% si no da RFC | Art. 25 fr. VI LIF 2026 (DOF 07-11-2025) |
| IVA | 50% del IVA cobrado; 100% sin RFC | 50% del IVA cobrado | Art. 18-J fr. II a) LIVA; Art. 25 fr. IX LIF 2026 |

- PF con ingresos solo por plataformas ≤ $300,000 en el año anterior pueden optar por retención como pago definitivo (Art. 113-B LISR; IVA Art. 18-M LIVA)
- La venta de comida es "enajenación de bienes" (fr. III), no "entrega de bienes" (fr. I, 2.1%, que aplica al repartidor)

Ejemplo de un pedido de $365 con IVA a persona física:
- Base sin IVA: 365 / 1.16 = $314.66; IVA: $50.34
- ISR retenido: 314.66 × 2.5% = $7.87
- IVA retenido: 50.34 × 50% = $25.17

> Validación profesional: las retenciones se acreditan en tus declaraciones; confirma con tu contador el régimen (PF actividad empresarial, RESICO, PM) antes de presentar.

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
      "Comisión efectiva Uber Eats 35% vs 30% del contrato — reclamar",
      "Falta CFDI de retenciones de DiDi Food de marzo"
    ],
    "recomendaciones": [
      "Negociar con UberEats por volumen creciente",
      "Considerar pausar promo Rappi que no genera ROI"
    ]
  }
}
```

## Validación pendiente

- Comisiones reales por contrato (no hay fuente oficial pública)
- Cláusulas de devolución y contracargos por plataforma
- Modelo contractual (intermediaria vs revendedora) de cada plataforma
