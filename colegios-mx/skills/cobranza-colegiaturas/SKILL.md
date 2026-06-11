---
name: cobranza-colegiaturas
description: Flujo escalado de cobranza de colegiaturas para colegios privados mexicanos. Cinco etapas progresivas con templates específicos para padres de familia (tono empático pero firme), considera la dinámica relacional única (el colegio no puede ofender al padre que va al colegio mañana a llevar al hijo), políticas reales de suspensión académica (cuándo es legal retener calificaciones vs cuándo NO según SEP), penalizaciones aplicables (recargo por mora típico 2-5% mensual), opciones de regularización (convenio de pago, descuentos por pronto pago para regularizar), y derivación a cobranza extrajudicial sin perder al alumno. Usar cuando el usuario diga cobranza colegiatura, padres morosos, mensualidad atrasada, cartera vencida colegio, recordatorio pago padres, recargo escolar. NO usar para alumnos becados (otra lógica) ni para baja del alumno (otra decisión administrativa).
allowed-tools: Read, Write, Edit
---

# Cobranza de colegiaturas

Único: la cobranza escolar tiene una dinámica relacional especial. El colegio NO PUEDE ofender al padre porque mañana el hijo está en el aula. La firmeza tiene que coexistir con el respeto y la posibilidad de continuidad.

## Las 5 etapas

### Etapa 1 — Recordatorio amable (día 1-3 post vencimiento)

Asume buena fe. La mayoría de pagos atrasados son distracción del padre, no incapacidad.

**Template WhatsApp Business (UTILITY)**:
```
Hola [Padre/Madre],

Te recordamos que la colegiatura de [Mes] por $[monto] MXN del alumno [Nombre del alumno] vencía el [fecha].

Puedes pagar por SPEI:
Banco: [BANCO]
CLABE: [XXX]
Beneficiario: [Razón Social del colegio]
Referencia: [matrícula o nombre alumno]

Cualquier duda, estamos para apoyarte.

Saludos,
Administración [Colegio]
```

**Tono**: amable, asume distracción, ofrece facilidad. Sin drama.

### Etapa 2 — Recordatorio formal con recargo (día 10-15 post vencimiento)

Cliente no responde. Se aplica el recargo establecido en el reglamento interno.

**Template**:
```
Hola [Padre/Madre],

Damos seguimiento a la colegiatura de [Mes] del alumno [Nombre], con monto vencido de $[monto] MXN.

Conforme al reglamento, a partir del día 10 se aplica recargo del [%]% mensual:
- Colegiatura: $[monto] MXN
- Recargo acumulado: $[recargo] MXN
- Total al día de hoy: $[total] MXN

Te pedimos liberar el pago a la brevedad para mantener la situación al corriente.

Datos para SPEI: [como arriba]

Si tienes dificultad para cubrir el monto, podemos platicar opciones. Llámanos al [teléfono].

Administración [Colegio]
```

**Tono**: profesional, factual, ofrece diálogo. Sin amenaza.

### Etapa 3 — Llamada + cita con tutoría (día 20-30 post vencimiento)

Cliente sigue sin responder. Cambio de canal: llamada telefónica directa del área administrativa, idealmente la directora administrativa o tesorería.

**Script de llamada**:
```
Buenos días/tardes, le habla [Nombre] de la administración de [Colegio].

Le llamo para platicar sobre la colegiatura del mes de [Mes] del alumno [Nombre]. A la fecha no hemos recibido el pago y queremos asegurarnos de que todo esté bien por su lado.

[Escuchar — dejar que hable]

[Posibles respuestas y cómo proceder]:

Si dice que pagará en X días:
"Perfecto, le agradezco. Para que quede registrado, ¿puedo anotar la fecha del [X]? Si hay algún cambio, por favor avísenos para reagendar."

Si reporta problema económico real:
"Entiendo. ¿Podemos agendar una cita con la directora administrativa esta semana para platicar un convenio de pago que les funcione? Tenemos opciones."

Si responde evasivamente:
"Entiendo. Le envío hoy por correo el detalle del adeudo y los próximos pasos. Le pedimos respondernos en los próximos 3 días para evitar mayores complicaciones."
```

**Importante**: NO amenazar con suspensión académica en este punto.

### Etapa 4 — Carta formal de adeudo (día 35-45)

Sin respuesta tras llamada. Documento formal entregado a mano o por correo certificado.

**Template carta**:
```
[Ciudad], a [DD] de [mes] de [AAAA].

C. [Nombre del padre/madre/tutor]
Dirección: [domicilio]

ASUNTO: Adeudo de colegiaturas

Estimado/a [Nombre]:

Por este medio le hacemos del conocimiento que a la fecha presenta adeudo de colegiaturas correspondientes a los meses de [Meses], del alumno [Nombre completo del alumno], matrícula [matrícula], inscrito en [Grado/Grupo] del ciclo escolar [Ciclo].

Detalle del adeudo:

| Mes | Concepto | Vencimiento | Monto | Recargo | Total |
|---|---|---|---|---|---|
| ... | Colegiatura | ... | $... | $... | $... |
| ... | Colegiatura | ... | $... | $... | $... |

**Total adeudado al día de hoy**: $[total] MXN

Conforme al reglamento interno y al contrato de prestación de servicios educativos firmado por ustedes, le requerimos liberar el pago íntegro o agendar una reunión con la administración para acordar un convenio de pago, en un plazo no mayor a 10 días hábiles a partir de la recepción de esta comunicación.

Sabemos que las situaciones económicas pueden complicarse y estamos abiertos a encontrar una solución. Sin embargo, de no recibir respuesta o pago en el plazo señalado, nos veremos en la necesidad de tomar las medidas administrativas conforme al reglamento.

Quedamos atentos a sus comentarios.

Atentamente,

[Nombre Director Administrativo]
[Cargo]
[Razón social del colegio]
[Teléfono]
[Email]
```

**Tono**: muy formal, factual, abierto a diálogo, sin agresión.

### Etapa 5 — Convenio de pago o cobranza extrajudicial (día 50+)

Dos caminos posibles:

#### Camino A — Convenio de pago (preferible)
Si el padre se acerca a dialogar, ofrecer:

**Opciones de convenio**:
1. **Pago de 50% inmediato + saldo a 3 meses sin intereses** (incentivo para liberar parcialmente).
2. **Pago a 6 meses con intereses al 1.5% mensual** (más holgado, costoso).
3. **Descuento del 20% si paga total en 7 días** (incentivo agresivo si el colegio prefiere liquidez).

**Documento del convenio**:
```
Convenio de Pago de Adeudo

Las partes acuerdan lo siguiente respecto al adeudo de $[monto] MXN del alumno [Nombre]:

1. Monto total reconocido: $[monto] MXN
2. Esquema de pago: [opción elegida]
3. Fechas y montos específicos:
   - [Fecha 1]: $[monto]
   - [Fecha 2]: $[monto]
   - [Fecha 3]: $[monto]
4. Si incumple alguna fecha: vencimiento anticipado del saldo total + recargo del 3% mensual.
5. Vigencia: hasta liquidación total.

Firma del padre/madre/tutor: ____________
Firma de la administración: ____________
Fecha: ____________
```

#### Camino B — Cobranza extrajudicial

Si no hay diálogo después de 60-90 días:
- Pasar a despacho de cobranza (típicamente comisión 30-40% del recovery).
- Considerar baja del alumno conforme al reglamento (con notificación formal previa).

## Lo que el colegio NO PUEDE hacer

Importante saber los límites legales:

1. **No retener calificaciones por adeudo** según la SEP en el ciclo en curso si el alumno está vigente. La retención es una sanción no permitida si el alumno está inscrito y asistiendo.

2. **No expulsar al alumno a media clase** ni "negarle la entrada" sin notificación formal previa y sin agotar el proceso administrativo del reglamento.

3. **No publicar listas de morosos** ni exponer al padre frente a otros padres. Daño moral y violación LFPDPPP.

4. **No cobrar montos no establecidos en el contrato**. Recargos, intereses, comisiones administrativas: SOLO si están en el reglamento firmado al inicio del ciclo.

5. **No retener documentos académicos de ciclos pasados** (boletas, certificados, constancias). La SEP ha emitido pronunciamientos: el adeudo no faculta a retener documentos oficiales. El colegio puede solicitar el pago como condición para CFDI, pero no para documentos académicos terminados.

## Lo que el colegio SÍ PUEDE hacer

1. **Aplicar recargo por mora** establecido en el reglamento.
2. **Suspender CFDI** de colegiaturas no pagadas (no se factura lo no cobrado).
3. **Negar re-inscripción al ciclo siguiente** si hay adeudo vigente.
4. **Solicitar pago total** para acceso a graduación/ceremonia.
5. **Aplicar cláusula de baja** si está en el reglamento y se sigue el procedimiento.

## Insights operativos

- **80% de la cobranza se cierra en etapas 1-2** si se manda a tiempo. Sistemas semi-automatizados con WhatsApp Business cierran este 80% sin intervención humana.
- **Padres con 2+ hijos en el colegio** tienen mayor "stickiness" — más posibilidades de regularizar para no cambiar a ambos hijos.
- **Convenio firmado salva relación**: 60-70% de familias con convenio cumplen y se quedan al ciclo siguiente.
- **La directora administrativa debe llamar personalmente** en etapa 3, no delegar. Hace la diferencia.
- **Documentar TODO**: cada interacción, cada promesa de pago. En caso de baja, el expediente respalda la decisión.

## Comunicación con padres en cobranza — tono

**Sí**:
- Empatía sincera ("entendemos que las situaciones pueden complicarse")
- Datos específicos (montos, fechas, opciones concretas)
- Apertura al diálogo ("queremos encontrar una solución")
- Profesionalismo (sin emoción negativa)

**No**:
- Tono amenazante ("vamos a sacar a su hijo")
- Vergüenza pública ("usted ya tiene varios meses sin pagar")
- Comparaciones ("otros papás sí pagan")
- Drama emocional ("estamos preocupados por el futuro de su hijo")

## Salida esperada

Cuando el usuario pida "cobranza para [familia]":

1. Lee historial de pagos de la familia.
2. Identifica etapa apropiada según mora.
3. Genera template específico con datos del alumno, monto, recargo si aplica.
4. Si etapa 4-5, prepara documento formal.
5. Registra en bitácora de cobranza con timestamp.

## Integración

- `whatsapp-business-mx`: para envío via WA con templates UTILITY.
- `comunicacion-padres-wa`: cuando se necesita aviso a grupo grande de padres morosos.
- `cfdi-colegiaturas-deducibles`: si la familia regulariza, se emite CFDI deducible.
- `compliance-lfpdppp`: para resguardo de datos de cobranza.
