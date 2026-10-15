---
name: dashboard-academia-online
description: Dashboard mensual de una academia o escuela de cursos en línea: ingresos del mes (subtotal, IVA, total), alumnos activos por curso, altas y bajas, tasa de finalización, churn mensual, cartera vencida y CFDI pendientes. Calcula con fórmulas explícitas a partir del tracker local de inscripciones y pagos. Usar cuando el usuario diga dashboard academia online, cómo va mi academia, ingresos del mes cursos, churn alumnos, tasa de finalización, reporte mensual academia.
allowed-tools: Read, Write
---

# Dashboard de academia online

## Fuentes

- Tracker local de inscripciones (`inscripcion-alumno-curso`) y pagos (`cobranza-recurrente-cursos`).
- CFDI emitidos (`cfdi-mensualidad-curso`).
Si falta un dato, muéstralo como "sin dato", no lo estimes.

## Métricas y fórmulas

| Métrica | Fórmula |
|---|---|
| Ingresos del mes | Suma de pagos cobrados en el mes (separar subtotal e IVA) |
| Alumnos activos | Alumnos con inscripción vigente al último día del mes |
| Churn mensual | Bajas del mes ÷ activos al inicio del mes |
| Tasa de finalización | Alumnos que terminaron ÷ alumnos cuya fecha de fin cayó en el mes |
| Cartera vencida | Suma de mensualidades con más de 0 días de atraso |
| CFDI pendientes | Pagos cobrados sin CFDI emitido |

## Output esperado

```json
{
  "operation": "dashboard-academia-online",
  "data": {
    "mes": "2026-09",
    "ingresos": {"subtotal": "150000.00", "iva": "24000.00", "total": "174000.00"},
    "activos_inicio": 120,
    "altas": 18,
    "bajas": 9,
    "activos_fin": 129,
    "churn_pct": "7.5",
    "finalizacion_pct": "82.0",
    "cartera_vencida": "12180.00",
    "cfdi_pendientes": 4,
    "por_curso": [{"curso": "Inglés B1", "activos": 45}]
  },
  "vigencia_validada": true
}
```

Comprobación del ejemplo: 120 + 18 − 9 = 129 activos; churn 9 ÷ 120 = 7.5%; IVA 150,000 × 16% = 24,000.

Montos con `mxn-formato`. Si los cursos tienen RVOE (exentos), el IVA es 0.
