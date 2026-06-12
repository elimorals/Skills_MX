---
name: reservas-y-ocupacion
description: Tracking de reservas confirmadas, canceladas, y calendario de ocupación de la propiedad. Calcula tasa de ocupación mensual / trimestral / anual, identifica gaps (días sin reserva), y sugiere acciones (bajar tarifa, ofrecer descuento estancia larga). Útil para optimizar pricing dinámico. Usar cuando el usuario diga calendario airbnb, ocupación, gaps reservas, tarifa por noche.
allowed-tools: Read, Write
---

# Reservas y ocupación

## Output

```json
{
  "propiedad_id": "...",
  "periodo": "2026-06",
  "noches_disponibles": 30,
  "noches_reservadas": 22,
  "tasa_ocupacion_pct": 73.3,
  "ingreso_bruto_mxn": "40700.00",
  "tarifa_promedio_noche_mxn": "1850.00",
  "tarifa_min_noche_mxn": "1200.00",
  "tarifa_max_noche_mxn": "2800.00",
  "reservas": [
    {"check_in": "2026-06-03", "check_out": "2026-06-06", "noches": 3, "monto_mxn": "5550.00", "estado": "completada"},
    {"check_in": "2026-06-10", "check_out": "2026-06-14", "noches": 4, "monto_mxn": "7400.00", "estado": "completada"}
  ],
  "gaps_sin_reserva": [
    {"desde": "2026-06-07", "hasta": "2026-06-09", "noches": 3, "sugerencia": "Reducir tarifa 15% para llenar gap"}
  ],
  "comparativa": {
    "mes_anterior_ocupacion_pct": 65.0,
    "mismo_mes_anio_anterior_pct": 80.0,
    "promedio_zona_estimado_pct": 70.0
  }
}
```

## Estrategias para optimizar ocupación

1. **Pricing dinámico**: bajar tarifa en gaps de < 4 noches
2. **Descuentos por estancia larga** (>7 días)
3. **Photos profesionales** (incrementa CTR 20-30%)
4. **Respuesta rápida** (Airbnb premia hosts < 1h respuesta)
5. **Política flexible cancelación** (atrae más reservas pero más cancelaciones)
