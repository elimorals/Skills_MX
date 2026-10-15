---
name: expediente-geriatrico
description: Crea y mantiene el expediente clínico-funcional integral del adulto mayor (persona de 60+ según la Ley de los Derechos de las Personas Adultas Mayores) alineado a la NOM-031-SSA3-2012 (asistencia social a adultos mayores en establecimientos y residencias) y a la NOM-004-SSA3-2012 (expediente clínico): identificación, diagnósticos crónicos con CIE-10, escalas Barthel/Katz (actividades básicas), Lawton-Brody (instrumentales), MMSE o Pfeiffer (tamizaje cognitivo), Tinetti o Timed Up and Go (caídas), MNA (nutrición), polifarmacia con interacciones, red de cuidadores, voluntad anticipada y designación de apoyos o representante. Usar cuando el usuario diga "expediente adulto mayor", "expediente abuelita", "ficha geriátrica", "valoración geriátrica", "alta residente", "ingreso a residencia", "asilo", "casa de día". NO usar para expediente médico general (usar consultorio-especialista-mx:expediente-clinico-nom004) ni para registro civil.
allowed-tools: Read, Write, Edit
---

# Expediente geriátrico integral

## Componentes (NOM-031-SSA3-2012 + NOM-004-SSA3-2012)

La NOM-031-SSA3-2012 (DOF 13-09-2012) regula a los establecimientos de asistencia social para adultos mayores; el contenido clínico del expediente sigue la NOM-004-SSA3-2012. La NOM-167-SSA1-1997 es la norma anterior: verificar si sigue citándose en tu entidad. Las escalas son buena práctica geriátrica, no exigencia literal de la NOM.

1. **Identificación**: nombre, CURP, fecha nacimiento, edad cronológica
2. **Diagnósticos crónicos** (típico polipatología): lista con CIE-10
3. **Escalas funcionales**:
   - Barthel (ABVD): 0-100 (0=total dependencia, 100=independiente)
   - Lawton-Brody (AIVD): 0-8 mujeres / 0-5 hombres
   - MMSE: ≥24 normal, 18-23 posible deterioro leve, <18 deterioro importante (tamizaje, ajustar por escolaridad; no diagnostica demencia)
   - Tinetti / Timed Up and Go: riesgo caídas
   - MNA: estado nutricional
4. **Polifarmacia**: lista con interacciones detectadas
5. **Red de cuidadores**: jerarquía + contactos
6. **Voluntad anticipada** (ley estatal; p. ej. Ley de Voluntad Anticipada CDMX) y **designación de apoyos o representante** otorgada mientras tiene capacidad
7. **Datos de contacto en emergencia**

## Validaciones críticas

- Si MMSE < 18: el tamizaje no determina capacidad jurídica. Marcar "requiere valoración" y revisar si existen voluntad anticipada o designación de apoyos. Un poder notarial puede quedar en duda si el otorgante pierde capacidad; desde el Código Nacional de Procedimientos Civiles y Familiares (DOF 07-06-2023) la interdicción se sustituye por un sistema de apoyos (confianza media, consultar notario o abogado familiar)
- Si polifarmacia ≥ 5 fármacos: alerta de revisión médica (revisar con criterios Beers/STOPP)
- Si Barthel < 60: dependencia moderada o mayor → ajustar plan de cuidados
- Si vive solo + Barthel < 80: riesgo alto, recomendar acompañante

## Output

```
residentes/<curp-hash>/
  ├── expediente.json
  ├── escalas-funcionales/
  ├── medicamentos.json (link a tracking-medicamentos-vencimiento)
  ├── plan-de-cuidados.md
  └── red-familiar.json
```

> Herramienta de organización. Las escalas las aplica y firma personal de salud capacitado; la skill no diagnostica.
> Derechos de la persona adulta mayor (salud, trato digno, no discriminación, decidir sobre su cuidado): Ley de los Derechos de las Personas Adultas Mayores, Art. 5. Quejas por maltrato: INAPAM / DIF / fiscalía local.
