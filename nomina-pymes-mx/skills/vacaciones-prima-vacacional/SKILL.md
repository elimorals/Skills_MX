---
name: vacaciones-prima-vacacional
description: Calcula vacaciones según la reforma "vacaciones dignas" a la LFT (DOF 27-12-2022, vigente 2023 - 12 días el primer año, +2 por año hasta 20 en el quinto, después +2 cada 5 años, sin tope legal) y prima vacacional mínima de 25% (Art. 80 LFT), con exención ISR de 15 UMA. Genera tabla por empleado de días disponibles, acumulados y por prescribir. Usar cuando el usuario diga vacaciones, días de vacaciones, prima vacacional, vacaciones dignas, días de descanso, reforma LFT vacaciones, cuántos días de vacaciones le tocan.
allowed-tools: Read, Write
---

# Vacaciones + prima vacacional

## Tabla Art. 76 LFT (reforma DOF 27-12-2022)

| Años cumplidos | Días |
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
| 31-35 | 32 |
| 36-40 | 34 (y así: +2 cada 5 años, sin tope) |

```python
def dias_vacaciones(anios: int) -> int:
    if anios < 1:
        return 0
    if anios <= 5:
        return 10 + 2 * anios
    return 20 + 2 * ((anios - 6) // 5 + 1)
```

## Prima vacacional

Mínimo **25% del salario** de los días de vacaciones (Art. 80 LFT). Se calcula sobre el salario diario, no el SBC.

**Exención ISR:** 15 UMA (Art. 93 fr. XIV LISR) = $1,759.65 en 2026.

## Reglas LFT

- Al menos **12 días continuos**; el resto se distribuye como el trabajador decida (Art. 78).
- Deben concederse dentro de los **6 meses** siguientes al cumplimiento del año (Art. 81).
- No pueden compensarse con dinero mientras exista la relación (Art. 79); solo se pagan al terminar la relación (finiquito).
- La acción para reclamarlas prescribe en **1 año** contado desde que son exigibles (Art. 516), es decir, al vencer esos 6 meses.
- Los años se cuentan desde la fecha de ingreso, no por año calendario.

## Ejemplo recalculado

Ingreso 2023-06-15; al 2026-06-15 cumple 3 años → 16 días en el periodo actual. Tiene 8 días pendientes del periodo anterior; salario diario $600:
prima pendiente = 600 × 8 × 25% = **$1,200.00**.

```json
{
  "empleado_id_hash": "...",
  "fecha_alta": "2023-06-15",
  "fecha_corte": "2026-06-15",
  "antiguedad_anos_completos": 3,
  "dias_vacaciones_periodo_actual": 16,
  "vacaciones_pendientes_periodo_anterior": 8,
  "salario_diario_mxn": "600.00",
  "prima_vacacional_pendiente_mxn": "1200.00",
  "fecha_limite_otorgar_pendientes": "2025-12-15",
  "alerta_obligacion_descanso": true,
  "vigencia_validada": true
}
```

Los 8 días del 2.º año (cumplido 2025-06-15) debían otorgarse antes del 2025-12-15: ya hay incumplimiento, por eso la alerta.

## ⚠ Inspección

La STPS puede pedir constancia de vacaciones (Art. 81: constancia anual de antigüedad y periodo). No otorgarlas se sanciona con multa (Art. 1002 LFT, 50 a 5,000 UMA, genérica). Valida con tu asesor laboral.
