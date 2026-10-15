---
name: agenda-citas-salon
description: Gestión de agenda para salones de belleza, estéticas, spas y barberías mexicanos. Crear, modificar, cancelar citas con estilista específico considerando duración real del servicio, buffer entre citas, recordatorios WhatsApp 24h y 2h antes, manejo de no-shows (segunda cita → depósito), walk-ins en huecos, optimización de hueco para maximizar ingresos. Usar cuando el usuario diga agendar cita, mover cita, cancelar cita, recordatorio cliente, no-show, walk-in, hueco agenda, disponibilidad estilista. NO usar para cobrar (eso es el comando /salon:cierre-dia-salon) ni comisiones (otro skill).
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

Costo: fuera de la ventana de 24 h de servicio, cada recordatorio es una plantilla UTILITY que Meta cobra por mensaje entregado (modelo vigente desde 01-07-2025); dentro de una ventana abierta por el cliente, las UTILITY no se cobran. Tres recordatorios por cita pueden ser caros: considera solo 24 h + 2 h. Si el recordatorio incluye promociones, Meta lo recategoriza como MARKETING (más caro y requiere opt-in). Ver `whatsapp-business-mx`.

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

1. **Trigger automático**: WhatsApp a clientes en lista de espera que pidieron ser avisados (servicios compatibles); si el mensaje lleva descuento es plantilla MARKETING
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

⚠ **LFPC**: depósitos, cargos por cancelación y el recargo de walk-in solo se pueden cobrar si se informaron **antes** de reservar (al agendar y en el mensaje de confirmación) y el cliente los aceptó; no se pueden hacer cargos sin consentimiento (Art. 10 LFPC). Los precios exhibidos deben ser totales, con IVA (Art. 7 BIS). Mantén las penas proporcionales y recíprocas: si el salón cancela o llega tarde, ofrece algo equivalente (reembolso del depósito + descuento).

Datos del cliente (nombre, teléfono, notas de alergias o tratamientos): tratarlos conforme a la LFPDPPP vigente (DOF 20-03-2025), con aviso de privacidad. Las notas de salud (alergias a tintes) son datos sensibles: pide consentimiento expreso. Ver `compliance-lfpdppp`.

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
