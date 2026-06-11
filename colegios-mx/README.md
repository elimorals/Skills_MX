# colegios-mx

Plugin para colegios, kinders y escuelas privadas operando en México.

## Skills propios

| Skill | Propósito |
|---|---|
| `cobranza-colegiaturas` | Flujo escalado de cobranza con tono apropiado para padres de familia |
| `comunicacion-padres-wa` | Templates de WhatsApp Business para avisos masivos sin saturar |
| `constancias-academicas` | Constancia de estudios, boleta, certificados según SEP |
| `cfdi-colegiaturas-deducibles` | CFDI con uso D10 cumpliendo requisitos Art. 151 LISR |

## Skills heredados de `core-mexico`

CFDI, IVA, RFC, WhatsApp Business, LFPDPPP, MXN.

## Commands

- `/colegios:cobranza [familia]`
- `/colegios:aviso-padres [tipo] [grupo]`
- `/colegios:constancia [alumno]`
- `/colegios:facturar-colegiatura [familia] [mes]`

## Usuario objetivo

- Director administrativo de colegio K-12 (50-1500 alumnos)
- Dueña/dueño de kinder o escuela pequeña
- Equipo administrativo de 2-8 personas

## Filosofía

Bajar **cartera vencida del 18% promedio nacional al 8%** vía cobranza profesional y oportuna. Liberar **10-15 horas/semana** de la administradora del comunicación operativa con padres.

## Estado

`v0.1.0` — scaffolding inicial. Requiere partner del sector educativo para validación.

## Compliance crítico

- **NOM-024** para expediente clínico si hay servicio médico escolar
- **LFPDPPP** con énfasis en menores: tratar datos de alumnos con consentimiento de padres/tutores
- **Datos sensibles** (salud del alumno, situación familiar): protección reforzada
- **SEP/CCT**: constancias y boletas con formato y datos oficiales
