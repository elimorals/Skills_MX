# Brief para contador especializado en sector educativo — validación colegios

**Fecha**: 2026-06-12
**Esfuerzo estimado**: 4-6 horas de consultoría ($5-15k MXN).
**Entregables**: validación de CFDI D10/InsEduc + topes decreto facilidad + RVOE/CCT.

---

## 0. Contexto en 2 párrafos

Plugins-mx tiene un vertical `colegios-mx` y un vertical `educacion-particular-b2c-mx` que emiten CFDIs con complemento InsEduc para que el padre/tutor pueda deducir colegiaturas. Este es un esquema con **alta complejidad regulatoria SAT + SEP** y errores generan rechazo de deducción al padre o multas al colegio.

Necesitamos validación de un contador con experiencia en sector educativo MX (escuelas K-12 o universidades particulares) que confirme datos vigentes 2026.

---

## 1. Archivos a revisar

| Archivo | Cubre |
|---|---|
| `colegios-mx/skills/cfdi-colegiaturas-deducibles/SKILL.md` | CFDI D10 con InsEduc |
| `colegios-mx/skills/cobranza-colegiaturas/SKILL.md` | Política retención académica vs cobranza |
| `colegios-mx/skills/constancias-academicas/SKILL.md` | Boleta, constancia estudios, no adeudo |
| `educacion-particular-b2c-mx/skills/cfdi-curso-online-d10/SKILL.md` (si existe) | CFDI cursos online |
| `schemas/constancias-academicas-output.schema.json` | Datos requeridos: CCT, RVOE, autorización estatal |

---

## 2. Preguntas específicas

### 2.1 Decreto facilidad colegiaturas — topes 2026

Usamos:

| Nivel | Tope anual MXN |
|---|---|
| Preescolar | $14,200 |
| Primaria | $12,900 |
| Secundaria | $19,900 |
| Profesional técnico | $17,100 |
| Bachillerato | $24,500 |
| Universidad/posgrado | NO deducible |

**Preguntas**:
1. ¿Vigentes 2026? ¿Hay actualización pendiente de publicar en DOF?
2. ¿Hay topes diferenciados por modalidad (escolarizado vs mixto)?
3. ¿Hay topes diferenciados por entidad federativa o son nacionales?
4. ¿Decreto incluye también gastos por inscripción, materiales, uniformes? (Yo creo que NO, confirmar)

### 2.2 Complemento InsEduc — versión vigente

Manejamos el complemento como obligatorio para que el padre deduzca.

**Preguntas**:
1. ¿Cuál es la versión vigente 2026? (1.1, 2.0, otra)
2. ¿Hay campos nuevos vs años anteriores que pueden hacer fallar el timbrado?
3. ¿La CCT del centro educativo es siempre obligatoria o hay excepciones?
4. ¿Para particulares con autorización ESTATAL (no federal), el código que va en complemento es distinto del CCT federal?

### 2.3 Requisitos para que padre pueda deducir

Manejamos como obligatorio:
- CFDI a nombre del padre/tutor (con su RFC)
- Pago electrónico (NO efectivo)
- CURP del alumno en el complemento
- Parentesco con el padre (línea directa)

**Preguntas**:
1. ¿Hay requisitos adicionales que faltan? (constancia situación fiscal del padre, autorización del otro padre si están separados, etc.)
2. Si el alumno tiene 18+ años y trabaja, ¿el padre aún puede deducirlo? (Yo creo que SÍ si es dependiente económico, confirmar)
3. Si pago en parcialidades a lo largo del año, ¿cómo se factura — un CFDI por parcialidad o uno anual al cierre?

### 2.4 CFDI tipo G03 vs D10

Usamos D10 para colegiaturas + universidad cuando aplica al padre como gasto deducible. ¿Es la elección correcta?

**Preguntas**:
1. ¿G03 sería alternativa válida o D10 es obligatorio?
2. Si el receptor es PM (empresa que paga colegiatura como prestación al empleado), ¿qué UsoCFDI corresponde?

### 2.5 Política de retención académica vs LGE

En el skill `cobranza-colegiaturas` describimos retener boleta/constancia si hay adeudo de colegiatura.

**Preguntas**:
1. ¿Esta práctica es legal vigente? La LGE prohibe retener documentos académicos por adeudo en ciertos niveles (¿primaria? ¿secundaria?). Confirmar alcance.
2. ¿En qué niveles educativos sí puede aplicarse?
3. ¿Cómo manejar el alumno que ya ganó el ciclo pero no tiene boleta entregada?

### 2.6 CCT vs RVOE vs autorización estatal

Manejamos:
- CCT: Clave Centro de Trabajo (SEP federal)
- RVOE: Reconocimiento de Validez Oficial de Estudios (federal)
- Autorización estatal: para particulares con autorización del estado (no federal)

**Preguntas**:
1. ¿Para que el padre deduzca, basta cualquiera de las 3 o requiere RVOE federal específicamente?
2. ¿Hay obligación del colegio de hacer pública la cédula RVOE (para que padres validen)?
3. ¿Una escuela puede tener CCT pero NO RVOE (caso bastante común). ¿Sus colegiaturas son deducibles?

### 2.7 Universidades particulares — caso especial

Mencionamos que universidad NO es deducible. ¿Hay excepción para algún programa específico?

**Preguntas**:
1. ¿Hay programas de posgrado con RVOE que sí entren en algún decreto?
2. ¿Becas que el padre recibe se consideran ingreso acumulable de quién?

---

## 3. Formato de respuesta esperado

- **Tabla con preguntas** y respuestas
- **Topes vigentes 2026** confirmados
- **Casos edge** que tu experiencia detecte que no contemplamos
- **Documentos faltantes** que recomiendes agregar (avisos, manuales, formatos SEP)

---

## 4. Honorarios y entrega

- **Honorarios estimados**: $5,000-$15,000 MXN según profundidad
- **Plazo solicitado**: 3 semanas

---

## 5. Qué sigue después de tu validación

1. Aplico tus correcciones al SKILL.md
2. Marco vigencia validada
3. Actualizo schema constancias-academicas con campos adicionales requeridos
4. Genero fixtures con casos de prueba (RVOE, CCT, particular estatal)
5. Te invitamos a revisión anual (servicio recurrente si te interesa, especialmente cada que decreto se actualiza)
