---
name: cobranza-recurrente-cursos
description: Cobranza recurrente mensual de cursos y academias con escalado empático (el alumno es una relación continua). Recordatorio previo al cargo, aviso de cargo fallido, reintentos, pausa del acceso y baja, usando suscripciones o links de pago (Conekta, Mercado Pago) y WhatsApp con templates aprobados. Respeta la información previa de precios y cargos (LFPC) y no condiciona documentos del alumno al pago. Usar cuando el usuario diga cobranza recurrente cursos, cobrar mensualidades academia, alumno no pagó, cargo rechazado, domiciliación curso, suscripción curso en línea.
allowed-tools: Read, Write
---

# Cobranza recurrente de cursos

## Escalado

| Momento | Canal | Mensaje |
|---|---|---|
| T-3 días del cargo | WhatsApp (UTILITY) o email | "Hola {nombre}, el {fecha} se hará el cargo de tu mensualidad de {curso} por ${monto}." |
| Día del cargo fallido | WhatsApp + email | "No pudimos cobrar tu mensualidad. Puedes actualizar tu tarjeta o pagar aquí: {link}." |
| D+3 | WhatsApp | Recordatorio cordial con link de pago |
| D+7 | WhatsApp + llamada | Ofrecer cambiar fecha de cargo o pausar el curso |
| D+15 | Email formal | Aviso de pausa del acceso a clases nuevas en la fecha que diga el contrato |
| D+30 | Email | Baja del curso; el saldo vencido se gestiona aparte, sin exponer al alumno |

## Herramientas

- Suscripciones: `conekta_subscription_create`, `conekta_subscription_update`, `conekta_subscription_cancel` (MCP `mp_conekta`).
- Links de pago: `conekta_create_payment_link` o `mercadopago_create_preference` (MCP `mp_mercado_pago`).
- Los MCP requieren credenciales; sin ellas, trabaja en modo mock y entrega al usuario los mensajes y montos para que cobre manualmente.
- Templates de WhatsApp: deben estar aprobados por Meta; Meta cobra por mensaje entregado. Ver `whatsapp-business-mx`.

## Reglas

- Recargos, penalizaciones y política de cancelación solo si se informaron antes de contratar (Ley Federal de Protección al Consumidor). No inventes recargos.
- Si el alumno es menor de edad, la cobranza va al padre o tutor, nunca al alumno.
- No publiques listas de morosos ni comentes adeudos en grupos (LFPDPPP; ver `compliance-lfpdppp`).
- No retengas constancias de cursos ya terminados y pagados.
- Emite el CFDI al cobrar (`cfdi-mensualidad-curso`).

## Output esperado

```json
{
  "operation": "cobranza-recurrente-cursos",
  "data": {
    "alumno_hash": "…",
    "curso": "Inglés B1 sabatino",
    "monto": "1740.00",
    "dias_vencido": 7,
    "etapa": "D+7",
    "accion": "WhatsApp + llamada: ofrecer cambio de fecha o pausa",
    "link_pago": null
  },
  "vigencia_validada": true
}
```
