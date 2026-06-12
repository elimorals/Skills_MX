---
name: workflow-cobranza-renta-mensual
description: Workflow orquestador de cobranza mensual para arrendador residencial. Ejecuta secuencialmente status de pagos del mes, determinación de nivel de escalamiento por inquilino, envío de comunicaciones por nivel, registro de respuestas, escalación de morosos > 30 días. Útil para correr una vez al mes (recomendado día 5 + recordatorio día 15). Usar cuando el usuario diga corre cobranza mensual, workflow cobranza, cobranza mes completo.
allowed-tools: Read, Write
---

# Workflow cobranza renta mensual

Orquestador end-to-end de la corrida de cobranza para todas las propiedades rentadas.

## Cuándo correr

- Día 5 del mes (después de día de pago típico)
- Día 15 del mes (segundo barrido)
- Día 25 del mes (alerta para morosos extremos)

## Fase 0 — Status inicial

Invocar `dashboard-propiedades` para obtener:
- Propiedades rentadas con día de pago
- Última fecha de pago confirmada por propiedad
- Historial de puntualidad por inquilino

## Fase 1 — Identificar morosos

Por cada propiedad rentada:
- `dias_desde_fecha_pago = today - fecha_pago_mes`
- Si `dias_desde_fecha_pago > 0`: agregar a lista de morosos

## Fase 2 — Cruce automático con bancos

Para reducir falsos positivos (inquilino pagó pero no avisó):
- Invocar `mp_bancos_mx.bancos_listar_movimientos(cuenta, dias=10)`
- Buscar depósitos con monto == renta_mensual ± 1% en últimos 10 días
- Marcar como pagado si match

## Fase 3 — Determinar nivel por inquilino

Por cada moroso:
- Invocar `cobranza-mensual-renta` con días + historial
- Obtener nivel recomendado (1-5)
- Obtener plantilla renderizada

## Fase 4 — Enviar comunicaciones (con confirmación)

Para nivel 1-3: enviar automático via `mp_meta_whatsapp.send_message`.
Para nivel 4 (formal email): preparar borrador, esperar OK del operador.
Para nivel 5 (notarial): SIEMPRE pasar al operador, jamás automático.

⚠ Si batch > 50 destinatarios: hook `confirmar-envio-masivo-wa.sh` se dispara.

## Fase 5 — Persistir

Registrar en tracker:
- Fecha + nivel + canal + status envío
- Próximo escalamiento sugerido si no responde

## Fase 6 — Reporte

```json
{
  "workflow": "cobranza_renta_mensual",
  "fecha_ejecucion": "2026-06-12",
  "total_propiedades_rentadas": 4,
  "morosos_detectados": 2,
  "pagos_confirmados_via_banco": 1,
  "comunicaciones_enviadas_automaticas": 1,
  "comunicaciones_pendientes_aprobacion_operador": 1,
  "morosos_nivel_5_protocolo_desalojo": 0,
  "siguiente_corrida_sugerida": "2026-06-19",
  "alertas": [
    "Cdmx Sur: D+15, nivel 4 — operador debe revisar email antes de enviar"
  ]
}
```

## Casos edge

| Caso | Comportamiento |
|---|---|
| Banco no responde / sin credenciales | Continuar sin cruce automático |
| Inquilino tipo "puntual histórico" mora 1 vez | Subir 1 nivel menos (más empático) |
| Inquilino tipo "reincidente" mora | Subir 1 nivel más |
| WhatsApp no entrega | Fallback a email |
| Comunicación fallida 3 veces | Sugerir visita en persona o llamada |

## Compliance

- Bitácora con cuenta_hash, NO cuenta en claro
- Plantillas no amenazan acciones legales sin base
- Nivel 5 (notarial) JAMÁS automático — siempre operador
- LFPDPPP: no compartir deuda con terceros
