---
name: autorizacion-cliente-wa
description: Orquesta el flujo de autorización del cliente vía WhatsApp para trabajos de taller automotriz. Envía cotización estructurada con foto/video del problema, recibe respuesta del cliente con qué trabajos aprueba específicamente, registra la autorización con timestamp y método (mensaje WA con texto explícito o respuesta a botones), maneja casos de no respuesta con escalamiento (recordatorio 24h, 48h, 72h con política de auto detenido), y genera bitácora auditada de la autorización para evitar disputas. Implementa la regla clave: ningún trabajo se inicia sin autorización registrada (excepto trabajos de seguridad inmediata con cliente notificado). Usar cuando el usuario diga autorización cliente, aprobar trabajos taller, WhatsApp cotización, autorizar servicio, customer approval workshop. NO usar para diagnóstico inicial (otro skill) ni para cobranza post-servicio (otro skill).
allowed-tools: Read, Write, Edit
---

# Autorización del cliente vía WhatsApp

El 80% de los conflictos en talleres mexicanos vienen de "el cliente dice que no autorizó esto" después de hecho. Este skill cierra esa puerta con bitácora auditada.

## Regla central

**Ningún trabajo se inicia sin autorización explícita y registrada del cliente.**

Excepción única: trabajo de seguridad inmediata (auto que se desarmó y no puede salir sin ese trabajo) con cliente notificado del trabajo y costo, aunque no haya respuesta. Documentar el intento de contacto.

## Flujo completo

### Paso 1: Envío de cotización por WhatsApp

**Template del primer mensaje** (después del diagnóstico):

```
Hola [Nombre del cliente] 👋

Terminamos la revisión de tu [Marca Modelo Año, placas XXX]. Acá los hallazgos:

📋 *Cotización DIAG-XXXX*

Mira el video del problema: [link al video subido]
Y fotos del estado: [link a fotos]

*Trabajos URGENTES* (de seguridad, no debe salir el auto así):
1. [Trabajo 1] — $X,XXX
2. [Trabajo 2] — $X,XXX
Subtotal urgentes: $X,XXX

*Trabajos RECOMENDADOS* (no urgentes pero conviene):
3. [Trabajo 3] — $XXX
Subtotal recomendados: $XXX

*OPCIONALES*:
4. [Trabajo 4] — $XXX

*Tiempo estimado*: [X días/horas]

¿Cuáles trabajos autorizas? Responde con:
1️⃣ Solo URGENTES
2️⃣ URGENTES + RECOMENDADOS
3️⃣ TODOS los trabajos
4️⃣ NINGUNO (recojo el auto, cubro el diagnóstico de $XXX)

O dime trabajos específicos por número si quieres una combinación.

Quedo atento. Saludos,
[Nombre del taller]
```

**Asociado**: template de WA Business UTILITY pre-aprobado.

### Paso 2: Manejo de respuestas

#### Respuesta clara (caso ideal)
Cliente responde "1", "Apruebo urgentes y recomendados", "Quiero todos".

Acciones:
1. Registrar autorización con timestamp y texto literal de la respuesta.
2. Generar Orden de Trabajo formal (`orden-trabajo`).
3. Confirmar al cliente:
   ```
   ¡Listo [Nombre]! Procedemos con los trabajos:
   ✅ [Trabajo 1]
   ✅ [Trabajo 2]

   Tiempo estimado de entrega: [fecha y hora].
   Te aviso cualquier novedad.

   OT-XXXX
   ```

#### Respuesta ambigua
Cliente responde "Hazle lo que sea urgente nomás", "Lo importante", "Lo que tenga que ser".

Acciones:
- NO asumir. Re-confirmar específicamente:
  ```
  Para confirmar [Nombre], los URGENTES son:
  1. [Trabajo 1] - $X,XXX
  2. [Trabajo 2] - $X,XXX
  Subtotal: $X,XXX con IVA.

  ¿Confirmas que con esos procedemos?
  ```

Solo iniciar cuando la confirmación específica esté registrada.

#### Respuesta con pregunta
Cliente pregunta "¿es necesario rotores con balata?" o "¿hay opción más barata?".

Acciones:
- Responder con información técnica clara, sin presión de venta.
- Si hay opción alternativa, explicarla con precio.
- Esperar autorización tras la aclaración.

#### Sin respuesta — escalamiento

**Día 0 (mismo día de cotización)**: enviar mensaje inicial.

**Día +1 (24 horas sin respuesta)**:
```
Hola [Nombre], te recordamos la cotización del [auto] que mandamos ayer.

Cualquier duda, llámanos al [teléfono]. Si necesitas más tiempo para decidir, dinos.

Tu auto sigue en el taller esperando autorización.
```

**Día +3 (72 horas sin respuesta)**:
```
Hola [Nombre], no hemos recibido respuesta a la cotización del [auto].

Conforme a nuestra política, los autos sin autorización tras 5 días generan costo por almacenamiento de $XXX/día.

Por favor responde para coordinar:
1. Autorización para proceder
2. O retiro del auto previo pago del diagnóstico ($XXX)

Llámanos al [teléfono] si prefieres.
```

**Día +5 (políticas de almacenamiento)**: empieza cargo por almacenamiento si está declarado en política inicial.

**Día +15+**: enviar carta formal de aviso de retención según Ley Federal de Protección al Consumidor. En casos extremos, después de 60-90 días sin respuesta, el auto puede pasar a depósito vehicular y eventualmente subastarse según procedimiento legal (requiere asesoría legal específica).

### Paso 3: Cambios durante el trabajo

Si al desarmar se descubre algo nuevo (ej. al cambiar balatas se descubre que el cilindro de freno está dañado):

```
[Nombre], al desarmar encontramos algo adicional:

*Hallazgo*: [descripción]
Foto: [link]

*Trabajo adicional sugerido*: [trabajo]
*Costo adicional*: $XXX

Sin esto, los trabajos originales no resuelven el problema completo.

¿Autorizas también este trabajo adicional?
✅ Sí, procedan
❌ No, ajustar el plan
```

Sin esta autorización adicional registrada, no se realiza. Si el cliente dice "no", se entrega el auto en el estado en que pueda salir y se documenta la negativa.

### Paso 4: Aviso de auto listo

```
¡Hola [Nombre]! Tu [auto] está listo.

✅ Trabajos realizados:
- [Trabajo 1]
- [Trabajo 2]

Total a pagar: $X,XXX
¿Requieres CFDI? Si sí, mándanos tus datos fiscales.

Horario de retiro: [horario del taller]
Dirección: [dirección del taller]

Te esperamos. Saludos.
```

## Bitácora de autorización (archivo digital)

Cada autorización se registra:

```json
{
  "ot_folio": "OT-XXXX",
  "diagnostico_folio": "DIAG-XXXX",
  "cliente": {
    "nombre": "...",
    "telefono_wa": "..."
  },
  "vehiculo": {
    "marca_modelo_ano": "...",
    "placas": "..."
  },
  "interacciones": [
    {
      "timestamp": "2026-03-15T10:30:00-06:00",
      "tipo": "envio_cotizacion",
      "canal": "whatsapp",
      "contenido": "[texto del mensaje enviado]",
      "adjuntos": ["video.mp4", "foto1.jpg"]
    },
    {
      "timestamp": "2026-03-15T14:12:00-06:00",
      "tipo": "respuesta_cliente",
      "canal": "whatsapp",
      "contenido_literal": "Apruebo urgentes y recomendados",
      "interpretacion": "Aprueba trabajos 1, 2, 3"
    },
    {
      "timestamp": "2026-03-15T14:15:00-06:00",
      "tipo": "confirmacion_taller",
      "canal": "whatsapp",
      "trabajos_autorizados": [1, 2, 3],
      "ot_generada": "OT-XXXX"
    }
  ],
  "estado": "autorizado | en_proceso | listo | entregado | sin_respuesta | rechazado"
}
```

Si llega a tribunal del consumidor (PROFECO) o civil, esta bitácora es prueba.

## Reglas de oro

1. **Autorización en texto explícito**, no en silencio. Silencio no es consentimiento.
2. **Cambios al alcance original requieren nueva autorización**. No "ya que estabas".
3. **Bitácora con timestamps y screenshots WA si es posible**. Backup en archivo local.
4. **Política de auto detenido transparente desde el inicio**. Mencionada en diagnóstico, recordada en mensajes de no respuesta.
5. **NO trabajar sin autorización por presión de tiempo**. Mejor el cliente regrese a la semana que ir a PROFECO.

## Salida esperada

Cuando el usuario invoca este skill para una cotización pendiente:

1. Identifica estado actual (sin enviar, esperando respuesta, autorizado, en proceso).
2. Sugiere siguiente acción según estado.
3. Genera template específico para la acción.
4. Registra la nueva interacción en bitácora.
5. Si autorización confirmada, dispara `orden-trabajo` para generar OT formal.

## Integración

- `diagnostico-cotizacion`: el input es la cotización generada.
- `orden-trabajo`: el output (cuando hay autorización) genera OT formal.
- `whatsapp-business-mx`: templates para los mensajes UTILITY.
- `garantia-servicio`: la OT autorizada inicia garantía al cierre.
- `compliance-lfpdppp`: la bitácora contiene datos personales; tratamiento conforme aviso.
