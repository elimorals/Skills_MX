# Brief para contador certificado — validación `freelance-tax-mx` + `pf-anual-mx`

**Fecha**: 2026-06-12
**Esfuerzo estimado**: 4-6 horas de consultoría ($3-8k MXN según tarifa).
**Entregables**: tabla de respuestas + cualquier corrección suelta.

---

## 0. Contexto en 2 párrafos

Plugins-mx es un monorepo de software para automatizar operación fiscal de PyMEs y freelancers en México. Tiene dos skills directamente expuestos al riesgo regulatorio que **necesitan validación de un contador** antes de exponerlos a cualquier usuario externo:

1. **`freelance-tax-mx`** — calcula pago provisional mensual ISR para PFAE (régimen 612) y RESICO PF (régimen 626).
2. **`pf-anual-mx`** — workflow completo de declaración anual personal (recopilar CFDIs + identificar deducciones personales + calcular ISR anual + comparar contra retenciones).

Estos skills usan tarifas y reglas que **podemos haber capturado desactualizadas**. La RMF 2026, los topes del Art. 151 LISR y las tasas RESICO se actualizan periódicamente. Sin validación, hay riesgo de generar cálculos que dejen al usuario con diferencias y multas SAT.

---

## 1. Archivos a auditar (paths exactos)

| Archivo | Qué revisar |
|---|---|
| `freelancers-mx/skills/freelance-tax-mx/SKILL.md` | Tarifa Art. 96 LISR, tasas RESICO PF, lógica de pago provisional |
| `_shared/iva-retenciones-mx/SKILL.md` + `references/` | Matriz de retenciones por escenario, IVA traslado/acreditamiento |
| `pf-anual-mx/skills/calculadora-isr-anual/SKILL.md` | Cálculo ISR anual, aplicación de tarifa anual Art. 152 |
| `pf-anual-mx/skills/identificar-deducciones-personales/SKILL.md` | Deducciones personales Art. 151 LISR + topes |
| `pf-anual-mx/skills/generar-borrador-declaracion/SKILL.md` | Formato y campos esperados por SAT |
| `pf-anual-mx/skills/cruzar-bancos-vs-cfdis/SKILL.md` | Lógica de detección de discrepancias |

---

## 2. Preguntas específicas (las "killer questions" para la consultoría)

### 2.1 Tarifa Art. 96 LISR (PFAE — pago provisional mensual)

El skill `freelance-tax-mx` usa esta tarifa (vigencia esperada 2026):

| Límite inferior | Límite superior | Cuota fija | % sobre excedente |
|---|---|---|---|
| 0.01 | 8,952.49 | 0.00 | 1.92% |
| 8,952.50 | 75,984.55 | 171.88 | 6.40% |
| 75,984.56 | 133,536.07 | 4,461.94 | 10.88% |
| 133,536.08 | 155,229.80 | 10,723.55 | 16.00% |
| 155,229.81 | 185,852.57 | 14,194.54 | 17.92% |
| 185,852.58 | 374,837.88 | 19,682.13 | 21.36% |
| 374,837.89 | 590,795.99 | 60,049.40 | 23.52% |

**Pregunta**: ¿Estos valores son los vigentes para 2026? Si no, dime los correctos y la fuente oficial (RMF, DOF).

### 2.2 Tasas RESICO PF (régimen 626) — pago provisional mensual

El skill usa:

| Rango ingresos cobrados/mes | Tasa |
|---|---|
| Hasta $25,000 | 1.00% |
| Hasta $50,000 | 1.10% |
| Hasta $83,333 | 1.50% |
| Hasta $208,333 | 2.00% |
| Hasta $3,500,000 (tope anual) | 2.50% |

**Preguntas**:
1. ¿Estos rangos y tasas son los vigentes 2026?
2. ¿El tope anual sigue siendo $3.5M MXN o cambió?
3. ¿La retención que las PMs hacen a contribuyentes RESICO sigue siendo 1.25%?
4. Para acreditamiento: ¿La retención recibida se acredita 100% contra el pago provisional del mes, o hay algún tope?

### 2.3 Topes deducciones personales Art. 151 LISR (anual)

El skill `identificar-deducciones-personales` necesita confirmar:

| Concepto | Tope que usa el skill | ¿Vigente? |
|---|---|---|
| Honorarios médicos/dentales/hospitalarios | Sin tope individual, pero sujeto al tope global | (a confirmar) |
| Gastos funerarios | 1 UMA anual | |
| Donativos | 7% ingresos acumulables ejercicio previo | |
| Aportaciones voluntarias SAR/AFORE | 10% ingresos acumulables, sin exceder 5 UMA anual | |
| Primas de seguros gastos médicos | Sin tope individual | |
| Transporte escolar obligatorio | Sin tope individual (debe ser obligatorio por escuela) | |
| Intereses hipotecarios reales | Casa habitación, crédito ≤ $750k UDIs | |
| Colegiaturas (Decreto facilidad) | Por nivel educativo | |
| **Tope GLOBAL** | 5 UMA anual o 15% ingresos, lo menor | |

**Pregunta**: ¿Confirmas todos los topes vigentes 2026? Especialmente el tope global, que ha cambiado varias veces.

### 2.4 Tope colegiaturas por nivel (Decreto facilidad)

| Nivel | Tope anual MXN |
|---|---|
| Preescolar | $14,200 |
| Primaria | $12,900 |
| Secundaria | $19,900 |
| Profesional técnico | $17,100 |
| Bachillerato / equivalente | $24,500 |
| Universidad/posgrado | **NO deducible** (no incluida en decreto) |

**Pregunta**: ¿Vigentes 2026? El decreto se publica cada cierto tiempo; si ya hay actualización, indícamela.

### 2.5 Deducción intereses hipotecarios reales

Skill calcula: `intereses_reales = intereses_nominales − ajuste_inflacionario`.

**Pregunta**: ¿La fórmula INPC para calcular el ajuste inflacionario sigue siendo la del Art. 159 LISR? ¿Hay matiz operativo (qué INPC usar — mensual o anual)?

### 2.6 Alertas críticas (depósitos > $15k)

El skill alerta cuando hay depósitos en efectivo > $15,000 MXN/mes (discrepancia ISR).

**Preguntas**:
1. ¿Sigue siendo $15,000 el umbral del Art. 81 fracc. IV CFF (instituciones financieras informan)?
2. ¿La obligación del freelancer cuando esto pasa es informar al SAT? ¿En qué forma?

### 2.7 Cancelación de CFDIs (motivos 01-04)

El skill `cfdi-emision` documenta los motivos:
- 01 = Comprobantes emitidos con errores con relación
- 02 = Comprobantes emitidos con errores sin relación
- 03 = No se llevó a cabo la operación
- 04 = Operación nominativa relacionada en una factura global

**Pregunta**: ¿Los plazos para cancelar CFDIs (regla de RMF) siguen siendo:
- En el mismo ejercicio fiscal sin solicitar autorización del receptor
- Después: requiere aceptación del receptor en 72h?

¿Hay cambio en RMF 2026 sobre esto?

### 2.8 Buzón Tributario y obligaciones

**Pregunta**: ¿Sigue siendo obligatorio el Buzón Tributario activo para PF con actividad económica? ¿Multas vigentes por no tenerlo?

---

## 3. Casos de prueba para validar (opcional pero ideal)

Si tienes 1 hora extra, te entrego 3 casos de prueba con datos sintéticos y nos das el cálculo que tú harías. Comparamos contra el skill.

**Caso 1 (RESICO PF)**:
- Ingresos cobrados marzo 2026: $45,000 MXN
- Retención recibida (PM cliente, 1.25%): $562.50
- ¿Cuánto es el pago provisional ISR marzo?

**Caso 2 (PFAE)**:
- Ingresos acumulados ene-mar 2026: $180,000 MXN
- Gastos deducibles ene-mar: $40,000 MXN
- Pagos provisionales ene-feb: $5,200 MXN acumulado
- ¿Cuánto es el pago provisional marzo?

**Caso 3 (anual PFAE 2026)**:
- Ingresos acumulables: $850,000 MXN
- Gastos deducibles: $180,000 MXN
- Deducciones personales: médicos $35k, colegiatura primaria $12,900, SAR $40k
- Retenciones acreditables: $58,000 MXN
- Pagos provisionales: $42,000 MXN
- ¿Cuánto debe pagar/recuperar en anual?

---

## 4. Formato de respuesta esperado

Idealmente:
- **Tabla con las preguntas y "✅ correcto / ❌ valor real es X / ⚠ matiz: Y"**.
- **Cualquier observación suelta** sobre prácticas que veas mal en los SKILL.md (ej. "la regla de redondeo de pesos cambió", "el cruce bancos vs CFDIs debería considerar Z").
- **Si los casos de prueba dan distinto al skill**: el detalle de tu cálculo para ajustar.

---

## 5. Honorarios y entrega

- **Honorarios estimados**: $3,000-$8,000 MXN según tu tarifa y profundidad.
- **Entrega**: PDF o email con la tabla de respuestas.
- **Plazo solicitado**: 2 semanas (antes de Sem 4 del plan = 2026-07-10).

---

## 6. Qué sigue después de tu validación

1. Aplico tus correcciones a los SKILL.md (estimo 1 día).
2. Marco vigencia validada con fecha + tu firma digital en frontmatter del skill.
3. Genero fixtures de prueba con tus casos de validación.
4. Empezamos dogfooding con declaración personal real.
5. Te invitamos a revisión semestral del skill (servicio recurrente $X/semestre si te interesa).

---

## 7. Datos del proyecto

- **Repositorio**: `/Users/elias/Documents/Trabajo/skills/`
- **Documentos de contexto** (te puedo enviar PDF):
  - `docs/analisis-profundo-2026-06.md` — visión general
  - `docs/estado-real.md` — auditoría honesta de riesgo
  - `docs/specs/05-vertical-pf-anual-mx.md` — spec del vertical anual
- **Contacto**: Elías Rashid Morales Mendoza — elimoralsmendox@gmail.com

---

## Anexo — Acceso al código (opcional)

Si prefieres leer el código directamente:

```bash
# 1. Clonar (privado — te paso credenciales si lo necesitas)
git clone <url-privada>
cd Skills_MX

# 2. Abrir los SKILL.md relevantes
cat freelancers-mx/skills/freelance-tax-mx/SKILL.md
cat _shared/iva-retenciones-mx/SKILL.md
cat _shared/iva-retenciones-mx/references/*
cat pf-anual-mx/skills/*/SKILL.md
```

No necesitas correr código; los SKILL.md son markdown.
