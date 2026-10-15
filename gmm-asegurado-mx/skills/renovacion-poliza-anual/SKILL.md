---
name: renovacion-poliza-anual
description: Gestión de renovación anual del GMM con alertas 90/60/30 días antes. Solicitar cotizaciones paralelas a 2-3 aseguradoras (negociación). Revisar ajuste de prima por edad, zona e inflación médica. Usar cuando el usuario diga renovar gmm, vencimiento poliza, renovacion seguro medico.
allowed-tools: Read, Write
---

# Renovación póliza GMM anual

## Calendario

| Días antes | Acción |
|---|---|
| 90 | Solicitar cotización a tu aseguradora + 2 competidores |
| 60 | Comparar ofertas + decidir renovar / cambiar |
| 30 | Firmar renovación o solicitar cambio |
| 0 | Vencimiento. Hay periodo de gracia para pagar la prima (30 días naturales salvo pacto distinto, Art. 40 Ley sobre el Contrato de Seguro); si vence sin pago, la póliza se cancela y pierdes antigüedad |

## Output

```json
{
  "poliza_actual": "GNP Premium",
  "fecha_vencimiento": "2027-01-03",
  "dias_para_vencer": 80,
  "prima_actual_anual_mxn": "32500",
  "ajuste_edad_proyectado_mxn": "+1800",
  "prima_renovacion_estimada_mxn": "34300",
  "cotizaciones_competencia": [...],
  "recomendacion": "Renovar GNP — diferencia <$2k vs alternativas + mantienes antigüedad"
}
```

## Notas

- En pólizas individuales, la prima de renovación sale de la tarifa registrada ante la CNSF (edad, zona, plan); pide que te expliquen cualquier aumento fuera de edad/inflación. Confianza media: verificar en condiciones generales y, si hay duda, con CONDUSEF.
- Ejemplo: 32,500 + 1,800 = 34,300.
