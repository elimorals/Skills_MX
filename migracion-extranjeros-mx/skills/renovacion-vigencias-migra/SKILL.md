---
name: renovacion-vigencias-migra
description: Gestión proactiva de renovaciones de documentos migratorios (tarjeta de residente temporal, paso de temporal a permanente al cumplir 4 años, FMM de visitante). La solicitud de renovación se presenta dentro de los 30 días naturales previos al vencimiento; la skill alerta desde 90 días antes para reunir documentos y pagar derechos 2026 (LFD). Si se pasa la fecha, explica la regularización por documento vencido (60 días naturales, multa 20-100 UMA). Usar cuando el usuario diga vence mi residencia, renovar tarjeta, renovar visa, renovación migratoria, se me venció la residencia.
allowed-tools: Read, Write
---

# Renovación de vigencias migratorias

Fuentes: Reglamento de la Ley de Migración (ventana de 30 días naturales previos al vencimiento); Arts. 134 fr. I, 146 y 54 fr. V de la Ley de Migración; Art. 8o LFD 2026.

## Alertas escalonadas

| Días para vencer | Acción |
|---|---|
| > 90 | Tracker informativo |
| 90 | Reunir documentos (solvencia u oferta de empleo vigente, pasaporte con vigencia suficiente) |
| 45 | Tener listo el pago de derechos y la cita |
| 30 | 🟠 Abre la ventana: presentar la solicitud ya |
| 7 | 🔴 Crítico — presentar antes del vencimiento (si cae en inhábil, el siguiente hábil) |
| Vencida ≤ 60 días | ⛔ Regularización por documento vencido: derecho $1,847.13 + cuota de la condición + multa 20-100 UMA (Art. 146 LM) |
| Vencida > 60 días | ⛔ Irregular: ver `regularizacion-migratoria` y abogado |

Multa en UMA 2026 ($117.31 desde 01-02-2026): 20 UMA = $2,346.20; 100 UMA = $11,731.00. En enero de 2026 aplica UMA 2025 ($113.14): $2,262.80 a $11,314.00. La ley dice "salario mínimo general del DF"; desde la reforma constitucional de 2016 se entiende UMA.

## Renovaciones

- **Residente temporal**: misma cuota que la expedición (Art. 8o LFD): 1 año $11,140.74 · 2 años $16,693.36 · 3 años $21,142.58. El total acumulado no puede pasar de 4 años.
- **Temporal → permanente**: al cumplir 4 años como residente temporal (Art. 54 fr. V LM). Se tramita en lugar de la última renovación; cuota $13,578.96.
- **Descuento 50%** si acredita unidad familiar u oferta de empleo con CIE vigente (Art. 8o LFD); procedimiento operativo por confirmar con el INM.
- **FMM (visitante)**: no se renueva en México; al terminar los días autorizados debe salir.
- Cambios de domicilio, estado civil, nacionalidad o lugar de trabajo: avisar al INM dentro de 90 días (Art. 63 LM); si no, multa 20-100 UMA (Art. 158 LM).

## Output

```json
{
  "documento_id": "TARJETA-RESIDENTE-TEMPORAL",
  "fecha_emision": "2026-01-15",
  "fecha_vencimiento": "2027-01-14",
  "dias_para_vencer": 92,
  "ventana_renovacion_abre": "2026-12-15",
  "estado": "vigente",
  "puede_solicitar_permanente": false,
  "anios_continuos": 1,
  "derechos_renovacion_1_anio_mxn": "11140.74",
  "alerta_activa": false
}
```

Ejemplo con fecha de cálculo 2026-10-14: del 14-oct-2026 al 14-ene-2027 hay 92 días; la ventana abre 30 días antes del vencimiento (15-dic-2026).
