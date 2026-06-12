---
name: optimizador-rutas-conductores
description: Sugiere zonas y horarios óptimos para que conductor de plataforma maximice ingreso por hora. Considera demanda histórica por zona/hora, surge pricing predictions, eventos especiales (concertos, partidos), y tipo de servicio (UberX vs Uber Premium vs DiDi Vip). Usar cuando el usuario diga donde conducir, mejor zona, horas pico, optimizar viajes.
allowed-tools: Read, Write
---

# Optimizador rutas conductor

## Factores

| Factor | Impacto |
|---|---|
| Hora del día | Punta 6-9am + 6-10pm = +30-50% tarifa |
| Día semana | Vie/Sáb noche +40-80% |
| Eventos locales | +100-300% surge pricing |
| Zona | CDMX Polanco/Roma > zonas periféricas |
| Aeropuerto | Pickups frecuentes pero esperas largas |
| Lluvia | Demanda +50% |

## Output

```
🚗 SUGERENCIAS HOY (Vie 12 Jun)

⏰ AHORA (10:00am):
  Zona sugerida: Polanco / Reforma
  Demanda: ⭐⭐⭐ moderada
  Tarifa promedio: $85 viaje

🎯 PRÓXIMO PICO (6-9pm):
  Zona sugerida: Roma + Condesa (eventos)
  Demanda: ⭐⭐⭐⭐⭐ alta
  Tarifa promedio esperada: $140 viaje
  Razón: Fin de semana + concierto Foro Sol

⛔ EVITAR:
  Periférico zonas sin demanda baja (Tlalpan, Cuajimalpa interior)
  Aeropuerto antes de 12pm (esperas > 1h)
```

## Dependencias

- Datos históricos del propio conductor (mejor)
- Calendario eventos locales (manual o scrape)
