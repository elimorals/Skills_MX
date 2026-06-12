---
name: cfdi-estimacion-obra
description: Emite CFDI por estimación de avance de obra civil con desglose por concepto contratado (clave SAT capítulo construcción 72, 83, 88), avance medido en cantidad o porcentaje contra catálogo de conceptos del contrato, anexo con cálculo de unidades ejecutadas, retención de garantía aplicada (típicamente 5% del importe ejecutado, retenida hasta entrega final), amortización de anticipo si lo hubo, y proyección de saldo del contrato (ejecutado acumulado vs total). Incluye complemento de servicios parciales de construcción cuando aplica (Anexo 20). Diferencia entre contrato a precio alzado (CFDI por estimación con números de obra cerrados) y administración (CFDI por costo real + honorario). Usar cuando el usuario diga "estimación obra", "facturar avance construcción", "CFDI obra civil", "factura constructora", "valuación obra", "estimación contrato precio alzado". NO usar para CFDI de venta de materiales ni para facturación de flete.
allowed-tools: Read, Write, Edit
---

# CFDI por estimación de avance de obra

## Conceptos clave

- **Catálogo de conceptos**: lista de actividades con unidad + precio unitario del contrato
- **Volumen ejecutado**: cantidad realmente hecha en el periodo
- **Estimación**: documento de medición + cálculo, base para el CFDI
- **Retención garantía**: 5% típico, retenido hasta entrega final
- **Anticipo amortizable**: si hubo anticipo, se descuenta proporcionalmente

## Estructura del CFDI

```
Por cada concepto del catálogo:
  Descripcion: "Excavación a cielo abierto material clase II"
  ClaveProdServ: "72100000" (servicios construcción)
  ClaveUnidad: "MTQ" (metro cúbico)
  Cantidad: 850.5
  ValorUnitario: 145.00
  Importe: 123,322.50

Subtotal: $X
- Anticipo amortizado: $Y
- Retención garantía 5%: $Z
+ IVA 16%: $W
Total: $T
```

## Validaciones

1. Cantidad ejecutada acumulada ≤ cantidad contratada
2. Suma de estimaciones previas + actual ≤ total del contrato
3. Si hay anticipo: amortización proporcional aplicada
4. Anexo de cálculo coherente con cantidades del CFDI
