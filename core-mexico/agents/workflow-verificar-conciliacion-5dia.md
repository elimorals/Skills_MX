---
name: workflow-verificar-conciliacion-5dia
description: Verificación rápida (NO conciliación completa) que se ejecuta cada día 5 del mes para detectar pagos recurrentes que aún no se han recibido y disparar la primera ronda de cobranza (nivel 2 — amable post-vencimiento). Más simple que workflow-conciliacion-bancaria-mensual: solo cruza pagos esperados vs recibidos del mes en curso. Usar cuando el usuario diga verifica pagos del 5, revisión de día 5, quien no ha pagado este mes. NO sirve para conciliación fiscal mensual.
allowed-tools: Read, Write, Bash
---

# Workflow: Verificar conciliación día 5

Verificación ligera (5 minutos típica) del estado de cobros del mes en curso.

## Trigger

- Cron mensual día 5 09:00 (`scripts/verificar-cobros.sh`)
- Manual: "¿quién no ha pagado este mes?"

## Inputs

- `cobranza-pendiente.jsonl` (output de `cobranza-recurrente.sh`)
- `pagos-recibidos.jsonl` (alimentado por handlers webhook)
- `mp_bancos_mx` (cruce automático, opcional)

## Fases

### Fase 1 — Lista de pagos esperados

Cargar `cobranza-pendiente.jsonl`. Es el output del cron del día 1.

### Fase 2 — Cruce con pagos recibidos

Por cada cliente esperado:
- Buscar match en `pagos-recibidos.jsonl` (cliente_hash + monto + fecha en ventana ±2 días)
- Cruce opcional con extractos bancos via `mp_bancos_mx`
- Marcar como `pagado` o `pendiente_d5`

### Fase 3 — Disparar comunicación nivel 2

Por cada pendiente:
- Generar plantilla nivel 2 ("amable post-vencimiento") via `cobranza-multinivel` (freelancers-mx) o `cobranza-mensual-renta` (arrendador-residencial-mx)
- Encolar en `wa-outbox-borrador.jsonl` para confirmación operador

### Fase 4 — Reporte

```json
{
  "workflow": "verificar_conciliacion_5dia",
  "mes": "2026-06",
  "dia_corte": 5,
  "total_esperados": 24,
  "pagados_a_tiempo": 18,
  "pendientes_d5": 6,
  "porcentaje_recaudacion": 75.0,
  "comunicaciones_nivel_2_encoladas": 6,
  "siguiente_corrida": "2026-06-12 (D+7 si siguen pendientes)"
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Cliente pagó parcial | Marcar como `pendiente_d5` por la diferencia |
| Cliente pidió extensión escrita | Excluir de comunicación auto |
| Cliente nuevo del mes (sin historial) | Tono extra empático en comunicación |

## Dependencias

- `cobranza-recurrente.sh` (cron día 1)
- `mp_bancos_mx` (opcional)
- Webhook handlers de pago (Stripe, MP, Conekta) alimentan `pagos-recibidos.jsonl`
