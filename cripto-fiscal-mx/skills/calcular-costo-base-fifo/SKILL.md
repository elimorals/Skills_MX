---
name: calcular-costo-base-fifo
description: Calcula costo base FIFO (First In First Out) por activo. SAT permite FIFO o promedio ponderado. Importante porque determina la ganancia/pérdida gravable de cada venta. Usar cuando el usuario diga costo base, FIFO cripto, calcular ganancia.
allowed-tools: Read, Write
---

# Costo base FIFO

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
                "costo_unitario_mxn": op.valor_mxn_dia / op.cantidad_recibida + op.fee_mxn
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
        "neto_gravable_mxn": str(ganancia_realizada - pérdida_realizada),
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
  "neto_gravable_mxn": "33000.00",
  "holdings_finales_valor_mxn": "517800.00",
  "ganancia_latente_mxn": "85000.00"
}
```
