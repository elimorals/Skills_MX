---
name: simulador-pre-pagos-hipotecarios
description: Simula el impacto financiero de pre-pagos anticipados a un crédito hipotecario (capital reducido, plazo o pago mensual). Compara escenarios: pre-pago único vs aportes mensuales adicionales vs sin pre-pago. Calcula intereses ahorrados, plazo final, y break-even si el cliente además paga comisión por prepago (algunos bancos cobran 1-3%). Usar cuando el usuario diga prepago hipoteca, pagar anticipado credito vivienda, conviene prepagar, simular hipoteca.
allowed-tools: Read, Write
---

# Simulador pre-pagos hipotecarios

## Inputs

```json
{
  "saldo_actual_mxn": "1250000.00",
  "plazo_restante_meses": 240,
  "tasa_anual_nominal": 10.5,
  "pago_mensual_actual_mxn": "13500.00",
  "comision_prepago_pct": 0.02,
  "escenarios": [
    {"tipo": "prepago_unico", "monto_mxn": "100000"},
    {"tipo": "aporte_mensual_extra", "monto_mensual_mxn": "1500"},
    {"tipo": "sin_prepago"}
  ]
}
```

## Cálculo

Fórmula pago francés:
```
pago_mensual = capital × (tasa / (1 - (1 + tasa)^(-n)))
```

Donde `tasa = tasa_anual / 12` y `n = plazo_meses`.

Para pre-pago único: recalcular plazo o pago mensual sobre nuevo capital reducido.
Para aporte mensual extra: amortizar capital adicional cada mes.

## Output

```json
{
  "escenarios_comparados": [
    {
      "tipo": "sin_prepago",
      "intereses_totales_mxn": "2010000.00",
      "plazo_final_meses": 240,
      "fecha_final": "2046-06-12",
      "pago_mensual_final_mxn": "13500.00"
    },
    {
      "tipo": "prepago_unico_100k",
      "comision_prepago_mxn": "2000.00",
      "intereses_totales_mxn": "1500000.00",
      "ahorro_intereses_mxn": "510000.00",
      "plazo_final_meses": 180,
      "ahorro_meses": 60,
      "pago_mensual_final_mxn": "13500.00",
      "ROI_pct": 25.5,
      "recomendado": true
    },
    {
      "tipo": "aporte_mensual_1500",
      "intereses_totales_mxn": "1750000.00",
      "ahorro_intereses_mxn": "260000.00",
      "plazo_final_meses": 215,
      "ahorro_meses": 25
    }
  ],
  "mejor_escenario": "prepago_unico_100k",
  "comparativa_invertir": {
    "ROI_alternativo_cetes_anual": 9.5,
    "ROI_alternativo_renta_fija": 11.0,
    "vs_prepago_hipoteca": "Prepago tiene ROI 10.5% efectivo — mejor que CETES, comparable a renta fija"
  },
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Hipoteca a tasa variable | Recalcular con expectativa de tasa futura |
| Cliente con poco fondo de emergencia | NO prepagar — mantener liquidez |
| Hipoteca en UDIs | Usar valor UDI vigente + estimación inflación |
| Comisión prepago > 5% | Negociar con banco o no prepagar |

## ⚠ Compliance

- Tasas y comisiones reales del banco del usuario (varían)
- `vigencia_validada: false`
