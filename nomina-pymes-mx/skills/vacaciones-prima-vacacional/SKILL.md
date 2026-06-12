---
name: vacaciones-prima-vacacional
description: Cálculo de vacaciones según reforma LFT 2023 (12 días año 1, +2 días por año hasta 20 días en año 5, +2 cada 5 años, máximo 32 días) y prima vacacional 25% del sueldo de esos días. Genera tabla por empleado de vacaciones disponibles + acumuladas + vencidas. Usar cuando el usuario diga vacaciones, prima vacacional, dias descanso, reforma LFT 2023.
allowed-tools: Read, Write
---

# Vacaciones + Prima vacacional (reforma 2023)

## Tabla días vacaciones (Art. 76 LFT — reforma diciembre 2022)

| Años antigüedad | Días vacaciones |
|---|---|
| 1 | 12 |
| 2 | 14 |
| 3 | 16 |
| 4 | 18 |
| 5 | 20 |
| 6-10 | 22 |
| 11-15 | 24 |
| 16-20 | 26 |
| 21-25 | 28 |
| 26-30 | 30 |
| 31+ | 32 |

## Prima vacacional

25% del sueldo correspondiente a los días de vacaciones (Art. 80 LFT).

```python
def calcular_prima_vacacional(sueldo_diario: Decimal, dias_vacaciones: int) -> Decimal:
    return sueldo_diario * dias_vacaciones * Decimal("0.25")
```

## Exención fiscal

15 UMAs exentas del ISR para prima vacacional (Art. 93 fr. XIV LISR).

## Reglas LFT

- Disfrutarse en periodo continuo
- No es legal "comprar" vacaciones (empleado debe descansar)
- Pueden disfrutarse en periodos distintos si convenio firmado
- Prescriben al año de generadas si no se disfrutan

## Output

```json
{
  "empleado_id_hash": "...",
  "fecha_alta": "2023-06-15",
  "antiguedad_anos_completos": 2,
  "dias_vacaciones_aplicables_año_curso": 14,
  "vacaciones_acumuladas_no_disfrutadas": 8,
  "vacaciones_vencidas_prescritas": 0,
  "sueldo_diario_mxn": "627.12",
  "prima_vacacional_pendiente_mxn": "1097.46",
  "vacaciones_proximas_vencer_dias": 60,
  "alerta_obligacion_descanso": false,
  "vigencia_validada": false
}
```

## ⚠ Inspección STPS

STPS audita aleatoriamente. Empleado sin vacaciones registradas = multa al patrón.
