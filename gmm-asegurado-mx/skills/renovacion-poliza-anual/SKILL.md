---
name: renovacion-poliza-anual
description: Gestión de renovación anual del GMM con alertas 90/60/30 días antes. Solicitar cotizaciones paralelas a 2-3 aseguradoras (negociación). Atender ajuste de prima por edad + ajustes por uso del año. Usar cuando el usuario diga renovar gmm, vencimiento poliza, renovacion seguro medico.
allowed-tools: Read, Write
---

# Renovación póliza GMM anual

## Calendario

| Días antes | Acción |
|---|---|
| 90 | Solicitar cotización a tu aseguradora + 2 competidores |
| 60 | Comparar ofertas + decidir renovar / cambiar |
| 30 | Firmar renovación o solicitar cambio |
| 0 | Vencimiento — si no renovaste, pierdes antigüedad |

## Output

```json
{
  "poliza_actual": "GNP Premium",
  "fecha_vencimiento": "2026-08-31",
  "dias_para_vencer": 80,
  "prima_actual_anual_mxn": "32500",
  "ajuste_edad_proyectado_mxn": "+1800",
  "ajuste_por_uso_2025_mxn": "+0",
  "prima_renovacion_estimada_mxn": "34300",
  "cotizaciones_competencia": [...],
  "recomendacion": "Renovar GNP — diferencia <$2k vs alternativas + mantienes antigüedad"
}
```
