---
name: comunicacion-padres-wa
description: Diseña y orquesta comunicación masiva con padres de familia vía WhatsApp Business para colegios mexicanos. Cubre avisos académicos (calificaciones disponibles, exámenes próximos, juntas), avisos administrativos (cobros, fechas límite, comprobantes), avisos operativos (suspensión de clases, cambios de horario, eventos), avisos de emergencia (incidentes, climáticos, sanitarios), y comunicación segmentada por grupo/grado. Diseña templates Meta-aprobables, define cadencia para evitar saturación (regla 3-5 mensajes/semana máximo por familia), y maneja opt-out conforme LFPDPPP. Usar cuando el usuario diga aviso a padres, comunicar a padres de familia, mensaje masivo padres, junta de padres, recordatorio escolar, parent communication, school messaging. NO usar para comunicación 1-a-1 con un padre específico (eso es atención personalizada estándar) ni para difusión a externos (eso es marketing).
allowed-tools: Read, Write, Edit
---

# Comunicación masiva con padres vía WhatsApp Business

El colegio típico de 300 alumnos manda 200-500 mensajes/semana a padres. Mal gestionado: padres saturados, mensajes ignorados, padres "silenciando" el número del colegio (= no recibe avisos críticos). Bien gestionado: comunicación efectiva con la mínima fricción.

## Reglas de oro

1. **Máximo 3-5 mensajes por familia por semana** salvo emergencias. Más satura.
2. **Categorizar siempre**: ¿Es operativo? ¿Académico? ¿Administrativo? ¿Emergencia? Permite a padres decidir nivel de atención.
3. **Segmentar audiencia**: no mandar a TODOS los padres avisos de UN solo grado.
4. **Opt-in al inicio del ciclo** y opt-out fácil. LFPDPPP obliga.
5. **Templates UTILITY para todo lo operativo/administrativo**. MARKETING solo para promoción de eventos externos (open house, taller pagado).

## Catálogo de templates por categoría

### Académicos

#### Calificaciones disponibles

```json
{
  "name": "utility_calificaciones_disponibles_colegio_mx",
  "language": "es_MX",
  "category": "UTILITY",
  "components": [{
    "type": "BODY",
    "text": "Hola {{1}}, las calificaciones del bimestre {{2}} de {{3}} ya están disponibles en la plataforma.\n\nConsúltalas en: {{4}}\nUsuario: {{5}}\n\nCualquier duda, escríbenos.",
    "example": {
      "body_text": [["María", "2do", "Diego Pérez (5to A)", "plataforma.colegioaurora.mx", "su matrícula"]]
    }
  }]
}
```

#### Recordatorio de examen próximo

```json
{
  "name": "utility_recordatorio_examen_colegio_mx",
  "language": "es_MX",
  "category": "UTILITY",
  "components": [{
    "type": "BODY",
    "text": "Hola {{1}}, te recordamos que el {{2}} tendremos examen de {{3}} en {{4}}.\n\nTemas a estudiar: {{5}}\n\nNo se nos olvide repasar 📚",
    "example": {
      "body_text": [["María", "lunes 18 de marzo", "Matemáticas", "5to A", "fracciones, conversiones, geometría básica"]]
    }
  }]
}
```

#### Convocatoria a junta de padres

```json
{
  "name": "utility_junta_padres_colegio_mx",
  "language": "es_MX",
  "category": "UTILITY",
  "components": [{
    "type": "HEADER",
    "format": "TEXT",
    "text": "Junta de padres de familia"
  },{
    "type": "BODY",
    "text": "Hola {{1}}, te invitamos a la junta de padres del grupo {{2}}:\n\nFecha: {{3}}\nHora: {{4}}\nLugar: {{5}}\n\nTema: {{6}}\n\nResponde *SI* para confirmar tu asistencia o *NO* si no podrás asistir.",
    "example": {
      "body_text": [["María", "5to A", "viernes 22 de marzo", "6:00 PM", "auditorio principal", "avance académico del bimestre + organización fin de cursos"]]
    }
  }]
}
```

### Administrativos

#### Recordatorio de pago de colegiatura

```json
{
  "name": "utility_recordatorio_colegiatura_colegio_mx",
  "language": "es_MX",
  "category": "UTILITY",
  "components": [{
    "type": "BODY",
    "text": "Hola {{1}}, te recordamos que la colegiatura de {{2}} por ${{3}} MXN del alumno {{4}} vence el {{5}}.\n\nPaga por SPEI:\nBanco: {{6}}\nCLABE: {{7}}\nBeneficiario: {{8}}\nReferencia: {{9}}\n\nCualquier duda, estamos para apoyarte.",
    "example": {
      "body_text": [["María", "marzo", "5,800.00", "Diego (5to A)", "viernes 28", "BBVA", "012180012345678901", "Colegio Aurora SC", "MAT-1234"]]
    }
  }]
}
```

#### CFDI listo para descarga

```json
{
  "name": "utility_cfdi_colegiatura_listo_mx",
  "language": "es_MX",
  "category": "UTILITY",
  "components": [{
    "type": "BODY",
    "text": "Hola {{1}}, tu factura por la colegiatura de {{2}} del alumno {{3}} ya está disponible.\n\nDescarga XML y PDF aquí: {{4}}\nFolio fiscal: {{5}}\n\nRecuerda que las colegiaturas de educación básica son deducibles conforme al Art. 151 LISR con topes específicos por nivel.",
    "example": {
      "body_text": [["María", "marzo", "Diego (5to A)", "https://facturas.colegioaurora.mx/F-1234", "abc12345-6789-..."]]
    }
  }]
}
```

### Operativos

#### Suspensión de clases

```json
{
  "name": "utility_suspension_clases_colegio_mx",
  "language": "es_MX",
  "category": "UTILITY",
  "components": [{
    "type": "HEADER",
    "format": "TEXT",
    "text": "Aviso importante"
  },{
    "type": "BODY",
    "text": "Hola {{1}}, les informamos que el {{2}} *NO habrá clases* en {{3}} por motivo de {{4}}.\n\nLas actividades se reanudan el {{5}}.\n\nCualquier duda, llámenos al {{6}}.",
    "example": {
      "body_text": [["María", "viernes 15 de marzo", "todo el colegio", "junta de consejo técnico SEP", "lunes 18 de marzo", "55-1234-5678"]]
    }
  }]
}
```

#### Cambio de horario

```json
{
  "name": "utility_cambio_horario_colegio_mx",
  "language": "es_MX",
  "category": "UTILITY",
  "components": [{
    "type": "BODY",
    "text": "Hola {{1}}, les informamos que el {{2}}, el horario de {{3}} será de {{4}} a {{5}}.\n\nMotivo: {{6}}\n\nLos cambios de salida programada se notificarán por separado.",
    "example": {
      "body_text": [["María", "miércoles 20 de marzo", "5to A", "8:00 AM", "12:00 PM", "salida temprana por consejo técnico"]]
    }
  }]
}
```

#### Recordatorio de evento

```json
{
  "name": "utility_recordatorio_evento_colegio_mx",
  "language": "es_MX",
  "category": "UTILITY",
  "components": [{
    "type": "BODY",
    "text": "Hola {{1}}, les recordamos el evento *{{2}}* el {{3}} a las {{4}} en {{5}}.\n\nQué traer: {{6}}\nLos esperamos.",
    "example": {
      "body_text": [["María", "Kermés Primaria", "sábado 30 de marzo", "11:00 AM", "patio central", "ropa cómoda y muchas ganas de jugar 🎈"]]
    }
  }]
}
```

### Emergencia / urgentes

#### Incidente

```json
{
  "name": "utility_incidente_colegio_mx",
  "language": "es_MX",
  "category": "UTILITY",
  "components": [{
    "type": "HEADER",
    "format": "TEXT",
    "text": "Aviso urgente"
  },{
    "type": "BODY",
    "text": "Hola {{1}}, les informamos que {{2}}. Su hijo {{3}} se encuentra {{4}}.\n\nLas clases {{5}}.\n\nLes mantendremos informados. Si necesita más detalles, llamenos al {{6}}.",
    "example": {
      "body_text": [["María", "se reportó un sismo de magnitud media", "Diego (5to A)", "bien y a salvo en el punto de reunión del colegio", "se reanudan a las 11:30 AM tras evaluación de seguridad", "55-1234-5678"]]
    }
  }]
}
```

#### Aviso sanitario

```json
{
  "name": "utility_aviso_sanitario_colegio_mx",
  "language": "es_MX",
  "category": "UTILITY",
  "components": [{
    "type": "BODY",
    "text": "Hola {{1}}, les informamos que se han detectado casos de {{2}} en {{3}}.\n\nMedidas que estamos tomando:\n{{4}}\n\nQué pueden hacer ustedes:\n{{5}}\n\nCualquier duda, contáctenos al {{6}}.",
    "example": {
      "body_text": [["María", "varicela", "5to A", "comunicación a familias del grupo, reforzamiento de limpieza, monitoreo de síntomas", "estar atentos a fiebre y erupciones; mantener al alumno en casa si presenta síntomas", "55-1234-5678 ext. 5"]]
    }
  }]
}
```

## Cadencia recomendada

| Tipo | Frecuencia |
|---|---|
| Cobranza | Día 1, día 10, día 20, día 30, día 45 (5 toques) |
| Académico (calif disponibles, examen) | 1-2 por bimestre |
| Convocatoria juntas | 7 días antes + recordatorio 1 día antes |
| Recordatorio eventos | 7 días antes + 1 día antes |
| Operativos no urgentes | 24-48h antes |
| Emergencias | Inmediato |

**Regla agregada**: si tienes que mandar 3+ mensajes en un día a un mismo padre, considera consolidar en uno solo bien estructurado.

## Segmentación de audiencia

Variables relevantes para segmentar:
- **Grado**: distinguir preescolar / primaria / secundaria / prepa
- **Grupo**: distinguir A, B, C dentro del grado
- **Estado de pago**: al corriente / con adeudo
- **Tipo de comunicación opt-in**: emergencias solamente / todo

Listas más comunes:
- "Todo el colegio" (cuidado, solo emergencias o cosas que aplican a todos)
- "Primaria 5to A" (lo más segmentado y útil)
- "Padres con adeudo > 30 días" (cobranza específica)
- "Padres que aceptaron eventos extracurriculares" (promo opcional)

## Opt-in y compliance LFPDPPP

Al inicio del ciclo, el colegio recopila consentimiento explícito de padres para:
- Comunicación operativa (calificaciones, juntas, suspensiones) — necesaria para servicio, no es opcional
- Comunicación de eventos sociales (kermés, festivales, ceremonias) — opt-in default ON
- Promoción de servicios adicionales (talleres pagados, campamentos) — opt-in DEFAULT OFF

Cualquier padre puede solicitar reducir las comunicaciones respondiendo "MENOS" o "STOP" al número del colegio.

## Calidad de cuenta WhatsApp

Avisos masivos generan reportes (cuando alguien marca como spam). Para mantener Quality Rating GREEN:
- No mandar lo mismo a TODOS los padres si solo aplica a un grupo (alto reporte de spam).
- Respetar opt-outs inmediatamente.
- No exceder 5 mensajes/semana/familia salvo emergencia.
- Footer del template con marca del colegio para que padre identifique remitente.

## Salida esperada

Cuando el usuario pida "aviso de [tipo] a [audiencia]":

1. Selecciona el template apropiado de la biblioteca.
2. Pide las variables necesarias para completar (fechas, montos, contexto).
3. Confirma la audiencia objetivo (grado, grupo, lista).
4. Estima cuántas familias recibirán el mensaje.
5. Alerta si hay riesgo de saturación (es el 3er mensaje a esta audiencia esta semana).
6. Genera el mensaje listo para envío y la lista de destinatarios.

## Integración

- `whatsapp-business-mx`: para templates específicos y reglas Meta.
- `cobranza-colegiaturas`: comparte templates de recordatorio de pago.
- `cfdi-colegiaturas-deducibles`: notificación de CFDI listo.
- `compliance-lfpdppp`: registro de opt-ins y opt-outs.
