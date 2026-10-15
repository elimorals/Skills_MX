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
  "pago_mensual_actual_mxn": "12479.75",
  "comision_prepago_pct": 0.02,
  "tasa_alternativa_inversion_pct": null,
  "escenarios": [
    {"tipo": "prepago_unico", "monto_mxn": "100000"},
    {"tipo": "aporte_mensual_extra", "monto_mensual_mxn": "1500"},
    {"tipo": "sin_prepago"}
  ]
}
```

`comision_prepago_pct` sale del contrato (muchos créditos no cobran); `tasa_alternativa_inversion_pct` la da el usuario (p. ej. rendimiento actual de CETES que consulte), no se asume.

## Cálculo

Fórmula pago francés:
```
pago_mensual = capital × (tasa / (1 - (1 + tasa)^(-n)))
```

Donde `tasa = tasa_anual / 12` y `n = plazo_meses`. $1,250,000 a 10.5% y 240 meses → **$12,479.75**.

- Pre-pago único: se resta del capital y se mantiene el pago (reduce plazo).
- Aporte mensual extra: se suma al pago de cada mes como abono a capital.
- Simula mes a mes hasta saldo cero (ver `simulador-prepagos-hipotecarios`).

## Output (recalculado)

```json
{
  "escenarios_comparados": [
    {
      "tipo": "sin_prepago",
      "intereses_totales_mxn": "1745139.66",
      "plazo_final_meses": 240,
      "pago_mensual_mxn": "12479.75"
    },
    {
      "tipo": "prepago_unico_100k",
      "comision_prepago_mxn": "2000.00",
      "intereses_totales_mxn": "1201409.38",
      "ahorro_intereses_mxn": "543730.28",
      "ahorro_neto_de_comision_mxn": "541730.28",
      "plazo_final_meses": 189,
      "ahorro_meses": 51
    },
    {
      "tipo": "aporte_mensual_1500",
      "total_aportado_extra_mxn": "264000.00",
      "intereses_totales_mxn": "1197137.98",
      "ahorro_intereses_mxn": "548001.68",
      "plazo_final_meses": 176,
      "ahorro_meses": 64
    }
  ],
  "lectura": "El aporte mensual ahorra un poco más de intereses pero exige $264,000 a lo largo de 176 meses; el prepago único ahorra casi lo mismo con $100,000 hoy. Elegir según liquidez.",
  "comparativa_invertir": "Pre-pagar rinde la tasa del crédito (10.5% nominal). Compárala con la tasa alternativa que dé el usuario, después de impuestos.",
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
