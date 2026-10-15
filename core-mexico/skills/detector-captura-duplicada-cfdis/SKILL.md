---
name: detector-captura-duplicada-cfdis
description: Detecta CFDI recibidos duplicados o casi duplicados en la contabilidad (mismo emisor, mismo monto, fechas cercanas, conceptos similares, o un CFDI cancelado/sustituido que se siguió deduciendo) que podrían estar deducidos o acreditados dos veces por error de captura, y estima el ISR e IVA en riesgo. Usar cuando el usuario diga CFDIs duplicados, factura duplicada, captura duplicada, deducción doble, revisión de contabilidad, depurar XML.
allowed-tools: Read, Write
---

# Detector de CFDI duplicados

## Patrones

- **Mismo UUID** registrado dos veces en contabilidad (error puro de captura).
- **UUID distinto, misma operación**: mismo RFC emisor, mismo total (±$1), fechas a ≤ 15 días, conceptos similares — típico de refacturación.
- **CFDI cancelado o sustituido** (motivo 01 con UUID relacionado) que sigue en la contabilidad: verifica estatus con `sat_verificar_cfdi_uuid` (MCP `mp_sat_portal`).

## Riesgo

Si el SAT lo detecta:
- Rechazo de la deducción y del IVA acreditable duplicados.
- Actualización y recargos.
- Multa por omisión de contribuciones: **55% a 75% del impuesto omitido** (Art. 76 CFF), no del monto del CFDI. Si se corrige de forma espontánea, antes de que el SAT lo requiera, no hay multa (Art. 73 CFF), solo actualización y recargos.

## Output

```json
{
  "ejercicio_revisado": 2025,
  "duplicados_potenciales": [
    {
      "uuid_1": "abc-001",
      "uuid_2": "abc-002",
      "emisor_rfc_hash": "...",
      "subtotal_mxn": "5000.00",
      "iva_mxn": "800.00",
      "total_mxn": "5800.00",
      "fechas": ["2025-03-15", "2025-03-17"],
      "estatus_sat": ["vigente", "vigente"],
      "score_duplicado": 0.95,
      "recomendacion": "Revisar — probable duplicado por captura"
    }
  ],
  "deduccion_duplicada_mxn": "5000.00",
  "isr_en_riesgo_pm_30pct_mxn": "1500.00",
  "iva_acreditable_en_riesgo_mxn": "800.00"
}
```

ISR en riesgo sobre el subtotal (5,000 × 30% para PM); el IVA acreditado de más es 800. Para PF, usa su tasa marginal.

## Siguiente paso

Corrige con declaración complementaria (pagos provisionales y anual si ya se presentó) antes de que el SAT inicie facultades. Valida con el contador.
