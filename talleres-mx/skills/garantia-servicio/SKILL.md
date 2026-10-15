---
name: garantia-servicio
description: Gestiona la garantía de servicios de taller automotriz conforme a la Ley Federal de Protección al Consumidor (LFPC). Mínimo legal de 90 días naturales desde la entrega tanto en mano de obra como en refacciones (Arts. 77 y 81 LFPC), o el plazo mayor que ofrezca el taller o el fabricante. Cubre el certificado de garantía, el procedimiento de reclamo (cliente regresa con la falla, taller valida, repara sin costo si aplica), falla cubierta vs uso indebido, cobro de revisión si el reclamo no procede, y el expediente que respalda al taller ante una queja en PROFECO. Usar cuando el usuario diga garantía, reclamo de garantía, falla del trabajo, regresó la falla, warranty claim, PROFECO, queja del cliente. NO usar para garantía de venta de vehículo ni para garantías de fábrica del auto (agencia/marca).
allowed-tools: Read, Write, Edit
---

# Garantía de servicios automotrices

PROFECO vigila esto. Cumplir previene sanciones y quejas; no cumplir es riesgo legal y reputacional.

## Garantía mínima legal (LFPC)

- **Art. 77 LFPC**: la garantía no puede ser menor a **90 días** desde la entrega del bien o la prestación del servicio.
- **Art. 81 LFPC**: si una reparación o mantenimiento presenta deficiencias imputables al taller dentro de los **90 días naturales** posteriores a la entrega, el consumidor tiene derecho a que se repare de nuevo sin costo. Si la garantía ofrecida es mayor, rige el plazo mayor.
- **Art. 60 LFPC**: en reparaciones se usan refacciones nuevas y apropiadas, salvo que el consumidor autorice expresamente otras (usadas o reconstruidas). Esa autorización va por escrito en la OT.
- **NOM-174-SCFI-2007** (información en la prestación de servicios): precios a la vista, presupuesto y desglose de mano de obra y refacciones, garantía por escrito. Confianza media: verifica el texto vigente en el DOF.
- Contrato de adhesión: PROFECO ha sancionado talleres por no tener contrato de adhesión registrado; revisa si tu giro debe registrarlo (Registro Público de Contratos de Adhesión).

| Concepto | Plazo mínimo |
|---|---|
| Mano de obra del taller | 90 días naturales desde la entrega |
| Refacciones nuevas instaladas | 90 días naturales, o la garantía del fabricante si es mayor |
| Refacciones usadas o reconstruidas (autorizadas por escrito) | 90 días naturales; el taller puede ofrecer más, no menos |
| Pintura y hojalatería | 90 días naturales |

El taller puede ofrecer garantía **mayor**, nunca menor. Una política de "30 días en mano de obra" incumple la LFPC.

## Política de garantía estándar del taller

Toda OT cerrada incluye un documento de garantía con:

```markdown
# Certificado de Garantía

Folio OT: OT-XXXX
Fecha de cierre del servicio: DD/MM/AAAA
Vencimiento de garantía:
  - Mano de obra: hasta DD/MM/AAAA (90 días naturales)
  - Refacciones: hasta DD/MM/AAAA (90 días naturales o garantía del fabricante, la mayor)

## Trabajos cubiertos

| Trabajo | Cobertura mano de obra | Cobertura refacción |
|---|---|---|
| [Trabajo 1] | 90 días | 90 días (fabricante: 1 año) |
| [Trabajo 2] | 90 días | 90 días |

## Qué cubre
- Falla del trabajo realizado por causa imputable al taller (mala instalación, error de procedimiento).
- Falla de refacción nueva instalada por defecto de fábrica (dentro del plazo del fabricante).

## Qué NO cubre
- Daños por uso indebido del vehículo (correr en condiciones no recomendadas, sobrecarga, terreno inadecuado).
- Daños por accidente posterior al servicio.
- Desgaste normal de la pieza por uso (las balatas se desgastan con kilometraje normal).
- Daños por falta de mantenimiento posterior (no checar niveles, no realizar servicios recomendados).
- Trabajos realizados por terceros sobre la misma pieza después de nuestro servicio.
- Modificaciones al vehículo posteriores que afecten el sistema reparado.

## Procedimiento de reclamo

Si presenta falla relacionada con el trabajo realizado:

1. Contactar al taller dentro del plazo de garantía: [teléfono / WhatsApp].
2. Acudir al taller con el vehículo y el certificado de garantía.
3. Revisión gratuita para validar si la falla está cubierta.
4. Si está cubierta: reparación sin costo dentro de los días hábiles necesarios.
5. Si NO está cubierta (uso indebido, otra causa): cobro de diagnóstico de $XXX MXN y cotización normal de reparación.

## Datos
- Taller: [Razón social]
- Dirección: [...]
- Horario: [...]
- Contacto: [...]

Firmas:
- Taller: ____________
- Cliente: ____________
```

## Procedimiento de reclamo paso a paso

### Paso 1: Recepción del reclamo

Cliente regresa diciendo "se volvió a aflojar lo que arreglaron" o "sigue haciendo el ruido".

Acciones del taller:
1. Recibir con buena disposición. NO defensivo desde el inicio.
2. Validar que la garantía esté vigente (consultar fecha de cierre de OT vs hoy).
3. Recibir el auto, asignar a mecánico (idealmente el mismo que hizo el trabajo original).
4. Generar folio de revisión por garantía vinculado a la OT original.

### Paso 2: Diagnóstico de validación

Mecánico inspecciona y determina:
- **Caso A**: la falla es la misma del trabajo original. Cubierta por garantía.
- **Caso B**: la falla es nueva (componente distinto). NO cubierta.
- **Caso C**: la falla es la misma pero por uso indebido o causa externa. NO cubierta.
- **Caso D**: necesita más diagnóstico para determinar (raro pero ocurre).

### Paso 3: Comunicación al cliente

#### Si Caso A — cubierta
```
Hola [Nombre], validamos la falla y SÍ está cubierta por la garantía del trabajo realizado en OT-XXXX.

Procedemos sin costo. Tiempo estimado: [plazo].

Te aviso cuando esté listo.
```

#### Si Caso B/C — no cubierta
```
Hola [Nombre], revisamos el auto y la falla actual NO está relacionada con el trabajo previo de OT-XXXX.

Detalle:
- [Explicación clara]
- Causa: [...]
- Foto: [link]

Cotización para reparar:
- Mano de obra: $X,XXX
- Refacciones: $X,XXX
- Total: $X,XXX MXN

Costo del diagnóstico de revisión: $XXX MXN (se descuenta si autorizas la reparación).

¿Cómo quieres proceder?
```

#### Si Caso D — más diagnóstico
```
Hola [Nombre], necesitamos un poco más de tiempo para determinar la causa de la falla.

Te aviso en [X horas/día] con el detalle.

Mientras tanto, el auto se queda en el taller.
```

### Paso 4: Documentación

Cualquier reclamo de garantía debe quedar registrado:
- Folio de revisión por garantía.
- Vinculación con OT original.
- Diagnóstico de la falla actual.
- Determinación (cubierta/no cubierta).
- Fotos del estado.
- Comunicación con el cliente.

Este expediente protege al taller en caso de queja PROFECO.

## Si el cliente se va a PROFECO

Si el cliente decide quejarse en PROFECO, el procedimiento típico:

1. PROFECO recibe la queja (presencial o Concilianet si el proveedor está adherido) y cita al taller.
2. Audiencia de conciliación: el taller presenta su informe y documentos.
3. Si no hay acuerdo, PROFECO deja a salvo los derechos del consumidor (vía judicial o arbitraje) y puede iniciar un procedimiento por infracciones a la LFPC.
4. Las multas están en los Arts. 126–128 LFPC y PROFECO las actualiza cada año (Acuerdo en el DOF). No cites montos sin revisar el acuerdo vigente.

**Defensa del taller en PROFECO**:
- Diagnóstico inicial documentado con fotos/video.
- Cotización con desglose claro firmada/autorizada por cliente.
- Bitácora de autorización (skill `autorizacion-cliente-wa`).
- OT firmada al inicio del servicio.
- Certificado de garantía entregado al cliente.
- Bitácora de revisión por garantía si aplica.

Con esos documentos el taller puede demostrar qué se autorizó, qué se hizo y qué garantía se dio. Sin documentación, es su palabra contra la del cliente.

## Casos edge

### Cliente reclama 92 días después de cierre
Pasaron los 90 días legales del taller, pero la refacción puede seguir bajo garantía del fabricante (p. ej. 1 año). Si la falla es de la refacción, hay que canalizar al fabricante para reposición. El taller puede absorber el costo de mano de obra como goodwill o cobrarlo (depende de relación).

### Cliente reclama trabajo NO realizado por el taller
A veces el cliente reclama por trabajo que en realidad fue otro taller. Verificar contra OT original; si no aplica, explicarlo con respeto.

### Reclamo después de modificación al vehículo
Si el cliente cambió neumáticos no compatibles, agregó accesorios, o llevó a otro lado a tocar el sistema reparado, la garantía típicamente se anula. Esto debe estar explicado en el certificado.

### Garantía vence durante el reclamo
Si el cliente avisa el día 85 que falla, pero puede llevar el auto el día 95 (después del vencimiento): la garantía aplica porque el reclamo se hizo en tiempo. Documentar fecha del aviso.

## Salida esperada

Cuando el usuario invoca este skill para un reclamo:

1. Lee OT original y certificado de garantía.
2. Valida vigencia.
3. Conduce el flujo de validación de reclamo.
4. Genera comunicación al cliente según caso (A/B/C/D).
5. Genera documentación del proceso.
6. Si Caso B/C (no cubierta), genera cotización adicional.

Cuando se invoca para "generar certificado de garantía de OT-XXXX":

1. Lee OT cerrada.
2. Genera certificado completo en `garantias/[OT].md`.
3. Sugiere imprimir + entregar al cliente al recoger el auto.

## Integración

- `orden-trabajo`: la OT cerrada genera el certificado de garantía.
- `diagnostico-cotizacion`: si reclamo NO cubierto, genera nueva cotización.
- `compliance-lfpdppp`: el expediente contiene datos del cliente.
- `whatsapp-business-mx`: templates para comunicación durante el reclamo.

## Datos que requieren verificación

1. **Arts. 60, 77 y 81 LFPC**: verificados contra fuentes secundarias (mley.mx, El Financiero); confirma el texto vigente en diputados.gob.mx.
2. **NOM-174-SCFI-2007**: contenido aplicable a talleres sin cotejar contra el DOF (confianza media).
3. **Multas LFPC**: montos actualizados anualmente por PROFECO; consultar el acuerdo vigente.
4. **Auto en abandono / derecho de retención**: no lo regula la LFPC; depende del código civil local. Requiere abogado.

Antes de usar el certificado con clientes, valida el texto con un abogado de derecho del consumidor.
