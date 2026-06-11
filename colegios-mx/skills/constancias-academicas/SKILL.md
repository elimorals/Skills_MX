---
name: constancias-academicas
description: Genera constancias académicas, boletas de calificaciones, certificados de estudios, constancias de inscripción y otros documentos académicos para colegios privados mexicanos. Estructura conforme a lineamientos SEP (Clave de Centro de Trabajo CCT, RVOE, número de incorporación cuando aplica), incluye datos obligatorios del alumno (CURP, matrícula, grado, ciclo), del colegio (razón social, CCT, RVOE, domicilio), firma del director y sello, y para constancias oficiales con valor para trámites incluye footer legal correcto. Maneja casos de constancia con/sin adeudo (no se pueden retener documentos de ciclos pasados pero sí condicionar CFDI). Usar cuando el usuario diga constancia académica, constancia de estudios, boleta, certificado, certificado de estudios, certificado parcial, constancia de inscripción, school transcript, certificate of studies. NO usar para certificado final SEP (ese lo emite la autoridad, el colegio solo proporciona los antecedentes).
allowed-tools: Read, Write, Edit
---

# Constancias académicas SEP-compliant

Documentos académicos generados con los datos correctos para tener validez. Errores comunes que invalidan: falta CCT, RVOE no actualizado, firma de director que ya no está, sello desactualizado.

## Tipos de constancia

### 1. Constancia de inscripción

Acredita que el alumno está inscrito en el colegio para el ciclo en curso. Útil para trámites bancarios, becas, traslados.

```markdown
# CONSTANCIA DE INSCRIPCIÓN

[Membretado del colegio con logo, razón social, CCT, RVOE, domicilio, teléfono]

[Ciudad], a los [DD] días del mes de [mes] de [AAAA].

A QUIEN CORRESPONDA:

Por medio de la presente, [Razón social del colegio], con Clave de Centro de Trabajo [CCT] y RVOE [número y fecha], hace constar que:

**[NOMBRE COMPLETO DEL ALUMNO]**, con CURP [CURP], matrícula [matrícula], se encuentra debidamente inscrito en este plantel cursando el [grado] de [nivel educativo] del ciclo escolar [ciclo, ej. 2025-2026], en el turno [matutino/vespertino], grupo [letra].

Se extiende la presente a petición del interesado para los fines que estime convenientes.

ATENTAMENTE

________________________
[Nombre del Director]
Director / Titular
[Razón social del colegio]

[Sello del colegio]
```

### 2. Constancia de estudios

Acredita estudios cursados en el colegio. Útil para inscripciones a otro plantel, trámites de incorporación.

Similar a la de inscripción pero detalla **grados cursados** y **resultados generales** (sin desglosar calificaciones por materia, eso va en boleta).

### 3. Boleta de calificaciones

Documento académico oficial con calificaciones por materia. En México educación básica usa escala 5.0-10.0 conforme acuerdo SEP.

```markdown
# BOLETA DE CALIFICACIONES

[Membretado del colegio]

Ciclo escolar: [ciclo]
Nivel: [preescolar/primaria/secundaria/preparatoria]
Grado: [grado] Grupo: [grupo]

Alumno: [Nombre completo]
CURP: [CURP]
Matrícula: [matrícula]

## Calificaciones por materia

| Asignatura | Bim 1 | Bim 2 | Bim 3 | Bim 4 | Bim 5 | Promedio |
|---|---|---|---|---|---|---|
| Español | 9.5 | 9.0 | 8.5 | 9.5 | 9.0 | 9.1 |
| Matemáticas | 8.0 | 8.5 | 9.0 | 8.5 | 9.0 | 8.6 |
| ... | | | | | | |

**Promedio general**: X.X

## Observaciones del docente

[Texto libre del docente titular]

## Faltas justificadas / injustificadas

Justificadas: X | Injustificadas: Y

ATENTAMENTE

________________________
[Nombre del Director]

[Sello del colegio]

[Fecha]
```

**Reglas para boleta**:
- Educación básica (preescolar a secundaria): escala 5.0-10.0, calificación mínima aprobatoria 6.0.
- Preescolar: calificaciones descriptivas (no numéricas) según planes y programas SEP.
- Bachillerato/preparatoria: puede ser por bimestres, trimestres o semestres según el modelo.
- Promedio: una decimal típicamente.

### 4. Certificado parcial de estudios

Para alumnos que se cambian a otro plantel a media de un ciclo o nivel. Detalla los grados completados con calificaciones promedio.

### 5. Certificado de estudios (final de nivel)

**IMPORTANTE**: el certificado oficial SEP de fin de nivel (primaria, secundaria, prepa) lo emite la **autoridad educativa**, no el colegio. El colegio entrega un documento que el padre tramita en la SEP.

El colegio puede entregar:
- Un certificado interno (con valor solo institucional, no oficial SEP).
- Constancia detallando que el alumno terminó el nivel y va a tramitar el certificado SEP.

## Datos obligatorios para validez

### Del colegio
1. **Razón social completa**: tal cual está registrada ante SEP.
2. **Clave de Centro de Trabajo (CCT)**: 10 caracteres alfanuméricos (ej. 09PPR1234A).
3. **RVOE (Reconocimiento de Validez Oficial de Estudios)**: número de acuerdo y fecha. Sin RVOE actual, los estudios no tienen validez oficial SEP.
4. **Domicilio del colegio**: completo.
5. **Teléfono y correo de contacto**.

### Del alumno
1. **Nombre completo** (apellido paterno, materno, nombre/s — orden tal como aparece en acta de nacimiento).
2. **CURP**: 18 caracteres. Validar estructura.
3. **Matrícula interna del colegio**.
4. **Grado y nivel** que cursa o cursó.
5. **Ciclo escolar** (formato YYYY-YYYY).

### De la firma
1. **Nombre del director/titular** legalmente registrado ante SEP. Si el director cambió a mitad de ciclo, los documentos posteriores llevan al nuevo.
2. **Firma autógrafa o electrónica si tiene FIEL**.
3. **Sello del colegio**.

## Manejo de adeudos

**Lo que el colegio NO puede hacer**:
- Retener documentos de ciclos pasados ya concluidos. La SEP ha emitido pronunciamientos: el adeudo no faculta a retener documentos académicos terminados. Boletas, certificados, constancias de ciclos cerrados se entregan.
- Negar constancia de inscripción del ciclo en curso si el alumno está vigente.

**Lo que el colegio SÍ puede hacer**:
- Condicionar el CFDI al pago (no se factura lo no cobrado).
- Negar re-inscripción al ciclo siguiente si hay adeudo.
- Solicitar liquidación de adeudo para ceremonias / graduación (cláusula del reglamento).

## Salida esperada

Cuando el usuario pida una constancia/boleta:

1. Pregunta o lee datos:
   - Alumno (nombre, CURP, matrícula)
   - Tipo de constancia
   - Ciclo y grado
   - Calificaciones (para boletas)
2. Validar CURP estructuralmente (18 chars, formato AAAA000101HXXAAAA01).
3. Generar documento con membretado del colegio (variables del config).
4. Marcar campos pendientes de firma y sello (no se pueden imprimir desde el skill).
5. Sugerir flujo: imprimir en papel membretado, firmar, sellar, entregar copia al alumno y guardar original en expediente.

## Validaciones automáticas

- CURP estructura válida (regex `^[A-Z]{4}\d{6}[HM][A-Z]{5}[0-9A-Z]\d$`)
- CCT estructura válida (10 chars con formato regional)
- Grado consistente con nivel (1ro-6to primaria, 1ro-3ro secundaria, 1ro-3ro prepa típicamente)
- Calificaciones en rango (5.0-10.0 en básica)
- Si hay materia reprobada (<6.0), agregar nota o asterisco según política del colegio
- Fechas consistentes (no certificar un ciclo que aún no termina)

## Plantilla de membretado

El colegio configura una vez:
```json
{
  "colegio": {
    "razon_social": "string",
    "cct": "string",
    "rvoe": {
      "numero": "string",
      "fecha": "DD/MM/AAAA",
      "nivel": "preescolar | primaria | secundaria | preparatoria"
    },
    "domicilio": {
      "calle": "...",
      "numero": "...",
      "colonia": "...",
      "ciudad": "...",
      "estado": "...",
      "cp": "..."
    },
    "telefono": "string",
    "email": "string",
    "logo_url": "ruta al logo",
    "director": {
      "nombre_completo": "string",
      "cargo": "string"
    }
  }
}
```

Este config se guarda en `config/colegio.json` y se usa por todos los documentos del plugin.

## Integración

- `compliance-lfpdppp`: los documentos contienen datos personales de menores; tratamiento conforme aviso.
- `cfdi-colegiaturas-deducibles`: si la familia regulariza, se emite CFDI antes/después de constancia según política.
