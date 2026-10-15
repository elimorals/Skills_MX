---
name: comparador-subrogaciones-bancarias
description: Compara ofertas de subrogación de un crédito hipotecario actual a otro banco con mejor tasa. Subrogación = pasar tu hipoteca a otro banco que paga tu saldo, con costos menores que un crédito nuevo pero no nulos. Calcula ahorro real considerando todos los costos (avalúo, notario, comisión de apertura del nuevo banco) y break-even. Varios bancos en MX ofrecen productos de mejora de hipoteca; compara su CAT. Usar cuando el usuario diga subrogar hipoteca, mejor tasa hipoteca, cambiar banco hipotecario, comparar hipotecas. NO usar para tramitar la subrogación (eso es proceso bancario).
allowed-tools: Read, Write
---

# Comparador subrogaciones hipotecarias

## Concepto

Subrogación hipotecaria: trasladas tu hipoteca a otro banco que te ofrece mejor tasa. Pagas avalúo, gastos notariales y, en su caso, comisión de apertura: el cálculo de break-even es obligatorio.

## Inputs

```json
{
  "hipoteca_actual": {
    "banco": "Banorte",
    "saldo_mxn": "1500000.00",
    "tasa_anual": 10.8,
    "plazo_restante_meses": 240,
    "pago_mensual_mxn": "15279.18"
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
    pago_nuevo = actual["saldo_mxn"] * (tasa_nueva / (1 - (1 + tasa_nueva)**(-actual["plazo_restante_meses"])))

    # Ahorro mensual
    ahorro_mensual = actual["pago_mensual_mxn"] - pago_nuevo

    # Costos totales de subrogar
    costos = (
        actual["saldo_mxn"] * (nueva["comision_apertura_pct"] / 100)
        + nueva["avaluo_mxn"]
        + nueva["gastos_notariales_mxn"]
    )

    # Break-even (meses para recuperar costos)
    breakeven_meses = costos / ahorro_mensual if ahorro_mensual > 0 else None

    # Ahorro total en plazo restante
    ahorro_total = (ahorro_mensual * actual["plazo_restante_meses"]) - costos

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

Cálculo: $1,500,000 a 10.8% y 240 meses → $15,279.18. BBVA 9.2% → $13,689.43; costos 0 + 8,000 + 15,000. Santander 9.5% → $13,981.97; costos 0.5% × 1,500,000 = 7,500 + 8,500 + 12,000 = 28,000. Ahorro total = ahorro mensual × 240 − costos (sin descontar a valor presente).

```json
{
  "actual": {"banco": "Banorte", "tasa": 10.8, "pago_mensual_mxn": "15279.18"},
  "comparativa": [
    {
      "banco": "BBVA",
      "tasa_nueva": 9.2,
      "pago_mensual_nuevo_mxn": "13689.43",
      "ahorro_mensual_mxn": "1589.75",
      "costos_subrogacion_mxn": "23000.00",
      "breakeven_meses": 14.5,
      "ahorro_total_plazo_mxn": "358540.13",
      "recomendado": true
    },
    {
      "banco": "Santander",
      "tasa_nueva": 9.5,
      "pago_mensual_nuevo_mxn": "13981.97",
      "ahorro_mensual_mxn": "1297.21",
      "costos_subrogacion_mxn": "28000.00",
      "breakeven_meses": 21.6,
      "ahorro_total_plazo_mxn": "283331.22",
      "recomendado": true
    }
  ],
  "mejor_oferta": "BBVA",
  "ahorro_vs_segunda_oferta": "$75,208.91",
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
| Pocos años restantes de plazo | El ahorro se acumula en menos meses: puede no cubrir los costos (revisa break-even) |
| Crédito en mora | Subrogación complicada — primero regularizar |
| Hipoteca cofinanciada (INFONAVIT + banco) | Solo subrogar la parte del banco |

## ⚠ Compliance

- Tasas cambian a diario — solicitudes con vigencia 30 días típicamente
- `vigencia_validada: false`
