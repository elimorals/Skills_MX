---
name: garantia-servicio
description: Gestiona términos de garantía de servicios automotrices conforme a Ley Federal de Protección al Consumidor (PROFECO) en México. Cubre garantía mínima de 30 días en mano de obra y 90 días en refacciones nuevas instaladas (puede ser mayor según política del taller o de la marca de refacción), procedimiento de reclamo de garantía (cliente regresa con la falla, taller valida, repara sin costo si aplica), distinción entre falla cubierta vs uso indebido del vehículo, política de cobro si el reclamo no procede (cobro de diagnóstico de revisión), y documentación que respalda al taller en caso de disputa con cliente. Usar cuando el usuario diga garantía, reclamo de garantía, falla del trabajo, regresó la falla, warranty claim, PROFECO. NO usar para garantía de venta de vehículo (otra ley) ni para garantías de fabrica del auto (responsabilidad de la agencia/marca).
allowed-tools: Read, Write, Edit
---

# Garantía de servicios automotrices

PROFECO regula esto. Cumplir mejora la imagen del taller y previene multas; no cumplir es riesgo legal y reputacional.

## Garantía mínima legal (PROFECO)

Conforme a la **Norma Mexicana NMX-D-003-IMNC** y artículos relacionados de la **Ley Federal de Protección al Consumidor (LFPC)**:

| Concepto | Plazo mínimo |
|---|---|
| Mano de obra del taller | 30 días |
| Refacciones nuevas instaladas por el taller | 90 días o garantía del fabricante (lo que sea mayor) |
| Refacciones usadas o reconstruidas | Lo que el taller indique por escrito (PROFECO recomienda mínimo 30 días) |
| Trabajos de pintura y hojalatería | 90 días en mano de obra |

**El taller puede ofrecer garantía MAYOR a la mínima**, pero no menor. Si el cliente la negocia más larga (ej. 180 días), debe quedar por escrito.

## Política de garantía estándar del taller

Toda OT cerrada incluye un documento de garantía con:

```markdown
# Certificado de Garantía

Folio OT: OT-XXXX
Fecha de cierre del servicio: DD/MM/AAAA
Vencimiento de garantía:
  - Mano de obra: hasta DD/MM/AAAA (30 días)
  - Refacciones: hasta DD/MM/AAAA (90 días o garantía fabricante)

## Trabajos cubiertos

| Trabajo | Cobertura mano de obra | Cobertura refacción |
|---|---|---|
| [Trabajo 1] | 30 días | 90 días (fabricante Brembo: 1 año) |
| [Trabajo 2] | 30 días | 90 días |

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

1. PROFECO emite citatorio al taller (15-30 días hábiles para responder).
2. Audiencia conciliatoria — primera instancia. El 60-70% se resuelve aquí.
3. Si no hay conciliación, procedimiento administrativo — puede llevar 6-18 meses.
4. Multa potencial al taller si se determina que actuó indebidamente (de $1k a $1M+ según gravedad).

**Defensa del taller en PROFECO**:
- Diagnóstico inicial documentado con fotos/video.
- Cotización con desglose claro firmada/autorizada por cliente.
- Bitácora de autorización (skill `autorizacion-cliente-wa`).
- OT firmada al inicio del servicio.
- Certificado de garantía entregado al cliente.
- Bitácora de revisión por garantía si aplica.

Con esos 6 documentos, el taller usualmente gana o concilia favorablemente.

**Sin documentación**, PROFECO tiende a dar la razón al consumidor.

## Casos edge

### Cliente reclama 92 días después de cierre
Refacción todavía bajo garantía (90 días el taller, pero fabricante Brembo es 1 año). Si la falla es de la refacción, hay que canalizar al fabricante para reposición. El taller puede absorber el costo de mano de obra como goodwill o cobrarlo (depende de relación).

### Cliente reclama trabajo NO realizado por el taller
A veces el cliente reclama por trabajo que en realidad fue otro taller. Verificar contra OT original; si no aplica, explicarlo con respeto.

### Reclamo después de modificación al vehículo
Si el cliente cambió neumáticos no compatibles, agregó accesorios, o llevó a otro lado a tocar el sistema reparado, la garantía típicamente se anula. Esto debe estar explicado en el certificado.

### Garantía vence durante el reclamo
Si el cliente avisa día 28 que falla, pero pude llevar el auto día 35 (después de vencimiento): la garantía aplica porque el reclamo se hizo en tiempo. Documentar fecha del aviso.

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

## ⚠ Datos que requieren verificación vigente

1. **NMX-D-003-IMNC** (Norma Mexicana de talleres automotrices): vigencia y contenido actual. Cité de memoria.

2. **Plazos PROFECO** (30 días mano de obra, 90 días refacciones): citados como "mínimo legal". Verificar:
   - Reglamento de la LFPC vigente.
   - Norma específica para servicios automotrices.
   - Acuerdos publicados por PROFECO sobre garantía mínima.

3. **Procedimientos de queja PROFECO**: plazos (citatorio 15-30 días, audiencia conciliatoria, procedimiento administrativo) son aproximados. PROFECO puede haber actualizado.

4. **Multas potenciales** ($1k a $1M+): rangos varían según reforma de la LFPC. Confirmar.

5. **Política de auto en abandono** (60-90 días): tiene base legal específica que requiere revisión por abogado para implementar correctamente. El skill da el marco general, no la implementación legalmente blindada.

**Antes de exponer a cliente**:
- Validar con abogado especializado en defensa del consumidor.
- Imprimir certificado de garantía y validar texto con jurídico.
- Documentar caso de prueba ficticio (sin nombres reales) y simular flujo de queja PROFECO.
