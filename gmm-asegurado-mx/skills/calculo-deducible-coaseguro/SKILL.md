---
name: calculo-deducible-coaseguro
description: Calcula cuánto pagará el asegurado vs cuánto la aseguradora al usar el GMM. Aplica deducible (lo primero que sale del bolsillo) + coaseguro (%X después del deducible). Importante: deducible y coaseguro tope pueden NO contar antigüedad/eventos previos del año. Usar cuando el usuario diga cuánto pago, cuanto cubre seguro, calcular gmm.
allowed-tools: Read, Write
---

# Cálculo deducible + coaseguro

## Algoritmo

```python
def calcular_pago_evento(costo_total: Decimal, deducible: Decimal, coaseguro_pct: Decimal,
                         tope_coaseguro: Decimal, deducible_ya_pagado_anio: Decimal) -> dict:
    # Si ya pagué todo el deducible este año, no aplica
    if deducible_ya_pagado_anio >= deducible:
        deducible_aplicable = 0
    else:
        deducible_aplicable = min(deducible - deducible_ya_pagado_anio, costo_total)

    # Coaseguro sobre el excedente del deducible
    excedente = max(0, costo_total - deducible_aplicable)
    coaseguro_bruto = excedente * coaseguro_pct
    coaseguro_aplicable = min(coaseguro_bruto, tope_coaseguro)

    pago_asegurado = deducible_aplicable + coaseguro_aplicable
    pago_aseguradora = costo_total - pago_asegurado

    return {
        "costo_total_mxn": str(costo_total),
        "deducible_aplicable_mxn": str(deducible_aplicable),
        "coaseguro_aplicable_mxn": str(coaseguro_aplicable),
        "total_paga_asegurado_mxn": str(pago_asegurado),
        "total_paga_aseguradora_mxn": str(pago_aseguradora)
    }
```

## Ejemplo

Cirugía de apéndice $180,000 MXN. Deducible $30,000, coaseguro 10%, tope $50,000.

- Deducible: $30,000
- Coaseguro: 10% de $150,000 = $15,000
- **Tú pagas: $45,000**
- **Aseguradora paga: $135,000**

## Output

```json
{
  "costo_total_mxn": "180000.00",
  "deducible_aplicable_mxn": "30000.00",
  "coaseguro_aplicable_mxn": "15000.00",
  "total_paga_asegurado_mxn": "45000.00",
  "total_paga_aseguradora_mxn": "135000.00"
}
```
