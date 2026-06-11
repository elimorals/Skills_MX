---
name: whatsapp-business-mx
description: Diseña, redacta y valida templates de WhatsApp Business Platform aprobables por Meta, con tono apropiado para audiencia mexicana. Cubre clasificación de templates (utility, marketing, authentication), reglas de aprobación (variables permitidas, contenido prohibido, idioma), ventana de 24 horas, lifecycle de plantillas (submission, approved, rejected, paused), categorización por costo (Meta cobra distinto por tipo), y manejo de respuestas freeform vs template-only. Útil para cualquier flujo que use WhatsApp Business API vía Cloud API (Meta directa), Gupshup, Twilio, 360Dialog o Sirena. Usar cuando el usuario diga WhatsApp template, plantilla WhatsApp, mensaje masivo WhatsApp, notificación a clientes, recordatorio automatizado, WhatsApp Business API, send template, broadcast, o esté planeando comunicación automatizada a clientes mexicanos. NO usar para WhatsApp personal/grupos personales (eso es contra ToS) ni para SMS o llamadas.
allowed-tools: Read, Write, Edit
---

# WhatsApp Business para México

Templates aprobables por Meta + tono mexicano que efectivamente convierte. La diferencia entre un template "técnicamente correcto" y uno "que se aprueba y vende" está en este skill.

## Tipos de template (clasificación Meta)

Meta clasifica templates en 3 categorías que **cuestan diferente** y tienen reglas distintas:

### `UTILITY` — el más permisivo y barato
Mensajes transaccionales relacionados con una acción del usuario:
- Confirmaciones de cita
- Actualizaciones de envío/estado de orden
- Notificaciones de pago recibido
- Recordatorios de servicio agendado

Costo: ~$0.03-0.05 USD por conversación México (revisar tarifa vigente).

### `MARKETING` — el más caro y más restringido
Promociones, ofertas, newsletters, re-engagement:
- "20% de descuento solo este viernes"
- "Nueva colección disponible"
- "Te extrañamos, regresa con código X"

Costo: ~$0.06-0.09 USD por conversación México. Requiere opt-in explícito y demostrable.

### `AUTHENTICATION` — específico para OTP
Solo códigos de verificación de un solo uso. Plantilla pre-formateada por Meta, no editas la estructura. Costo muy bajo.

## Regla de oro: la ventana de 24 horas

Cuando un usuario te escribe primero (sesión iniciada por cliente), tienes **24 horas para responder con cualquier mensaje libre (freeform)**. Pasadas las 24 horas, solo puedes mandar templates pre-aprobados.

Esto rige todo el diseño del flujo:
- Si el cliente inicia conversación → responde rápido y resuelve dentro de 24h (cero costo de template).
- Si tú quieres iniciar → solo con template aprobado (sí cuesta).

## Reglas de aprobación de templates

Meta rechaza templates por:

1. **Contenido prohibido**: alcohol, tabaco, armas, sustancias controladas, productos para adultos, servicios financieros sin licencia, dating, criptomonedas sin regulación.
2. **Lenguaje engañoso o spam**: "gratis", "100% garantizado", emojis excesivos, mayúsculas sostenidas, signos de exclamación múltiples.
3. **Variables mal formateadas**: solo se permiten variables numeradas `{{1}}`, `{{2}}`, etc. No se permiten URLs dinámicas como variable (la URL debe ser fija o usar parámetro de URL específico).
4. **Falta de contexto**: un template tipo MARKETING que diga solo "Hola {{1}}" sin contexto se rechaza.
5. **Idioma mal declarado**: si declaras `es_MX` pero el contenido es portugués, rechazado.
6. **Categorización incorrecta**: si registras como UTILITY un mensaje obviamente promocional, Meta puede recategorizar (te cobra como MARKETING) o rechazar.

## Estructura técnica del template

```json
{
  "name": "confirmacion_cita_dental",
  "language": "es_MX",
  "category": "UTILITY",
  "components": [
    {
      "type": "HEADER",
      "format": "TEXT",
      "text": "Recordatorio de cita"
    },
    {
      "type": "BODY",
      "text": "Hola {{1}}, te recordamos tu cita en {{2}} para el {{3}} a las {{4}}. Responde *SI* para confirmar o *NO* para reagendar.",
      "example": {
        "body_text": [["Juan", "Clínica Dental Aurora", "viernes 15 de marzo", "10:30 AM"]]
      }
    },
    {
      "type": "FOOTER",
      "text": "Clínica Dental Aurora · Roma Norte, CDMX"
    }
  ]
}
```

Notas:
- `language: "es_MX"` (no `es` genérico — los códigos regionales mejoran aprobación).
- `example` es obligatorio: Meta lo usa para entender el contexto.
- HEADER puede ser TEXT, IMAGE, VIDEO, DOCUMENT.
- Botones (no mostrados) pueden ser QUICK_REPLY (hasta 3) o CTA (URL o llamada).

## Tono para audiencia mexicana

México neutro funciona para todo el país, pero hay matices regionales que pueden bajar conversión si los ignoras:

**Lo que funciona en México:**
- Tuteo amable (no "usted" salvo segmentos premium o clientes corporativos).
- Saludo cálido pero breve: "Hola Juan" o "Qué tal, Juan".
- Lenguaje claro, evitar tecnicismos legales/fiscales (incluso para CFDI, decir "tu factura" en mensajes al cliente final).
- Llamada a acción específica: "Responde 1 para confirmar" mejor que "Por favor confírmenos".

**Lo que NO funciona:**
- "¡¡¡Hola!!! 🎉🎉🎉" — spam visual, rechazo de Meta.
- Lenguaje español de España ("vale", "tío", "móvil"). Decir "celular" no "móvil".
- Anglicismos innecesarios ("schedule tu meeting"). Sí está bien el inglés de marca conocida ("checkout", "tracking").
- Frases de marketing tipo "¡Aprovecha YA!" — alto rechazo en MARKETING.

## Templates de referencia listos para usar

Este skill bundleará templates pre-aprobados para los casos más comunes:
- Confirmación de cita (UTILITY)
- Recordatorio de cita 24h antes (UTILITY)
- Confirmación de orden (UTILITY)
- Aviso de envío con tracking (UTILITY)
- Recordatorio de pago pendiente (UTILITY — pero cuidado, puede recategorizar a MARKETING si es muy promocional)
- Encuesta NPS post-servicio (MARKETING)
- Promoción de temporada (MARKETING)
- Re-engagement carrito abandonado (MARKETING)

*(Catálogo completo pendiente en `references/templates-aprobados.md`).*

## Lifecycle de un template

```
1. Drafting (este skill diseña)
2. Submission a Meta vía Business Manager o API
3. Review (1-2 horas en horario hábil, hasta 48h)
4. Approved → ya puedes enviarlo
   Rejected → razón en el response; ajustar y reenviar
5. Paused (si genera muchos opt-out o quejas, Meta lo pausa automáticamente)
6. Disabled (puede pasar si tu calidad de cuenta cae mucho)
```

## Calidad de cuenta (Quality Rating)

Meta evalúa tu cuenta WhatsApp Business por:
- **GREEN** (alta): mandas templates, los reciben, no bloquean, conversan.
- **YELLOW** (media): empiezan a bloquear/reportar. Tarifas pueden subir.
- **RED** (baja): mucha gente reporta spam. Meta puede limitar tu volumen diario.

Diseñar templates buenos protege la calidad de cuenta. Por eso este skill se preocupa por el tono, no solo por la estructura técnica.

## Salida esperada

Cuando el usuario pida un template:

1. **Template estructurado** en JSON listo para envío a Meta API.
2. **Variables documentadas**: qué representa cada `{{N}}`.
3. **Categorización propuesta** (UTILITY, MARKETING, AUTHENTICATION) con justificación.
4. **Bandera de riesgo de rechazo**: si hay contenido en zona gris, alertar al usuario antes de enviar a Meta.
5. **Versión preview** legible (no JSON) para que el usuario valide el tono antes de subir a Meta.

## Integración con otros skills

- Skills verticales (`colegios-mx`, `salon-mx`, etc.) construyen flows que usan este skill para sus templates específicos.
- Integra con `compliance-lfpdppp`: cualquier template MARKETING requiere demostrar opt-in del usuario (registro de consentimiento).
