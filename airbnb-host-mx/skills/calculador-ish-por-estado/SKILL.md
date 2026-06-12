---
name: calculador-ish-por-estado
description: Calcula el ISH (Impuesto Sobre Hospedaje) por estado donde se ubica la propiedad Airbnb. La tasa varía 2-6% según entidad. Genera reporte mensual para declarar al fisco estatal. Distinto a fiscal-host-art113A que cubre el lado federal. Usar cuando el usuario diga ISH, impuesto hospedaje, hospedaje estatal.
allowed-tools: Read, Write
---

# Calculador ISH por estado

## Tasas vigentes (validar anual)

| Estado | Tasa ISH |
|---|---|
| CDMX | 3.5% |
| Quintana Roo | 5.0% |
| Yucatán | 3.0% |
| Jalisco | 3.0% |
| Baja California Sur | 3.0% |
| Edo. México | 4.0% |
| Sinaloa | 3.0% |
| Veracruz | 2.0% |

## Quién paga

- **Huésped** lo paga al hospedarse
- **Host** lo cobra y lo entera al fisco estatal mensualmente

## Output

```json
{
  "estado": "cdmx",
  "tasa_aplicable": 0.035,
  "ingresos_brutos_mes_mxn": "40700.00",
  "ish_a_pagar_mxn": "1425.00",
  "deadline_pago": "2026-07-20",
  "portal_pago": "https://www.finanzas.cdmx.gob.mx",
  "vigencia_validada": false
}
```
