---
name: detector-anomalias-consumo
description: Detecta anomalías en consumo de servicios comparando contra histórico de 12 meses. Alerta sobre fugas de agua (consumo > 3x baseline en mismo período), sobrecargos eléctricos sin razón, errores facturación CFE, factor de potencia bajo. Usar cuando el usuario diga consumo raro, sobrecargo cfe, fuga agua, anomalia factura.
allowed-tools: Read, Write
---

# Detector anomalías consumo

## Patrones detectados

### Agua
- Consumo > 3x histórico mismo mes → probable fuga
- Consumo en horario nocturno (si medidor lo dice) → fuga
- Salto súbito > 50% sin razón conocida

### CFE
- Consumo > 1.5x histórico → revisar electrodomésticos
- Factor de potencia < 0.9 → penalización en factura
- Cobro de subsidio mal aplicado
- Tarifa cambiada sin aviso (DAC trigger)

### Gas
- Salto súbito → fuga

### Predial
- Reavalúo sin aviso → sobrecargo del año

## Output

```json
{
  "anomalias_detectadas": 2,
  "items": [
    {
      "servicio": "agua",
      "tipo": "fuga_probable",
      "consumo_actual_m3": 45,
      "baseline_mismo_mes_m3": 14,
      "incremento_pct": 220,
      "recomendacion": "Cerrar llaves, observar medidor 1h. Si avanza → llamar plomero."
    },
    {
      "servicio": "cfe",
      "tipo": "factor_potencia_bajo",
      "fp_actual": 0.82,
      "fp_umbral": 0.9,
      "penalizacion_mensual_estimada_mxn": "300",
      "recomendacion": "Instalar banco de capacitores"
    }
  ]
}
```
