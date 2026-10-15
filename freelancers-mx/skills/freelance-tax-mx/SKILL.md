---
name: freelance-tax-mx
description: Calcula obligaciones fiscales mensuales y anuales para freelancers en México bajo regímenes 612 (PFAE — Personas Físicas con Actividades Empresariales y Profesionales) y 626 (RESICO PF — Régimen Simplificado de Confianza). Genera cálculo del pago provisional mensual de ISR considerando ingresos cobrados, gastos deducibles, retenciones a cuenta, y coeficiente o tasa según régimen. Estima la declaración anual (en 612, con deducciones personales del Art. 151 LISR y su tope; en RESICO PF sin deducciones). Identifica omisiones comunes (retenciones no acreditadas, gastos sin CFDI, depósitos en efectivo > $15,000 MXN/mes que el banco informa). Usar cuando el usuario diga pago provisional, declaración mensual, declaración anual, ISR mensual, RESICO calculo, PFAE calculo, deducciones personales, ahorro fiscal, tax planning México, optimización fiscal freelancer. NO usar para PMs (sus declaraciones son distintas), salarios (régimen 605 con tarifa mensual), ni para impuestos no federales (predial, ISN).
allowed-tools: Read, Write, Edit
---

# Pago provisional y declaración anual — freelancer MX

Skill que evita el dolor del cierre mensual. El freelancer mexicano típico:
- Pierde 4-6 horas/mes en captura de gastos y cálculo de pago provisional
- Comete errores del 5-15% en retenciones acreditables porque no las lleva bien
- Olvida deducciones personales en anual por no organizar CFDIs deducibles durante el año

Este skill resuelve los tres.

## Regímenes cubiertos

### RESICO PF (Régimen 626 Persona Física)
- Vigente desde 2022, **el más relevante hoy** para freelancers que facturan hasta $3.5M MXN/año.
- Tasa ISR sobre **ingresos cobrados** (no devengados — base flujo).
- Tarifa mensual progresiva:

| Rango ingresos cobrados/mes | Tasa |
|---|---|
| Hasta $25,000 | 1.00% |
| Hasta $50,000 | 1.10% |
| Hasta $83,333 | 1.50% |
| Hasta $208,333 | 2.00% |
| Hasta $3,500,000 (anual) | 2.50% |

- **Sin gastos deducibles**: el régimen es simplificado, paga sobre el ingreso bruto cobrado.
- IVA: se traslada al 16% y se declara mensual. Si el cliente es PM, retiene 2/3 del IVA (10.6667% del valor) además del ISR.
- Retenciones recibidas (1.25% de ISR que retienen las PM, Art. 113-J) se acreditan contra el pago mensual.
- **No aplica deducciones personales** del Art. 151 en la anual.

### PFAE (Régimen 612)
- El régimen "tradicional" antes de RESICO.
- Permite deducir gastos relacionados con la actividad.
- Pago provisional (Art. 106): tarifa del Art. 96 **acumulada al mes** sobre la utilidad fiscal acumulada del ejercicio. El Anexo 8 RMF publica una tabla por mes (equivale a la mensual × número de meses).
- Si el cliente es PM: retiene 10% de ISR y 2/3 del IVA.

Tarifa mensual Art. 96 LISR **2026** (Anexo 8 RMF 2026, DOF 28-12-2025; actualizada por inflación > 10%):

| Límite inferior | Límite superior | Cuota fija | % sobre excedente |
|---|---|---|---|
| 0.01 | 844.59 | 0.00 | 1.92% |
| 844.60 | 7,168.51 | 16.22 | 6.40% |
| 7,168.52 | 12,598.02 | 420.95 | 10.88% |
| 12,598.03 | 14,644.64 | 1,011.68 | 16.00% |
| 14,644.65 | 17,533.64 | 1,339.14 | 17.92% |
| 17,533.65 | 35,362.83 | 1,856.84 | 21.36% |
| 35,362.84 | 55,736.68 | 5,665.16 | 23.52% |
| 55,736.69 | 106,410.50 | 10,457.09 | 30.00% |
| 106,410.51 | 141,880.66 | 25,659.23 | 32.00% |
| 141,880.67 | 425,641.99 | 37,009.69 | 34.00% |
| 425,642.00 | en adelante | 133,488.54 | 35.00% |

Pagos de 2025 (y su complementaria) usan la tarifa 2025 (primer renglón 0.01–746.04). La tarifa **anual** para la declaración está en `pf-anual-mx/skills/calculadora-isr-anual`.

## Pago provisional RESICO PF — flujo

**Datos requeridos**:
- Ingresos cobrados del mes (base flujo, no devengado)
- Retenciones que le hicieron (CFDIs con retención 1.25% ISR)

**Cálculo**:
```
Ingresos cobrados del mes:           $80,000
Tasa según rango (hasta $83,333):    1.50%
ISR causado del mes:                 $1,200
Retenciones acreditables:           −$1,000
ISR a pagar al SAT:                  $200
```

Cuando las retenciones superan el ISR causado del mes: el pago del mes queda en cero; el excedente se refleja en la declaración anual RESICO (Art. 113-F), donde se acreditan pagos y retenciones del año (confirmar con contador si procede compensarlo antes).

## Pago provisional PFAE — flujo

**Datos requeridos**:
- Ingresos acumulados del ejercicio (enero al mes que se declara)
- Gastos deducibles acumulados del ejercicio
- Pagos provisionales ya enterados anteriormente del ejercicio
- Retenciones acumuladas

**Cálculo**:
```
Ingresos acumulados ene-mar 2026:          $300,000
(-) Gastos deducibles ene-mar:             $80,000
(=) Utilidad fiscal acumulada:             $220,000

Tarifa de marzo 2026 (Anexo 8; renglón 167,210.05 – 319,231.50):
  Cuota fija:                              $31,371.27
  Excedente: $220,000 - $167,210.05 = $52,789.95
  30% del excedente:                       $15,836.99
(=) ISR del ejercicio acumulado:           $47,208.26

(-) Pagos provisionales ya enterados:      $25,000.00
(-) Retenciones acumuladas del ejercicio:  $6,000.00
(=) ISR a pagar este mes:                  $16,208.26
```

## Gastos deducibles típicos para PFAE

- Renta de oficina o coworking (con CFDI a tu RFC)
- Internet, teléfono móvil (proporcional al uso para negocio)
- Equipo de cómputo y periféricos
- Software / SaaS (con CFDI o factura de exportación)
- Cursos y capacitación profesional
- Viáticos (transporte, hospedaje, alimentos en viajes de trabajo)
- Honorarios de contador, abogado, asesor
- Servicios de diseño/marketing/freelancers contratados
- Suministros de oficina
- Cuotas IMSS propias como trabajador independiente: deducibilidad **verificar con contador**

**Reglas críticas**:
- Pago en efectivo > $2,000 MXN: NO deducible (Art. 27 fr. III LISR); combustible nunca en efectivo. SIEMPRE transferencia, cheque o tarjeta.
- CFDI a tu RFC con dirección fiscal correcta. CFDI a "público en general" no deduce.
- Concepto del CFDI debe corresponder a actividad real. "Servicios profesionales" genérico es señal de alerta SAT.
- Gastos personales mezclados con negocio: solo deduce la parte de negocio. Mantener separación clara.

## Deducciones personales (anual, Art. 151 LISR)

Aplican en la anual de **PFAE 612** (y sueldos). **RESICO PF no aplica deducciones personales.**

| Concepto | Tope |
|---|---|
| Honorarios médicos, dentales, psicología, nutrición, hospitalarios (D01) | Dentro del tope global |
| Gastos funerales (D03) | 1 UMA anual, dentro del tope global |
| Intereses reales hipotecarios casa habitación (D05) | Dentro del tope global (crédito ≤ 750,000 UDIS) |
| Primas de seguros de gastos médicos (D07) | Dentro del tope global |
| Transportación escolar obligatoria (D08) | Dentro del tope global |
| Donativos a donatarias autorizadas (D04) | Máx. 7% de ingresos acumulables del año previo, y dentro del tope global |
| Aportaciones voluntarias/complementarias al retiro (D06) | **Fuera** del tope global: 10% de ingresos acumulables, máx. 5 UMA anuales |
| Colegiaturas (D10, preescolar a bachillerato) | **Fuera** del tope global (Decreto DOF 26-12-2013): preescolar $14,200, primaria $12,900, secundaria $19,900, profesional técnico $17,100, bachillerato $24,500 por alumno |

**TOPE GLOBAL** (Art. 151 último párrafo): el menor entre:
- 5 UMA anuales: $206,480.50 (ejercicio 2025, UMA $113.14) / $214,090.75 (ejercicio 2026, UMA $117.31)
- 15% del total de ingresos del contribuyente (incluidos exentos)

**Forma de pago**: efectivo NO califica. Transferencia, cheque nominativo, tarjeta de crédito/débito/servicios. Detalle completo: `pf-anual-mx/skills/identificar-deducciones-personales`.

## Salida esperada — Pago provisional mensual

```markdown
# Pago provisional — [Mes] [Año]

**Régimen**: RESICO PF (626) | PFAE (612)
**Contribuyente**: [Nombre] / RFC [RFC]

## Ingresos del mes
- Total cobrado en el mes: $XX,XXX MXN
- Número de CFDIs emitidos: N
- Ingresos por moneda extranjera convertidos al TC DOF promedio del mes: $XX,XXX MXN

## Retenciones recibidas en el mes
- ISR: $X,XXX (de N CFDIs)
- IVA: $X,XXX (si PFAE)

## Cálculo de ISR
[Detalle paso a paso del cálculo según régimen]

## ISR a pagar al SAT
$X,XXX MXN

## Plazo límite
17 del mes siguiente (o día hábil siguiente si cae fin de semana/festivo).

## Mecanismo de pago
DPC (Declaración y Pago de Contribuciones) en sat.gob.mx con FIEL o contraseña.

## Alertas detectadas
[Si las hay: ej. "Pago en efectivo de $X detectado en CFDI deducido — verificar para evitar rechazo SAT"]
```

## Estimación anual (proyección durante el año)

A medio año o cualquier mes, el skill puede proyectar:

```
Ingresos proyectados año completo: $X,XXX,XXX
ISR estimado año (RESICO): $XX,XXX
ISR ya pagado al mes M: $XX,XXX
ISR pendiente de pagar (mensuales restantes + anual): $XX,XXX

Deducciones personales acumuladas en CFDIs detectados: $XX,XXX
Saldo a favor proyectado en anual: $XX,XXX
```

Útil para planeación financiera: si proyectas saldo a favor grande, sabes que recuperas en abril/mayo.

## Alertas que el skill debe detectar automáticamente

1. **Depósitos en efectivo > $15,000 MXN/mes en cuentas bancarias del contribuyente**: el banco los informa al SAT (Art. 55 fr. IV LISR). Pueden generar discrepancia con ingresos facturados.
2. **Retenciones no acreditadas**: hay CFDIs recibidos con retenciones que no se están aplicando en pagos provisionales (dinero perdido).
3. **Gastos deducidos sin CFDI**: ningún gasto sin CFDI a tu RFC.
4. **Forma de pago efectivo en deducciones**: no procede.
5. **Cliente RESICO PF que no fue retenido por PM**: el cliente PM tiene obligación; puede ser tema cuando audite el SAT al cliente.
6. **Cambio significativo de patrón**: caída/aumento del 50%+ vs promedio histórico — bandera para revisar manualmente.

## Estructura de datos esperada

El skill consume:
- CSV/JSON con CFDIs emitidos del mes (descargados del SAT o del PAC)
- CSV/JSON con CFDIs recibidos del mes (gastos)
- Estado de cuenta bancario (opcional, para conciliar y detectar depósitos en efectivo)
- Histórico de pagos provisionales anteriores del ejercicio

Si el usuario no tiene estos en formato estructurado, el skill ayuda a estructurarlos preguntando.

## Reservas legales

Este skill **no sustituye contador certificado**. Para:
- Operaciones internacionales complejas
- Ingresos mixtos (salarios + actividades profesionales)
- Cambio de régimen
- Situaciones de discrepancia fiscal o citatorios SAT

Derivar a contador. El skill da una base sólida; el contador valida y firma.

## ⚠ Riesgo regulatorio CRÍTICO — verificación vigente obligatoria

Este es el skill con **mayor riesgo regulatorio del monorepo**. Un cálculo incorrecto puede generar:
- Actualización, recargos y multa de 55% a 75% del impuesto omitido (Art. 76 CFF)
- Discrepancia fiscal con consecuencias mayores
- Sanción profesional al contador firmante (si aplica)

**Datos que DEBES verificar antes de cualquier uso real**:

1. **Tarifa Art. 96 LISR**: verificada contra Anexo 8 RMF 2026 (DOF 28-12-2025). Se actualiza solo cuando la inflación acumulada supera 10% (Art. 152); confirmar el Anexo 8 de cada año.

2. **Tasas RESICO PF** (1.0, 1.1, 1.5, 2.0, 2.5%): están en el Art. 113-E LISR (no en la RMF); texto vigente verificado (última reforma LISR DOF 01-04-2024).

3. **Topes de deducción personal Art. 151 LISR**:
   - Tope global: el menor entre 5 UMAs anuales y 15% del ingreso. La UMA se actualiza anualmente.
   - Topes de colegiaturas: Decreto DOF 26-12-2013, montos sin cambio desde entonces.

4. **Forma de pago para deducción**: efectivo NO califica.

5. **Coeficiente de utilidad**: NO aplica a personas físicas 612 (es de personas morales). El pago provisional PFAE es utilidad acumulada × tarifa acumulada (Art. 106).

6. **Depósitos en efectivo informados por bancos** ($15,000 MXN/mes): Art. 55 fr. IV LISR.

7. **Plazo del pago provisional** (día 17 del mes siguiente): estable pero confirmar que no cambió en el ejercicio.

**Antes de exponer a cliente**:
- Validar al menos UN pago provisional contra cálculo manual de contador certificado.
- Hacerlo con un caso real con datos verificables.
- Documentar la discrepancia (si la hay) y ajustar el skill.
- Después de 3 cálculos seguidos sin discrepancia, considerar el skill apto para asistencia (siempre con disclaimer al usuario final de que el contador valida).

## Integración

- `cfdi-emision`: para entender el flujo del CFDI.
- `iva-retenciones-mx`: para verificar retenciones aplicadas en CFDIs.
- `rfc-validacion`: validar contribuyente.
- En el futuro, integración con API descarga masiva del SAT para automatizar input.
