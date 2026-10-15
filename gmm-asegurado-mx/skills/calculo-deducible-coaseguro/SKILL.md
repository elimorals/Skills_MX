---
name: calculo-deducible-coaseguro
description: Calcula cuánto pagará el asegurado vs cuánto la aseguradora al usar el GMM. Aplica deducible (lo primero que sale del bolsillo) + coaseguro (%X después del deducible). En GMM individual mexicano el deducible y el tope de coaseguro suelen aplicarse por padecimiento/accidente (no por año calendario); la skill lo confirma contra tus condiciones generales. Usar cuando el usuario diga cuánto pago, cuanto cubre seguro, calcular gmm.
allowed-tools: Read, Write
---

# Cálculo deducible + coaseguro

## Algoritmo

```python
def calcular_pago_evento(costo_total: Decimal, deducible: Decimal, coaseguro_pct: Decimal,
                         tope_coaseguro: Decimal, deducible_ya_pagado: Decimal,
                         coaseguro_ya_pagado: Decimal = Decimal("0")) -> dict:
    # deducible_ya_pagado / coaseguro_ya_pagado: lo pagado en ESTE padecimiento
    # (o en el periodo que diga la póliza, si su deducible es anual)
    deducible_aplicable = max(Decimal("0"), min(deducible - deducible_ya_pagado, costo_total))

    # Coaseguro sobre el excedente del deducible
    excedente = max(0, costo_total - deducible_aplicable)
    coaseguro_bruto = excedente * coaseguro_pct
    coaseguro_aplicable = min(coaseguro_bruto, max(Decimal("0"), tope_coaseguro - coaseguro_ya_pagado))

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

Cirugía de apéndice $180,000 MXN (gastos cubiertos según tabulador). Deducible $30,000, coaseguro 10%, tope de coaseguro $50,000, primer evento del padecimiento.

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

## Ajustes que cambian el resultado

- **Tabulador de honorarios**: si el médico cobra arriba del tabulador de la aseguradora, la diferencia la pagas tú además del deducible y coaseguro.
- **Nivel hospitalario**: usar un hospital de nivel superior al contratado suele subir el coaseguro.
- **Accidentes**: muchas pólizas eliminan deducible si el gasto inicial supera cierto monto.
- **Gastos no cubiertos** (artículos personales, acompañante) quedan fuera del cálculo.

Lo que tú pagas (deducible + coaseguro) es deducible en tu anual como gasto hospitalario/médico (D01) si se pagó con medio electrónico; lo que pagó la aseguradora no. Ver `paciente-mx:cfdis-medicos-deducibles-acumulados`.
