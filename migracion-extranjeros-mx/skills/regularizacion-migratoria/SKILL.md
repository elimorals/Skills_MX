---
name: regularizacion-migratoria
description: Guía para extranjeros en situación migratoria irregular (FMM o tarjeta de residente vencida, actividades no autorizadas, entrada sin documentos). Explica los supuestos de regularización de la Ley de Migración (Arts. 133 y 134), multas en UMA (Arts. 145 y 146), derechos 2026 (LFD Art. 10: $1,847.13 más la cuota de la condición) y plazos (60 días naturales tras el vencimiento). NO sustituye asesoría legal especializada. Usar cuando el usuario diga sin papeles, irregular en México, FMM vencido, se me venció la tarjeta, regularizar situación migratoria, multa INM.
allowed-tools: Read, Write
---

# Regularización migratoria

Fuente primaria: Ley de Migración (última reforma DOF 15-01-2026) y Ley Federal de Derechos 2026.

## Supuestos

| Situación | Fundamento | Multa | Notas |
|---|---|---|---|
| Excedió la estancia autorizada (FMM o tarjeta vencida) y solicita dentro de los 60 días naturales siguientes | Art. 134 fr. I LM | 20-100 UMA (Art. 146) | "Regularización por documento vencido" |
| Realiza actividades distintas a las permitidas (p. ej. trabaja sin permiso) | Art. 134 fr. II LM | 20-100 UMA (Art. 146) | |
| Cónyuge o concubino(a) de mexicano o de residente | Art. 133 fr. I LM | 20-40 UMA (Art. 145) | Derecho a regularizar aunque haya pasado el plazo |
| Padre, madre, hijo, tutor o custodio de mexicano o de residente | Art. 133 fr. II LM | 20-40 UMA (Art. 145) | |
| Víctima o testigo de delito grave; vulnerabilidad que impida la deportación; NNA en restitución internacional | Art. 133 fr. III-V LM | Sin multa (Art. 145) | Tampoco paga el derecho del Art. 10 LFD |
| Entró sin documentación o por lugar no autorizado | Art. 144 fr. I LM (causal de deportación) | — | Solo regulariza si encaja en Art. 133; requiere abogado |

## Costos 2026

- UMA 2026 = $117.31 diaria (desde 01-02-2026; enero usa $113.14). La LM habla de "salario mínimo del DF": se entiende UMA desde 2016.
- 20 UMA = $2,346.20 · 40 UMA = $4,692.40 · 100 UMA = $11,731.00
- Derecho de regularización: $1,847.13 (Art. 10 LFD), más la cuota de la condición que se otorgue (p. ej. residente temporal 1 año $11,140.74, Art. 8o LFD).
- Ejemplo FMM vencido hace 45 días que regulariza como residente temporal por vínculo con mexicano (Art. 133 fr. I): multa entre $2,346.20 y $4,692.40 + $1,847.13 + $11,140.74 (o 50% de esta última si acredita unidad familiar: $5,570.37).

## Output

```json
{
  "situacion": "FMM_vencido_45_dias",
  "fundamento": "Art. 134 fr. I LM",
  "dentro_de_60_dias": true,
  "opciones": [
    "Salir del país antes de que te detengan (puede haber multa al salir)",
    "Regularizar en México por documento vencido (Art. 134) o por vínculo familiar (Art. 133)"
  ],
  "multa_rango_mxn": ["2346.20", "11731.00"],
  "derecho_regularizacion_mxn": "1847.13",
  "recomendacion": "Consultar abogado migratorio antes de acudir al INM",
  "vigencia_validada": true
}
```

## ⚠ Compliance

- Recomendar siempre abogado migratorio: acudir al INM en situación irregular puede terminar en un procedimiento administrativo.
- No sugerir acciones que empeoren la situación (salidas y reentradas para "reiniciar" días, documentos falsos).
- Algunos casos requieren amparo; eso lo decide el abogado.
