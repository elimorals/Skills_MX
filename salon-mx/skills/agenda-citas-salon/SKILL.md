---
name: agenda-citas-salon
description: Gestión de agenda para salones de belleza, estéticas, spas y barberías mexicanos. Crear, modificar, cancelar citas con estilista específico considerando duración real del servicio, buffer entre citas, recordatorios WhatsApp 24h y 2h antes, manejo de no-shows (segunda cita → depósito), walk-ins en huecos, optimización de hueco para maximizar ingresos. Usar cuando el usuario diga agendar cita, mover cita, cancelar cita, recordatorio cliente, no-show, walk-in, hueco agenda, dispnibilidad estilista. NO usar para cobrar (eso es cierre-dia) ni comisiones (otro skill).
allowed-tools: Read, Write, Edit
---

# Agenda de citas — salones MX

La agenda es el activo central de un salón. Mal manejada = no-shows + huecos + pérdida.

## Datos clave por cita

```json
{
  "id_cita": "C-2026-0042",
  "cliente": {"nombre": "...", "tel_wa": "+52555...", "rfc": "opcional"},
  "estilista": "Ana",
  "servicio": "Corte + tinte",
  "duracion_minutos": 120,
  "hora_inicio": "2026-03-15T14:00:00",
  "precio_estimado_mxn": 1500.00,
  "status": "confirmada | tentativa | cancelada | no_show | completada",
  "depósito_pagado_mxn": 500.00,
  "notas": "Cliente quiere tono cobrizo"
}
```

## Recordatorios WhatsApp

Schedule automático:

| Tiempo antes | Template | Acción si cliente no responde |
|---|---|---|
| 24 horas | `recordatorio_24h` | Marcar `tentativa` si no confirma en 4h |
| 2 horas | `recordatorio_2h` con link mapas | Recordar status `tentativa` |
| 30 min | `llegando_pronto` | Si no responde, mantener slot 15 min, luego liberar |

## Política anti no-show

| Histórico cliente | Política |
|---|---|
| 1ra cita o sin no-shows | Sin depósito |
| 1 no-show histórico | Depósito 30% del servicio |
| 2+ no-shows | Depósito 100% (cancelable hasta 24h antes) |
| 3+ no-shows | Solo walk-ins (sin reserva anticipada) |

Cliente confirma con click en link WhatsApp para evitar fricciones.

## Walk-ins (sin reserva)

Cuando llega un cliente sin cita:
1. Buscar hueco en agenda del día (look-ahead 4 horas)
2. Verificar estilista compatible disponible
3. Ofrecer 3 alternativas: hoy mismo / mañana / agendar fecha futura
4. Si toma walk-in: cobrar 20% upcharge (premium por urgencia, opcional según política)

## Optimización de hueco

Cuando un hueco aparece (cancelación, no-show):

1. **Trigger automático**: WhatsApp blast a clientes en lista de espera (servicios compatibles)
2. **Si nadie toma en 30 min**: descuento 15% para llenar el hueco
3. **Si nadie toma en 1 hora**: marcar estilista disponible para walk-in
4. **Documentar el hueco**: causa (no-show / cancelación / cliente movió) — para análisis

## Manejo de cancelaciones por cliente

| Tiempo antes | Política |
|---|---|
| > 48h | Sin cargo, depósito reembolsable |
| 24-48h | Depósito retenido (puede usarse en próxima cita 30 días) |
| < 24h | Cargo 50% del servicio (excepto emergencia documentada) |
| < 2h | Cargo 100% (cuenta como no-show) |

## Buffer entre citas

Por estilista, agregar buffer:
- Servicios > 60 min: 15 min buffer
- Servicios < 60 min: 10 min buffer
- Spa (masaje, facial): 20 min buffer (limpieza camilla)
- Barbería (corte rápido): 5 min buffer

El sistema NO permite agendar si choca el buffer.

## Output estructurado

```json
{
  "cita_creada": {
    "id": "C-2026-0042",
    "status": "confirmada",
    "deposito_solicitado": false,
    "recordatorios_agendados": ["24h", "2h", "30min"]
  },
  "agenda_dia": {
    "fecha": "2026-03-15",
    "estilista": "Ana",
    "citas_count": 6,
    "huecos_disponibles_minutos": [60, 30],
    "tasa_ocupacion": 0.75
  }
}
```

## Validación pendiente

- Tasa típica de no-shows en salones MX (3-15% rango usual)
- Políticas de depósito por tipo de salón (barbería vs spa premium)
- Templates WhatsApp aprobados Meta para el sector

## Ver también

- `servicios-tarifario` para duración por servicio
- `comisiones-estilistas` para incentivos por cita completada
- `whatsapp-business-mx` para templates
