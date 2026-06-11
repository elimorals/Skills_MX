---
name: freelance-tax-mx
description: Calcula obligaciones fiscales mensuales y anuales para freelancers en México bajo regímenes 612 (PFAE — Personas Físicas con Actividades Empresariales y Profesionales) y 626 (RESICO PF — Régimen Simplificado de Confianza). Genera cálculo del pago provisional mensual de ISR considerando ingresos cobrados, gastos deducibles, retenciones a cuenta, y coeficiente o tasa según régimen. Estima declaración anual con deducciones personales (médicos, intereses hipotecarios, colegiaturas, transporte escolar, primas de seguros) aplicando topes vigentes del Art. 151 LISR. Identifica omisiones comunes (retenciones no acreditadas, gastos sin CFDI, depósitos en efectivo > $15,000 MXN/mes). Usar cuando el usuario diga pago provisional, declaración mensual, declaración anual, ISR mensual, RESICO calculo, PFAE calculo, deducciones personales, ahorro fiscal, tax planning México, optimización fiscal freelancer. NO usar para PMs (sus declaraciones son distintas), salarios (régimen 605 con tarifa mensual), ni para impuestos no federales (predial, ISN).
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
- IVA: se traslada al 16%, no hay tratamiento especial.
- Retenciones recibidas (1.25% que les retienen las PMs) son **a cuenta del pago provisional**, se acreditan.

### PFAE (Régimen 612)
- El régimen "tradicional" antes de RESICO.
- Permite deducir gastos relacionados con la actividad.
- Pago provisional: aplicación de la tarifa progresiva del Art. 96 LISR sobre **utilidad fiscal acumulada del ejercicio**.

Tarifa mensual del Art. 96 (vigente, se actualiza por inflación):

| Límite inferior | Límite superior | Cuota fija | % sobre excedente |
|---|---|---|---|
| 0.01 | 8,952.49 | 0.00 | 1.92% |
| 8,952.50 | 75,984.55 | 171.88 | 6.40% |
| 75,984.56 | 133,536.07 | 4,461.94 | 10.88% |
| 133,536.08 | 155,229.80 | 10,723.55 | 16.00% |
| 155,229.81 | 185,852.57 | 14,194.54 | 17.92% |
| 185,852.58 | 374,837.88 | 19,682.13 | 21.36% |
| 374,837.89 | 590,795.99 | 60,049.40 | 23.52% |
| 590,796.00 | 1,127,926.84 | 110,842.74 | 30.00% |
| 1,127,926.85 | 1,503,902.46 | 271,981.99 | 32.00% |
| 1,503,902.47 | 4,511,707.37 | 392,294.17 | 34.00% |
| 4,511,707.38 | en adelante | 1,414,947.85 | 35.00% |

(Verificar tarifa vigente del año fiscal en curso — se actualiza anualmente por inflación.)

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

Cuando las retenciones superan el ISR causado: queda saldo a favor acreditable contra futuros pagos.

## Pago provisional PFAE — flujo

**Datos requeridos**:
- Ingresos acumulados del ejercicio (enero al mes que se declara)
- Gastos deducibles acumulados del ejercicio
- Pagos provisionales ya enterados anteriormente del ejercicio
- Retenciones acumuladas

**Cálculo**:
```
Ingresos acumulados ene-mar:               $300,000
(-) Gastos deducibles ene-mar:             $80,000
(=) Utilidad fiscal acumulada:             $220,000

ISR según tarifa Art. 96 (rango 185,852-374,837):
  Cuota fija:                              $19,682.13
  Excedente: $220,000 - $185,852.57 = $34,147.43
  21.36% del excedente:                    $7,293.89
(=) ISR del ejercicio acumulado:           $26,976.02

(-) Pagos provisionales ya enterados:      $18,000
(-) Retenciones acumuladas del ejercicio:  $6,000
(=) ISR a pagar este mes:                  $2,976.02
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
- Cuotas IMSS si se aporta voluntariamente

**Reglas críticas**:
- Pago en efectivo > $2,000 MXN: NO deducible. SIEMPRE transferencia, cheque, o tarjeta.
- CFDI a tu RFC con dirección fiscal correcta. CFDI a "público en general" no deduce.
- Concepto del CFDI debe corresponder a actividad real. "Servicios profesionales" genérico es señal de alerta SAT.
- Gastos personales mezclados con negocio: solo deduce la parte de negocio. Mantener separación clara.

## Deducciones personales (anual, Art. 151 LISR)

Aplican a **ambos regímenes** (RESICO y PFAE) en la declaración anual:

| Concepto | Tope |
|---|---|
| Honorarios médicos, dentales, hospitalarios (uso D01) | Sin tope individual, pero sí tope global |
| Intereses reales pagados por crédito hipotecario casa habitación | Sin tope específico (sí global) |
| Aportaciones voluntarias SAR | Sin tope específico (sí global) |
| Primas seguros gastos médicos | Sin tope específico (sí global) |
| Transportación escolar obligatoria | Sin tope específico (sí global) |
| Donativos a donatarias autorizadas | Máx 7% de ingresos acumulados año previo |
| Colegiaturas (preescolar a media superior, no universidad) | Varios topes por nivel: preescolar $14,200, primaria $12,900, secundaria $19,900, prep tec $17,100, prep general $24,500 (verificar vigente) |

**TOPE GLOBAL** (Art. 151 último párrafo): el total de deducciones personales no puede exceder **el menor entre**:
- 5 UMAs anuales (~$200,000-250,000 MXN según UMA vigente)
- 15% del ingreso del contribuyente

**Forma de pago de deducción personal**: efectivo NO califica. Solo transferencia, cheque nominativo, tarjeta de crédito/débito/servicio (excepto honorarios médicos veterinarios que sí aceptan otras formas).

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

1. **Depósitos en efectivo > $15,000 MXN/mes en cuentas bancarias del contribuyente**: el banco reporta al SAT (Art. 32 Ley del IVA + circular). Genera discrepancia con ingresos facturados.
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
- Multa SAT por pago insuficiente (8% del omitido más recargos)
- Discrepancia fiscal con consecuencias mayores
- Sanción profesional al contador firmante (si aplica)

**Datos que DEBES verificar antes de cualquier uso real**:

1. **Tarifa Art. 96 LISR** (los 11 rangos con cuota fija y % sobre excedente): se actualiza **anualmente** por inflación. Los valores citados en este skill ($8,952.49, $75,984.55, etc.) **probablemente están desactualizados**. Descargar la tarifa vigente del portal SAT del ejercicio fiscal en curso.

2. **Tasas RESICO PF** (1.0, 1.1, 1.5, 2.0, 2.5%): validar contra RMF vigente.

3. **Topes de deducción personal Art. 151 LISR**:
   - Tope global: el menor entre 5 UMAs anuales y 15% del ingreso. La UMA se actualiza anualmente.
   - Topes específicos de colegiaturas (preescolar $14,200, primaria $12,900, secundaria $19,900, prepa técnica $17,100, prepa general $24,500): **valores históricos**. Verificar vigentes.

4. **Forma de pago para deducción**: efectivo NO califica para deducciones personales (excepto algunos casos). Verificar excepciones vigentes.

5. **Coeficiente de utilidad PFAE**: el cálculo del pago provisional PFAE usa el coeficiente del ejercicio anterior. El skill no calcula automáticamente este coeficiente — debe proveerse.

6. **Tope para depósitos en efectivo reportables** ($15,000 MXN/mes): verificar circular vigente.

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
