---
name: recordatorios-renovacion
description: Envía recordatorios de renovación al cliente con cadencia 60-30-7 días antes del fin de vigencia usando WhatsApp Business (templates aprobados por Meta), email de respaldo y llamada en T-7 si el cliente no responde. Personaliza el mensaje según ramo (auto: riesgo de circular sin seguro de responsabilidad civil; GMM: se pierde la antigüedad y se reinician periodos de espera si no renueva; vida: la prima de un temporal renovable se recalcula por edad). Incluye comparativo de prima actual vs nueva (si subió, explicar por qué — siniestralidad, inflación médica, edad), opciones de fraccionar el pago y link de pago (Mercado Pago, Conekta o SPEI). Diferencia renovación automática vs manual. Genera la tasa de renovación del agente como KPI. Usar cuando el usuario diga "recordatorios renovación", "WhatsApp renovación seguros", "campaña renovación", "póliza por vencer cliente", "T-60 T-30 T-7 seguros". NO usar para venta nueva (usar comparador-polizas-cliente) ni para cobro de recibos de una póliza en curso.
allowed-tools: Read, Write, Edit
---

# Recordatorios de renovación

## Cadencia 60-30-7

| T- | Canal | Tono | Mensaje |
|---|---|---|---|
| 60 días | WA template | Cordial proactivo | "Hola {nombre}, tu póliza de {ramo} con {aseguradora} vence el {fecha}. Ya estoy preparando tu renovación. ¿Sigue igual el vehículo/contratante?" |
| 30 días | WA template + email | Con propuesta | "Hola {nombre}, te comparto la renovación de tu póliza. Prima nueva: ${monto}. Si quieres comparar con otras aseguradoras, dime." |
| 7 días | WA + llamada si no responde | Urgente | "Hola {nombre}, faltan 7 días para que venza tu cobertura. ¿Confirmas la renovación? Te paso el link de pago." |

## Personalización por ramo

### Auto
> "Si la póliza vence, circulas sin seguro: si causas un accidente pagas de tu bolsa los daños a terceros, y en carreteras federales y en varios estados el seguro de responsabilidad civil es obligatorio."

### GMM
> "Si dejas vencer la póliza pierdes la antigüedad: al contratar de nuevo, los padecimientos que ya tengas pueden quedar como preexistentes y vuelven a correr los periodos de espera."

### Vida
> "En un seguro temporal renovable la prima se recalcula con tu edad en cada renovación. Si te interesa una prima fija, revisemos un plan nivelado."

No prometas que renovar "congela" la tarifa: depende del plan.

## Cobro

- Links de pago: `mercadopago_create_preference` (MCP `mp_mercado_pago`) o `conekta_create_order` (MCP `mp_conekta`). Ambos requieren credenciales del agente; sin ellas, comparte la CLABE para SPEI.
- La prima se paga a la aseguradora o por los medios que ella autorice; el agente no debe recibir primas salvo que la aseguradora lo autorice por escrito.

## Tracker KPI

```
renovaciones_mes:
  total_a_renovar: 45
  renovadas: 38
  tasa_renovacion: 84.4%   # 38 / 45
  perdidas_por_precio: 4
  perdidas_por_competencia: 2
  perdidas_otras: 1
```

## Validación pendiente

Los templates de WhatsApp deben estar aprobados por Meta antes de uso masivo, y Meta cobra por mensaje entregado. Ver `whatsapp-business-mx`.
