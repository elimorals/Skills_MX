---
name: pricing-dinamico-airbnb
description: Pricing dinámico de tarifa por noche en Airbnb según demanda, competencia local, eventos en la ciudad, día de semana, anticipación de la reserva. Sugerencias para subir/bajar precios para maximizar ingreso × ocupación. Usar cuando el usuario diga precio noche, tarifa airbnb, optimizar precio, pricing dinamico.
allowed-tools: Read, Write
---

# Pricing dinámico Airbnb

## Factores

| Factor | Impacto típico |
|---|---|
| Día semana | Vie/Sáb +20-40% vs L-J |
| Fechas festivas | +30-100% |
| Eventos locales (concierto, congreso) | +50-200% |
| Anticipación reserva | Reserva muy próxima > más cara; muy lejana > más barata para asegurar |
| Competencia mismo barrio | -10% si listings similares más baratos |
| Tiempo vacante consecutivo | Bajar 10-20% por cada semana sin reservar |
| Rating del host | +5-15% si > 4.7 ★ |

## Output

```json
{
  "propiedad_id": "...",
  "tarifa_base_mxn": "1800",
  "calendario_30d_sugerido": [
    {"fecha": "2026-06-13", "dia_sem": "sab", "tarifa": "2300", "ajuste_pct": "+28%"},
    {"fecha": "2026-06-15", "dia_sem": "lun", "tarifa": "1700", "ajuste_pct": "-6%"}
  ],
  "alertas": [
    "Concierto en Foro Sol 2026-06-28 — subir tarifa fines de semana cercanos"
  ]
}
```
