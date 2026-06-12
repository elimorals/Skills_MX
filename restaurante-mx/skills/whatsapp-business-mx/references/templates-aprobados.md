# Templates WhatsApp Business pre-aprobables — biblioteca MX

Biblioteca de templates redactados con tono mexicano neutro, listos para enviar a Meta Business Manager para aprobación. Cada uno indica categoría, variables, y notas sobre tasa de aprobación esperada.

## Convención de naming

`<categoria>_<intencion>_<vertical>_mx` (ej. `utility_confirmacion_cita_dental_mx`)

Nombre técnico de plantilla SIEMPRE en kebab-case sin tildes ni espacios. El display puede ser otro.

## Categoría UTILITY

### Confirmación de cita

```json
{
  "name": "utility_confirmacion_cita_general_mx",
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
      "text": "Hola {{1}}, te recordamos tu cita en {{2}} para el {{3}} a las {{4}}.\n\nResponde *SI* para confirmar o *NO* si necesitas reagendar.",
      "example": {
        "body_text": [["Juan", "Clínica Dental Aurora", "viernes 15 de marzo", "10:30 AM"]]
      }
    },
    {
      "type": "FOOTER",
      "text": "{{5}}"
    }
  ]
}
```

Variables: `{{1}}` nombre cliente · `{{2}}` nombre negocio · `{{3}}` fecha · `{{4}}` hora · `{{5}}` dirección/footer corto.

Aprobación esperada: **alta** (UTILITY transaccional limpio).

### Recordatorio 24h antes (mismo template, distinto trigger)

Usar `utility_recordatorio_24h_general_mx` con el mismo formato pero copy ajustado: "Te recordamos que mañana tienes tu cita..."

### Confirmación de orden e-commerce

```json
{
  "name": "utility_orden_confirmada_ecom_mx",
  "language": "es_MX",
  "category": "UTILITY",
  "components": [
    {
      "type": "BODY",
      "text": "¡Hola {{1}}! Recibimos tu orden *#{{2}}* por ${{3}} MXN.\n\nTu pedido será enviado en {{4}}. Te avisaremos cuando salga con tu número de guía.\n\nGracias por tu compra 🛍️",
      "example": {
        "body_text": [["María", "1024", "899", "1-2 días hábiles"]]
      }
    }
  ]
}
```

Variables: `{{1}}` nombre · `{{2}}` # orden · `{{3}}` monto · `{{4}}` plazo envío.

Aprobación esperada: **alta**.

### Aviso de envío con guía

```json
{
  "name": "utility_envio_en_camino_ecom_mx",
  "language": "es_MX",
  "category": "UTILITY",
  "components": [
    {
      "type": "BODY",
      "text": "Hola {{1}}, tu orden *#{{2}}* ya está en camino con {{3}}.\n\nNúmero de guía: *{{4}}*\nRastrea aquí: {{5}}\n\nEntrega estimada: {{6}}.",
      "example": {
        "body_text": [["María", "1024", "Estafeta", "12345678", "https://rastreo.estafeta.com/12345678", "miércoles 20"]]
      }
    }
  ]
}
```

### CFDI listo para descarga

```json
{
  "name": "utility_cfdi_disponible_mx",
  "language": "es_MX",
  "category": "UTILITY",
  "components": [
    {
      "type": "BODY",
      "text": "Hola {{1}}, tu factura del *{{2}}* por ${{3}} MXN ya está lista.\n\nDescarga XML y PDF aquí: {{4}}\n\nFolio fiscal: {{5}}",
      "example": {
        "body_text": [["Roberto", "12 de marzo", "5,800.00", "https://facturas.aurora.mx/F-1234", "abc12345-6789-..."]]
      }
    }
  ]
}
```

Aprobación esperada: **alta** (transaccional fiscal, indiscutible UTILITY).

### Recordatorio de pago pendiente

```json
{
  "name": "utility_recordatorio_pago_mx",
  "language": "es_MX",
  "category": "UTILITY",
  "components": [
    {
      "type": "BODY",
      "text": "Hola {{1}}, te recordamos que tu pago de ${{2}} MXN por *{{3}}* vence el {{4}}.\n\nPuedes pagar con SPEI:\nBanco: {{5}}\nCLABE: {{6}}\nReferencia: {{7}}\n\nCualquier duda, responde este mensaje.",
      "example": {
        "body_text": [["Ana", "1,500.00", "colegiatura marzo", "viernes 28", "BBVA", "012180012345678901", "ANA-MAR"]]
      }
    }
  ]
}
```

Aprobación esperada: **media-alta**. Meta puede recategorizar a MARKETING si lo considera promocional; redactar neutro.

### Encuesta NPS post-servicio

```json
{
  "name": "utility_nps_post_servicio_mx",
  "language": "es_MX",
  "category": "UTILITY",
  "components": [
    {
      "type": "BODY",
      "text": "Hola {{1}}, gracias por tu visita a {{2}}.\n\nEn una escala del 0 al 10, ¿qué tan probable es que nos recomiendes? Responde con tu número.",
      "example": {
        "body_text": [["Carla", "Salón Aurora"]]
      }
    }
  ]
}
```

## Categoría MARKETING

### Promoción de temporada

```json
{
  "name": "marketing_promo_temporada_mx",
  "language": "es_MX",
  "category": "MARKETING",
  "components": [
    {
      "type": "HEADER",
      "format": "IMAGE"
    },
    {
      "type": "BODY",
      "text": "Hola {{1}}, este {{2}} tenemos {{3}} en {{4}}.\n\nUsa el código *{{5}}* en tu próxima compra.\n\n¿Quieres más detalles?",
      "example": {
        "body_text": [["María", "viernes 15", "15% de descuento", "toda la tienda", "AMIGAS15"]]
      }
    },
    {
      "type": "BUTTONS",
      "buttons": [
        {"type": "QUICK_REPLY", "text": "Ver productos"},
        {"type": "QUICK_REPLY", "text": "Salir"}
      ]
    }
  ]
}
```

Variables: `{{1}}` nombre · `{{2}}` fecha · `{{3}}` % o monto descuento · `{{4}}` categoría · `{{5}}` código.

Aprobación esperada: **media**. Asegurar opt-in demostrable. Evitar urgencia falsa ("¡SOLO HOY!").

### Re-engagement carrito abandonado

```json
{
  "name": "marketing_carrito_abandonado_mx",
  "language": "es_MX",
  "category": "MARKETING",
  "components": [
    {
      "type": "BODY",
      "text": "Hola {{1}}, vimos que dejaste {{2}} en tu carrito. Aún está disponible 🛒\n\nFinaliza tu compra aquí: {{3}}",
      "example": {
        "body_text": [["Diego", "una sudadera Aurora talla M", "https://tienda.aurora.mx/carrito/abc123"]]
      }
    }
  ]
}
```

### Nueva colección/producto

```json
{
  "name": "marketing_nuevo_producto_mx",
  "language": "es_MX",
  "category": "MARKETING",
  "components": [
    {
      "type": "HEADER",
      "format": "IMAGE"
    },
    {
      "type": "BODY",
      "text": "Hola {{1}}, lanzamos {{2}} y queríamos que fueras de los primeros en verla 👀\n\nDescubre aquí: {{3}}",
      "example": {
        "body_text": [["Sofía", "la colección primavera", "https://tienda.aurora.mx/primavera"]]
      }
    }
  ]
}
```

## Categoría AUTHENTICATION

Los templates de OTP están pre-formateados por Meta. Solo eliges el formato del código y el ttl. No editas el cuerpo.

```json
{
  "name": "authentication_otp_general_mx",
  "language": "es_MX",
  "category": "AUTHENTICATION",
  "components": [
    {
      "type": "BODY",
      "text": "{{1}} es tu código de verificación. Por tu seguridad, no lo compartas con nadie."
    },
    {
      "type": "FOOTER",
      "text": "Este código expira en 10 minutos."
    },
    {
      "type": "BUTTONS",
      "buttons": [
        {"type": "OTP", "otp_type": "COPY_CODE", "text": "Copiar código"}
      ]
    }
  ]
}
```

Aprobación esperada: **inmediata** (Meta los aprueba automáticamente en su flujo de OTP).

## Reglas de oro para aprobación rápida

1. **Idioma declarado correctamente** (`es_MX` no `es`).
2. **Ejemplos en `example`** siempre presentes y realistas.
3. **Categoría honesta**: si es promocional, declara MARKETING. Mentir resulta en recategorización + cuenta marcada.
4. **Sin urgencia exagerada**: nada de "¡ÚLTIMA OPORTUNIDAD!" en mayúsculas sostenidas.
5. **Emojis con moderación**: 1-2 por mensaje máximo.
6. **Variables con sentido**: que el ejemplo `body_text` deje claro qué representa cada `{{N}}`.
7. **Sin URLs en el cuerpo si no son variables**: las URLs fijas hardcodeadas pueden bajar la tasa de aprobación si lucen sospechosas. Mejor en botón CTA.
8. **Footer útil** (nombre del negocio, ubicación, ó "puedes responder STOP para no recibir más") — mejora confianza.

## Tono MX — do's y don'ts

**Sí:**
- "Hola Juan" / "Qué tal, María"
- "Te recordamos que..."
- "Responde *SI* para confirmar"
- Tuteo amable (default)
- Emoji ocasional contextual (🛍️ 📅 🎉)
- Negocio en primera persona plural ("recibimos tu orden", "te enviamos")

**No:**
- "Hola estimado cliente" (frío para MX)
- "Vale" (España)
- "Pueden llamarme al..." (poco directo)
- "¡APROVECHA YA!" mayúsculas
- "100% GRATIS GARANTIZADO" (red flag spam)
- "Tío", "móvil", "ordenador" (España)
- Más de 2 emojis seguidos

## Cuándo expandir esta biblioteca

Cada vertical de `plugins-mx` agregará sus propios templates específicos:
- `colegios-mx`: aviso de junta, recordatorio examen, calificación lista, ausencia justificada
- `salon-mx`: confirmación reserva, recordatorio cumpleaños, paquete por vencer
- `talleres-mx`: diagnóstico listo, autorización de trabajo, refacciones pedidas, auto listo
- `veterinaria-mx`: recordatorio vacuna, resultado análisis, paquete medicamento listo

Los templates de cada vertical viven en `<vertical>/skills/<skill>/references/templates.md` y consumen las convenciones de este archivo.
