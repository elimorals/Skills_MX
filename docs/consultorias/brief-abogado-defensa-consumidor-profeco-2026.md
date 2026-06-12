# Brief para abogado defensa del consumidor — validación PROFECO talleres + ventas

**Fecha**: 2026-06-12
**Esfuerzo estimado**: 3-5 horas de consultoría ($5-10k MXN).
**Entregables**: revisión de certificado de garantía + política operativa + plantillas de PROFECO.

---

## 0. Contexto en 2 párrafos

Plugins-mx genera certificados de garantía y políticas de operación para talleres mecánicos, refaccionarias y comercios PyME en México. Estos documentos pueden ser usados como **prueba en defensa ante PROFECO**, por lo que necesitan estar perfectamente redactados — un error puede causar resolución negativa para nuestro usuario.

Necesitamos validación de un abogado especialista en defensa del consumidor (LFPC) que confirme vigencia y suficiencia de los plazos, formatos y procedimientos.

---

## 1. Archivos a revisar

| Archivo | Vertical |
|---|---|
| `talleres-mx/skills/garantia-servicio/SKILL.md` | Certificado garantía + política reclamación |
| `talleres-mx/skills/autorizacion-cliente-wa/SKILL.md` | Bitácora WhatsApp como prueba PROFECO |
| `talleres-mx/skills/orden-trabajo/SKILL.md` | OT detallada con desglose mano de obra + refacciones |
| `talleres-mx/skills/diagnostico-cotizacion/SKILL.md` | Cotización con autorización explícita |
| `talleres-mx/agents/defensor-profeco.md` | Procedimiento de defensa en queja PROFECO |
| `schemas/garantia-servicio-output.schema.json` | Estructura datos del certificado |

---

## 2. Preguntas específicas

### 2.1 Plazos de garantía mínimos

Usamos:
- **Mano de obra**: 30 días naturales mínimo
- **Refacciones**: 90 días naturales mínimo
- **NMX-D-003-IMNC**: lo mencionamos como referencia

**Preguntas**:
1. ¿Estos plazos siguen vigentes en LFPC + NMX 2026?
2. ¿Hay categorías de servicio con plazos mayores obligatorios (frenos, motor, sistemas de seguridad)?
3. ¿La NMX-D-003-IMNC está vigente o fue actualizada?

### 2.2 Bitácora WhatsApp como prueba

Documentamos cada autorización del cliente vía WhatsApp con timestamp + screenshot + texto de respuesta.

**Preguntas**:
1. ¿Es admisible como prueba en procedimiento PROFECO (Art. 80-91 LFPC)?
2. ¿Qué elementos adicionales fortalecerían la prueba? (¿Notificación notarial? ¿Captura con certificación digital?)
3. Si el cliente niega la conversación, ¿cómo se prueba autenticidad?

### 2.3 Certificado de garantía — requisitos LFPC

Nuestro template incluye:
- Datos del taller + cliente + vehículo (VIN/placas)
- Lista de servicios con tipo (mano obra / refacción / mixto)
- Plazo de garantía por concepto
- Exclusiones (uso indebido, falta de mantenimiento, modificaciones)
- Procedimiento de reclamo
- Firma del taller y del cliente

**Preguntas**:
1. ¿Cumple con Art. 79 LFPC (información de la garantía)?
2. ¿Falta alguna mención obligatoria (lugar donde se hace válida, costos del cliente, condiciones específicas)?
3. ¿La cláusula de exclusiones debe ser explícita o se sobreentiende?

### 2.4 Política de "auto detenido" (auto del cliente que no quiere pagar)

Cuando el cliente no autoriza un trabajo cotizado y queremos cobrar diagnóstico + almacenaje:

**Preguntas**:
1. ¿Cobro por diagnóstico requiere autorización previa por escrito del cliente?
2. ¿Cobro por almacenaje del vehículo está regulado? ¿Cuánto tiempo hay para retirarlo antes de poder embargar/abandonar?
3. ¿Si el cliente abandona el vehículo, qué procedimiento legal permite al taller venderlo o desecharlo?

### 2.5 Procedimiento PROFECO escalado

Nuestro agent `defensor-profeco` describe:
1. Recepción de queja PROFECO
2. Defensa con bitácora + certificado + OT + autorización WA
3. Conciliación → arbitraje → audiencia
4. Si necesario, juicio civil

**Preguntas**:
1. ¿Plazos vigentes en cada etapa?
2. ¿Qué errores comunes hacen los talleres que pierden por defensa débil?
3. ¿La carta formal de respuesta debe seguir formato específico?

### 2.6 Casos típicos de queja PROFECO en talleres

**Pregunta abierta**: ¿Cuáles son los 3-5 casos más comunes que veas en práctica y qué errores documentales hacen perder al taller?

---

## 3. Formato de respuesta esperado

- **Tabla resumen** con respuestas
- **Anotaciones en línea** del certificado de garantía
- **Casos prácticos** comunes (top 5)
- **Plantillas faltantes** que recomiendes agregar

---

## 4. Honorarios y entrega

- **Honorarios estimados**: $5,000-$10,000 MXN
- **Plazo solicitado**: 3 semanas

---

## 5. Qué sigue

1. Aplico correcciones al SKILL.md de `garantia-servicio` (estimo 1-2 días)
2. Actualizo el schema con campos adicionales requeridos
3. Marco vigencia validada
4. Te invitamos a revisión anual (servicio recurrente si te interesa)
