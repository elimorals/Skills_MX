---
name: recordatorios-renovacion
description: Envía recordatorios de renovación al cliente con cadencia 60-30-7 días antes del vencimiento usando WhatsApp Business (templates aprobables Meta), email respaldo, y llamada en T-7 si el cliente no responde a templates. Personaliza el mensaje según ramo (auto enfatiza periodo sin cobertura riesgo de multa o accidente; GMM enfatiza preexistencias que se reactivan al renovar; vida enfatiza beneficiarios + posible incremento de prima por edad). Incluye comparativo de prima actual vs nueva (si subió, explicar por qué — siniestralidad, inflación de costos médicos, edad), opciones de fraccionar pago, y link de pago directo (Mercado Pago / Conekta / SPEI). Diferencia entre renovación automática (algunos ramos lo hacen sin intervención) y renovación manual. Genera tracker de tasa de renovación del agente como KPI. Usar cuando el usuario diga "recordatorios renovación", "WhatsApp renovación seguros", "campaña renovación", "póliza por vencer cliente", "T-60 T-30 T-7 seguros". NO usar para venta nueva (usar comparador-polizas-cliente) ni para cobro de prima en curso.
allowed-tools: Read, Write, Edit
---

# Recordatorios de renovación

## Cadencia 60-30-7

| T- | Canal | Tono | Mensaje |
|---|---|---|---|
| 60 días | WA template | Cordial proactivo | "Hola {nombre}, tu póliza {ramo} con {aseguradora} vence el {fecha}. Ya estoy preparando tu renovación. ¿Sigues con el mismo auto/vehículo/contratante?" |
| 30 días | WA template + email | Con propuesta | "Hola {nombre}, te comparto la renovación de tu póliza. Prima nueva: ${monto}. Si quieres comparar con otras aseguradoras, dime." |
| 7 días | WA + llamada si no responde | Urgente | "Hola {nombre}, faltan 7 días para que venza tu cobertura. ¿Confirmas la renovación? Te paso link de pago." |

## Personalización por ramo

### Auto
> "Quedar sin cobertura, aunque sea 1 día, te expone a multa por seguro obligatorio + responsabilidad civil ilimitada si chocas."

### GMM
> "Si la póliza vence, las condiciones preexistentes se reinician al re-contratar (12 meses sin cobertura típicamente)."

### Vida
> "Tu edad subió este año, la prima sube proporcionalmente. Renovar ahora congela tarifa de hoy."

## Tracker KPI

```
renovaciones_mes:
  total_a_renovar: 45
  renovadas: 38
  tasa_renovacion: 84.4%
  perdidas_por_precio: 4
  perdidas_por_competencia: 2
  perdidas_otras: 1
```

## Validación pendiente

⚠ Templates WhatsApp deben pasar aprobación Meta antes de uso masivo. Ver brief whatsapp-business-mx.
