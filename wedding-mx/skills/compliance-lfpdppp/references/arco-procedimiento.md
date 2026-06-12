# Procedimiento detallado de derechos ARCO

Conforme a LFPDPPP (Ley Federal de Protección de Datos Personales en Posesión de los Particulares).

## Marco legal

- **LFPDPPP** Art. 22-32 (ejercicio de derechos)
- **Reglamento LFPDPPP** Art. 89-115 (procedimiento)
- **Lineamientos INAI** (criterios complementarios)

## Derechos cubiertos

| Derecho | Descripción | Cuándo procede |
|---|---|---|
| **A** Acceso | Conocer datos personales tratados, finalidades, condiciones de uso | Siempre |
| **R** Rectificación | Corregir datos inexactos, incompletos, desactualizados | Si datos están mal |
| **C** Cancelación | Eliminar datos cuando ya no sean necesarios | Si conservación no es legal/útil |
| **O** Oposición | Cesar tratamientos específicos | Para fines secundarios o por causa legítima |

---

## Procedimiento estándar

### Paso 1: Recepción de solicitud

El titular debe presentar solicitud por:
- Correo electrónico (designado en aviso de privacidad)
- Dirección física del Responsable
- Cualquier otro medio establecido en el aviso

### Paso 2: Validación de elementos mínimos

La solicitud debe contener (Art. 29 LFPDPPP):

1. **Nombre del titular** y domicilio o medio de notificación
2. **Documentos que acrediten su identidad**: copia de INE, pasaporte, FM2/FM3, etc.
3. **Descripción clara de los datos** que ejercerá el derecho sobre y
4. **Cualquier otro elemento** para facilitar localización (RFC, número de cliente, etc.)
5. **Derecho específico** que ejerce (A, R, C, O)
6. Si es **R**: indicar correcciones específicas + documentos que las sustenten
7. Si es **C**: especificar causa
8. Si es **O**: especificar finalidades a las que se opone

Si falta algún elemento: notificar al titular en **5 días hábiles** para que subsane.

### Paso 3: Confirmación de recepción

Generar acuse de recibo con:
- Fecha y hora de recepción
- Folio único de la solicitud
- Datos del Responsable
- Datos básicos del titular
- Resumen del derecho ejercido

Enviar al titular por el medio que indicó.

### Paso 4: Análisis interno

El Responsable debe:
1. Identificar las bases de datos donde están los datos del titular
2. Verificar la información solicitada
3. Determinar si procede o no el ejercicio
4. Si procede: ejecutar la acción
5. Si no procede: documentar fundamento legal de la negativa

### Paso 5: Respuesta al titular

Plazo legal: **20 días hábiles** desde recepción de solicitud completa.

Posibles respuestas:

#### Concedida
"Conforme a su solicitud del [fecha]:
- [Detalle de lo realizado]
- [Forma de acreditar el cumplimiento]"

#### Parcialmente concedida
"Conforme a su solicitud:
- [Lo que sí procede]
- [Lo que no procede, con fundamento]"

#### Negada
"Su solicitud no procede por las siguientes razones:
- [Fundamento legal]
- [Información sobre cómo impugnar ante INAI]"

### Paso 6: Ejecución

Si concedida:
- **Acceso**: entregar al titular la información en formato accesible (PDF, papel, electrónico)
- **Rectificación**: actualizar las bases de datos + notificar a terceros que hayan recibido los datos
- **Cancelación**: período de bloqueo + supresión + confirmación al titular
- **Oposición**: dejar de tratar para la finalidad opuesta

### Paso 7: Documentación interna

Bitácora ARCO con:
- Fecha de solicitud
- Folio
- Datos básicos del titular (sin exposición)
- Derecho ejercido
- Resolución
- Fecha de respuesta
- Acciones ejecutadas
- Vinculación a documentos generados

### Paso 8: Notificación a terceros

Si los datos fueron transferidos a terceros, notificarles sobre la corrección/cancelación realizada para que actualicen sus bases.

---

## Plantilla: respuesta de Acceso

```markdown
[Ciudad], a [fecha].

[Nombre del titular]
[Domicilio o medio]

Asunto: Respuesta a su solicitud de Acceso (Folio [XXX])

Estimado/a [Nombre del titular]:

En atención a su solicitud recibida el [fecha], donde ejerce su derecho de Acceso conforme a la LFPDPPP, le informamos lo siguiente:

## 1. Datos personales que tratamos sobre usted

[Listar categorías:
- Datos de identificación: nombre, RFC, CURP...
- Datos de contacto: email, teléfono, dirección...
- Datos patrimoniales: ...
- Datos sensibles: ... (solo si aplica)]

## 2. Finalidades del tratamiento

[Listar finalidades primarias y secundarias]

## 3. Origen de los datos

Los datos fueron recabados directamente de usted con motivo de [contexto: contratación de servicio, compra, etc.] el [fecha].

## 4. Transferencias

[Si aplica, listar a quién se ha transferido y por qué motivo. Si no, indicar "No hemos transferido sus datos a terceros sin su consentimiento."]

## 5. Cómo conservamos sus datos

[Indicar período de conservación y motivo]

Documentos anexos:
- Copia electrónica de los datos personales que constan en nuestras bases

Si requiere mayor información o desea ejercer otro derecho ARCO, puede contactarnos en [correo/dirección/teléfono].

Atentamente,

[Nombre del Responsable]
[Cargo]
[Razón social]
```

---

## Plantilla: respuesta de Rectificación

```markdown
[Ciudad], a [fecha].

[Nombre del titular]
[Domicilio o medio]

Asunto: Respuesta a su solicitud de Rectificación (Folio [XXX])

Estimado/a [Nombre del titular]:

En atención a su solicitud del [fecha], donde solicita la Rectificación de los siguientes datos:

| Dato | Valor anterior | Valor solicitado |
|---|---|---|
| [campo 1] | [valor viejo] | [valor nuevo] |
| [campo 2] | [valor viejo] | [valor nuevo] |

Le informamos que [se procedió / no procede]:

[Si se procedió]:
- La actualización fue realizada el [fecha], en las bases de datos correspondientes.
- Sustento documental adjunto: [si requiere]
- Hemos notificado a los siguientes terceros que recibieron sus datos para que actualicen sus registros: [lista]

[Si no procedió]:
- Motivo: [explicación con fundamento legal]
- Documentos requeridos para reconsiderar: [lista]

Si requiere mayor información o no está conforme con esta resolución, puede acudir al INAI:
- Portal: www.inai.org.mx
- Procedimiento de inconformidad: 15 días hábiles desde la notificación de respuesta

Atentamente,

[Responsable]
[Cargo]
```

---

## Plantilla: respuesta de Cancelación

```markdown
[Ciudad], a [fecha].

[Nombre del titular]
[Domicilio o medio]

Asunto: Respuesta a su solicitud de Cancelación (Folio [XXX])

Estimado/a [Nombre del titular]:

En atención a su solicitud del [fecha] de Cancelación de sus datos personales:

[Si se procedió completamente]:
Hemos iniciado el procedimiento de cancelación conforme al Art. 25 LFPDPPP:

1. **Período de bloqueo**: a partir del [fecha], sus datos están bloqueados (no se utilizan para ningún tratamiento) hasta el [fecha + 30 días o el período aplicable].

2. **Supresión definitiva**: el [fecha], procederemos a suprimir físicamente sus datos de nuestras bases.

3. **Excepciones legales**: conservaremos los siguientes datos por las siguientes causas legales:
   - CFDIs emitidos: 5 años (Art. 30 CFF)
   - Comprobantes contables: 5 años (Art. 67 CFF)
   - [Otros si aplican]

[Si la cancelación es parcial]:
Cancelamos [datos canceladas] pero conservamos [datos retenidos] por [fundamento legal].

[Si no procede]:
La cancelación no procede por: [fundamento legal específico]

Si está inconforme, puede acudir al INAI en 15 días hábiles.

Atentamente,

[Responsable]
```

---

## Plantilla: respuesta de Oposición

```markdown
[Ciudad], a [fecha].

[Nombre del titular]
[Domicilio o medio]

Asunto: Respuesta a su solicitud de Oposición (Folio [XXX])

Estimado/a [Nombre del titular]:

En atención a su solicitud del [fecha] de Oposición al tratamiento de sus datos personales para las finalidades de [especificar]:

Le confirmamos que a partir del [fecha], dejaremos de tratar sus datos para los siguientes fines:
- [Finalidad 1, ej. marketing directo]
- [Finalidad 2, ej. encuestas]

Continuaremos tratando sus datos para las siguientes finalidades primarias necesarias para la prestación del servicio contratado:
- [Finalidad primaria 1]
- [Finalidad primaria 2]

Atentamente,

[Responsable]
```

---

## Casos especiales

### Solicitud anónima
No procede. Requiere acreditar identidad del titular.

### Solicitud por representante legal
Procede si presenta:
- Poder notarial con facultades expresas para ejercicio del derecho
- Identificación del representante

### Solicitud de menor
Procede a través del padre/madre/tutor con:
- Acta de nacimiento del menor
- Identificación del padre/madre/tutor

### Solicitud post-mortem
Procede a través de heredero con:
- Acta de defunción
- Documento que acredite calidad de heredero (carta notarial, sentencia)

### Solicitud cuando hay obligación legal de conservar
Negar Cancelación pero indicar:
- Fundamento legal (ej. Art. 30 CFF para CFDIs)
- Plazo de conservación obligatorio
- Compromiso de eliminar al vencimiento

---

## Métricas de cumplimiento

| Métrica | Target |
|---|---|
| Solicitudes ARCO respondidas en plazo (20 días hábiles) | 100% |
| Solicitudes que requieren subsanación | < 20% |
| Solicitudes impugnadas ante INAI | < 5% |
| Resolución favorable al titular en INAI | 0 (idealmente) |

---

## Si el titular impugna ante INAI

Plazo para titular: 15 días hábiles desde respuesta del Responsable.

Procedimiento INAI:
1. Citatorio al Responsable
2. Audiencia de pruebas y alegatos
3. Resolución (en plazo legal)
4. Si afirmativa al titular: el Responsable debe cumplir + posible sanción

Documentación clave para defensa:
- Bitácora ARCO completa
- Acuses de recibo de solicitudes
- Respuestas enviadas con timestamp
- Fundamentos legales de las decisiones

---

## Multas potenciales (INAI)

Conforme a Art. 64-65 LFPDPPP:
- Por incumplir solicitud ARCO sin causa: $1,000 a $320,000 UMAs
- Por tratamiento de datos sin aviso de privacidad: $200 a $320,000 UMAs
- Por vulneración + falta de notificación: $1,000 a $640,000 UMAs

**Multas se DUPLICAN si involucran datos sensibles**.

(UMA 2026: ~$108 MXN diaria. Multa máxima teórica > $80M MXN.)

---

## Ver también

- `aviso-privacidad-plantillas.md` — plantillas por sector
- Skill `compliance-lfpdppp` — implementación principal
- [glosario-fiscal-mx.md](../../../docs/glosario-fiscal-mx.md) — términos
