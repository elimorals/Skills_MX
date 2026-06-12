---
name: detector-captura-duplicada-cfdis
description: Detecta CFDIs duplicados o casi-duplicados en el portal SAT/contabilidad (mismo proveedor + mismo monto + fechas cercanas) que pueden estar siendo deducidos 2 veces por error de captura. Evita riesgo de auditoría SAT por duplicar deducciones. Usar cuando el usuario diga cfdis duplicados, captura duplicada, revision contabilidad.
allowed-tools: Read, Write
---

# Detector CFDIs duplicados

## Patrón duplicado típico

- Mismo emisor RFC
- Mismo monto exacto (o ±$1 redondeo)
- Fecha emisión diferente máximo 15 días
- Conceptos similares

## Riesgo

Si SAT detecta duplicado en auditoría:
- Reversión deducción duplicada
- Recargos + actualización
- Posible multa 55-75% del monto duplicado

## Output

```json
{
  "ejercicio_revisado": 2025,
  "duplicados_potenciales": [
    {
      "uuid_1": "abc-001",
      "uuid_2": "abc-002",
      "emisor_rfc_hash": "...",
      "monto_mxn": "5800.00",
      "fechas": ["2025-03-15", "2025-03-17"],
      "score_duplicado": 0.95,
      "recomendacion": "Revisar — probable duplicado por captura"
    }
  ],
  "total_potencial_duplicado_mxn": "5800.00",
  "ahorro_si_se_corrige_isr": "1740.00"
}
```
