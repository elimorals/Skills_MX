---
name: calcular-costo-base-fifo
description: Calcula el costo base FIFO (primeras entradas, primeras salidas) por criptoactivo para determinar la ganancia o pérdida de cada venta o permuta en MXN. La LISR no fija método para activos fungibles; FIFO es un criterio común que debe documentarse y aplicarse de forma consistente. Usar cuando el usuario diga costo base, FIFO cripto, costo de adquisición cripto, calcular ganancia por venta de bitcoin, ganancia realizada.
allowed-tools: Read, Write
---

# Costo base FIFO

> La LISR exige "costo comprobado de adquisición" (Art. 121 fr. I) actualizado por INPC (Art. 124), pero no dice cómo identificar unidades fungibles. FIFO es defendible si se documenta y se usa siempre igual. Confianza media: validar con contador.

Reglas:
- Costo del lote = (valor MXN pagado + comisión) / cantidad recibida. TC del día de la operación (`mp_banxico.banxico_get_tc_dof`).
- Permutas y rewards crean lotes nuevos al valor de mercado en MXN del día de recepción.
- Transferencias entre wallets propias no crean ni consumen lotes.
- Actualizar el costo por INPC (Art. 124) al calcular la ganancia de cada enajenación (`banxico_get_inpc`).
- Las pérdidas se reportan por separado: criterio conservador, no se restan de las ganancias (ver `calculadora-isr-cripto-detallada`).

## Algoritmo

```python
def calcular_fifo(operaciones: list[OperacionCripto]) -> dict:
    inventario = {}  # activo → lista de lots (cantidad, costo_unitario_mxn)
    ganancia_realizada = Decimal("0")
    pérdida_realizada = Decimal("0")

    for op in sorted(operaciones, key=lambda x: x.fecha_hora):
        if op.tipo == "compra":
            inventario.setdefault(op.activo_recibido, []).append({
                "cantidad": op.cantidad_recibida,
                "costo_unitario_mxn": (op.valor_mxn_dia + op.fee_mxn) / op.cantidad_recibida
            })
        elif op.tipo == "venta":
            cantidad_a_vender = op.cantidad_dada
            ingreso_total = op.valor_mxn_dia
            costo_total = Decimal("0")

            while cantidad_a_vender > 0 and inventario[op.activo_dado]:
                lot = inventario[op.activo_dado][0]
                if lot["cantidad"] <= cantidad_a_vender:
                    costo_total += lot["cantidad"] * lot["costo_unitario_mxn"]
                    cantidad_a_vender -= lot["cantidad"]
                    inventario[op.activo_dado].pop(0)
                else:
                    costo_total += cantidad_a_vender * lot["costo_unitario_mxn"]
                    lot["cantidad"] -= cantidad_a_vender
                    cantidad_a_vender = Decimal("0")

            ganancia = ingreso_total - costo_total
            if ganancia > 0:
                ganancia_realizada += ganancia
            else:
                pérdida_realizada += abs(ganancia)

    return {
        "ganancia_realizada_mxn": str(ganancia_realizada),
        "perdida_realizada_mxn": str(pérdida_realizada),
        "ganancia_gravable_conservadora_mxn": str(ganancia_realizada),  # pérdidas no restadas
        "inventario_final": inventario
    }
```

## Output

```json
{
  "ejercicio": 2026,
  "metodo": "FIFO",
  "operaciones_procesadas": 245,
  "ganancia_realizada_mxn": "45000.00",
  "perdida_realizada_mxn": "12000.00",
  "ganancia_gravable_conservadora_mxn": "45000.00",
  "neto_si_contador_acepta_compensar_mxn": "33000.00",
  "holdings_finales_valor_mxn": "517800.00",
  "ganancia_latente_mxn": "85000.00"
}
```
