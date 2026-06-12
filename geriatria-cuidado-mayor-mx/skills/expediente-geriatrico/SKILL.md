---
name: expediente-geriatrico
description: Crea y mantiene expediente clínico-funcional integral del adulto mayor cumpliendo NOM-167-SSA1 (asistencia social) y NOM-031-SSA3 (residencias) con datos identificación + diagnósticos crónicos múltiples (polipatología típica: diabetes 2 + hipertensión + osteoartritis + déficit cognitivo), Escala de Actividades Básicas de la Vida Diaria (Barthel/Katz) para medir dependencia funcional, Escala de Lawton-Brody para actividades instrumentales, Mini-Mental State Examination (MMSE) o test de Pfeiffer para tamizaje cognitivo, riesgo de caídas (Tinetti o Timed Up and Go), evaluación nutricional MNA, medicamentos crónicos con interacciones detectadas (polifarmacia > 5 fármacos genera 25% riesgo de interacción adversa), red de cuidadores (familiares + profesionales) con contactos jerarquizados, voluntad anticipada si la firmó cuando capaz, poder notarial cuando ya no tiene capacidad jurídica. Usar cuando el usuario diga "expediente adulto mayor", "expediente abuelita", "ficha geriátrica", "alta residente", "ingreso a residencia". NO usar para expediente médico general (usar expediente-clinico-nom004) ni para registro civil.
allowed-tools: Read, Write, Edit
---

# Expediente geriátrico integral

## Componentes obligatorios NOM-167 / NOM-031

1. **Identificación**: nombre, CURP, fecha nacimiento, edad cronológica
2. **Diagnósticos crónicos** (típico polipatología): lista con CIE-10
3. **Escalas funcionales**:
   - Barthel (ABVD): 0-100 (0=total dependencia, 100=independiente)
   - Lawton-Brody (AIVD): 0-8 mujeres / 0-5 hombres
   - MMSE: ≥24 normal, 18-23 deterioro leve, <18 demencia
   - Tinetti / Timed Up and Go: riesgo caídas
   - MNA: estado nutricional
4. **Polifarmacia**: lista con interacciones detectadas
5. **Red de cuidadores**: jerarquía + contactos
6. **Voluntad anticipada** o **poder notarial**
7. **Datos de contacto en emergencia**

## Validaciones críticas

- Si MMSE < 18: marcar capacidad jurídica DUDOSA → verificar poder notarial
- Si polifarmacia > 5 fármacos: alerta de revisión médica
- Si Barthel < 60: dependencia moderada → ajustar plan de cuidados
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
