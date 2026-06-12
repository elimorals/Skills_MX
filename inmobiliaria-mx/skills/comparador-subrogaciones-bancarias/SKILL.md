---
name: comparador-subrogaciones-bancarias
description: Compara ofertas de subrogación de un crédito hipotecario actual a otro banco con mejor tasa. Subrogación = pasar tu hipoteca a otro banco sin pagar gastos de origen (típicamente promovido). Calcula ahorro real considerando todos los costos (avalúo, notario, comisión de apertura del nuevo banco) y break-even. En MX, Santander, BBVA, Banorte y Banamex compiten por subrogaciones. Usar cuando el usuario diga subrogar hipoteca, mejor tasa hipoteca, cambiar banco hipotecario, comparar hipotecas. NO usar para tramitar la subrogación (eso es proceso bancario).
allowed-tools: Read, Write
---

# Comparador subrogaciones hipotecarias

## Concepto

Subrogación hipotecaria: trasladas tu hipoteca a otro banco que te ofrece mejor tasa, sin pagar los gastos de un crédito nuevo (típicamente promovido por bancos para captar saldos).

## Inputs

```json
{
  "hipoteca_actual": {
    "banco": "Banorte",
    "saldo_mxn": "1500000.00",
    "tasa_anual": 10.8,
    "plazo_restante_meses": 240,
    "pago_mensual_mxn": "14200.00"
  },
  "ofertas_recibidas": [
    {"banco": "BBVA", "tasa_anual": 9.2, "comision_apertura_pct": 0, "avaluo_mxn": "8000", "gastos_notariales_mxn": "15000"},
    {"banco": "Santander", "tasa_anual": 9.5, "comision_apertura_pct": 0.5, "avaluo_mxn": "8500", "gastos_notariales_mxn": "12000"}
  ]
}
```

## Cálculo

```python
def comparar_oferta(actual, nueva):
    # Nuevo pago mensual con tasa nueva, mismo plazo
    tasa_nueva = nueva["tasa_anual"] / 12 / 100
    pago_nuevo = actual["saldo"] * (tasa_nueva / (1 - (1 + tasa_nueva)**(-actual["plazo_meses"])))

    # Ahorro mensual
    ahorro_mensual = actual["pago_mensual"] - pago_nuevo

    # Costos totales de subrogar
    costos = (
        actual["saldo"] * (nueva["comision_apertura_pct"] / 100)
        + nueva["avaluo_mxn"]
        + nueva["gastos_notariales_mxn"]
    )

    # Break-even (meses para recuperar costos)
    breakeven_meses = costos / ahorro_mensual if ahorro_mensual > 0 else None

    # Ahorro total en plazo restante
    ahorro_total = (ahorro_mensual * actual["plazo_meses"]) - costos

    return {
        "pago_mensual_nuevo": str(pago_nuevo),
        "ahorro_mensual": str(ahorro_mensual),
        "costos_subrogacion_totales": str(costos),
        "breakeven_meses": breakeven_meses,
        "ahorro_total_neto": str(ahorro_total),
        "recomendado": ahorro_total > 50000 and breakeven_meses < 60
    }
```

## Output

```json
{
  "actual": {"banco": "Banorte", "tasa": 10.8, "pago_mensual_mxn": "14200.00"},
  "comparativa": [
    {
      "banco": "BBVA",
      "tasa_nueva": 9.2,
      "pago_mensual_nuevo_mxn": "12800.00",
      "ahorro_mensual_mxn": "1400.00",
      "costos_subrogacion_mxn": "23000.00",
      "breakeven_meses": 16.4,
      "ahorro_total_plazo_mxn": "313000.00",
      "recomendado": true
    },
    {
      "banco": "Santander",
      "tasa_nueva": 9.5,
      "pago_mensual_nuevo_mxn": "13050.00",
      "ahorro_mensual_mxn": "1150.00",
      "costos_subrogacion_mxn": "27500.00",
      "breakeven_meses": 23.9,
      "ahorro_total_plazo_mxn": "248000.00",
      "recomendado": true
    }
  ],
  "mejor_oferta": "BBVA",
  "ahorro_vs_segunda_oferta": "$65,000",
  "advertencias": [
    "Confirmar que la tasa es FIJA, no variable",
    "Pedir CAT (Costo Anual Total) — incluye seguros obligatorios",
    "Negociar — bancos competidores suelen igualar o mejorar"
  ],
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Tasa variable (UDIs / IIE) | Calcular con expectativa, riesgo de subir |
| Cliente con < 5 años de pagos | Subrogar puede no convenir (mayor parte de pagos van a intereses ya hechos) |
| Crédito en mora | Subrogación complicada — primero regularizar |
| Hipoteca cofinanciada (INFONAVIT + banco) | Solo subrogar la parte del banco |

## ⚠ Compliance

- Tasas cambian a diario — solicitudes con vigencia 30 días típicamente
- `vigencia_validada: false`
