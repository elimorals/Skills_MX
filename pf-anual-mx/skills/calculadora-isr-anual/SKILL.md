---
name: calculadora-isr-anual
description: Calcula el ISR de la declaración anual de una persona física en México. Para sueldos (605) y actividad empresarial/profesional (612) aplica la tarifa anual del Art. 152 LISR (Anexo 8 RMF) sobre la base tras deducciones autorizadas y personales; para RESICO PF (626) aplica la tabla anual del Art. 113-F sin deducciones. Compara contra pagos provisionales y retenciones para obtener saldo a pagar o a favor. Ejercicio 2025 (se presenta en abril 2026) y ejercicio 2026 (abril 2027). Usar cuando el usuario diga calcula mi ISR anual, cuánto pago en la anual, cuánto me devuelven, simula mi declaración, saldo a favor, cálculo final del año. NO usar para pago provisional mensual (eso es cierre-fiscal-mensual del core).
allowed-tools: Read, Write
---

# Calculadora ISR anual — PF México

## Trigger

- "calcula mi ISR anual"
- "¿cuánto pago / cuánto me devuelven?"
- "dame el cálculo final del año"
- "simula mi declaración"

## Inputs requeridos

Idealmente vienen de skills previos del workflow:

- `regimen` ∈ {PFAE_612, RESICO_PF_626, SALARIOS_605, SALARIOS_605_MAS_612}
- `ejercicio` (int, ej. 2025)
- `ingresos_acumulables_mxn` (de `recopilar-cfdis-anuales`)
- `deducciones_autorizadas_mxn` (gastos de la actividad, solo 612)
- `deducciones_personales_aplicables_mxn` (de `identificar-deducciones-personales`, ya topadas)
- `pagos_provisionales_acumulados_mxn` (del tracker `cierre-fiscal-mensual`)
- `isr_retenido_acumulado_mxn` (retenciones de salarios, de PM por honorarios, de plataformas, de intereses)

## Tarifa anual Art. 152 LISR (fuente: Anexo 8 RMF 2026, DOF 28-12-2025, apartado C)

La tarifa se actualizó para 2026 porque la inflación acumulada superó 10% (Art. 152, último párrafo). **El ejercicio 2025 usa la tabla 2025; el ejercicio 2026 usa la tabla 2026.** No multipliques la tarifa mensual del Art. 96 × 12: usa la anual publicada.

| Límite inferior 2025 | Cuota fija 2025 | Límite inferior 2026 | Cuota fija 2026 | % sobre excedente |
|---:|---:|---:|---:|---:|
| 0.01 | 0.00 | 0.01 | 0.00 | 1.92 |
| 8,952.50 | 171.88 | 10,135.12 | 194.59 | 6.40 |
| 75,984.56 | 4,461.94 | 86,022.12 | 5,051.37 | 10.88 |
| 133,536.08 | 10,723.55 | 151,176.20 | 12,140.13 | 16.00 |
| 155,229.81 | 14,194.54 | 175,735.67 | 16,069.64 | 17.92 |
| 185,852.58 | 19,682.13 | 210,403.70 | 22,282.14 | 21.36 |
| 374,837.89 | 60,049.40 | 424,353.98 | 67,981.92 | 23.52 |
| 590,796.00 | 110,842.74 | 668,840.15 | 125,485.07 | 30.00 |
| 1,127,926.85 | 271,981.99 | 1,276,925.99 | 307,910.81 | 32.00 |
| 1,503,902.47 | 392,294.17 | 1,702,567.98 | 444,116.23 | 34.00 |
| 4,511,707.38 | 1,414,947.85 | 5,107,703.93 | 1,601,862.46 | 35.00 |

Límite superior de cada renglón = límite inferior del siguiente − 0.01.

```
ISR = cuota_fija + (base − límite_inferior) × tasa
```

## Algoritmo por régimen

### A. PFAE (612) y/o salarios (605) — Art. 152

Se suman los ingresos de los capítulos que acumulan (I salarios, II actividad empresarial/profesional, III arrendamiento, etc.) y se aplica la tarifa **una sola vez**.

```
Base = ingresos_acumulables − deducciones_autorizadas (612) − deducciones_personales_aplicables
ISR anual = tarifa Art. 152 del ejercicio sobre Base
```

- Salarios: restar ingresos exentos (Art. 93) antes de acumular.
- Pérdida fiscal de 612 (deducciones > ingresos): no se resta contra salarios; se amortiza en los 10 ejercicios siguientes (Art. 109).

### B. RESICO PF (626) — Art. 113-F

Pago anual con la tabla del Art. 113-F sobre el **total de ingresos cobrados** del año, sin deducciones de ningún tipo:

| Ingresos cobrados en el año (sin IVA) | Tasa |
|---|---|
| Hasta $300,000.00 | 1.00% |
| Hasta $600,000.00 | 1.10% |
| Hasta $1,000,000.00 | 1.50% |
| Hasta $2,500,000.00 | 2.00% |
| Hasta $3,500,000.00 | 2.50% |

```
ISR anual RESICO = ingresos_cobrados_año × tasa_del_renglón
Saldo = ISR anual − pagos mensuales (113-E) − retenciones 1.25% de PM
```

- **RESICO PF NO aplica deducciones personales del Art. 151** ni deducciones autorizadas.
- Si los ingresos superan $3,500,000 en el año, deja de tributar en RESICO a partir del mes siguiente y pasa al régimen general (Art. 113-I): calcular cada periodo por separado.
- Si además tiene sueldos, esos se declaran aparte con Art. 152 (RESICO se permite con sueldos si los ingresos totales no exceden $3.5M).

## Cálculo de saldo

```
ISR causado anual
− Pagos provisionales del ejercicio
− Retenciones de ISR (salarios, PM por honorarios 10%, plataformas, intereses)
= Diferencia
```

- Diferencia > 0: **saldo a pagar** (puede pagarse hasta en 6 parcialidades si la declaración se presenta en plazo — Art. 150 LISR).
- Diferencia < 0: **saldo a favor** (devolución o compensación desde DeclaraSAT).

## Ejemplo (PFAE 612, ejercicio 2025)

```
Ingresos acumulables              1,500,000.00
− Deducciones autorizadas          −250,000.00
− Deducciones personales            −60,000.00   (tope = menor de 5 UMA anuales $206,480.50 o 15% de ingresos $225,000 → $206,480.50; no se alcanza)
= Base                            1,190,000.00
Tarifa 2025, renglón 1,127,926.85: 271,981.99 + (1,190,000.00 − 1,127,926.85) × 32% = 291,845.40
− Pagos provisionales              −215,000.00
− ISR retenido                      −12,500.00
= Saldo a pagar                      64,345.40
```

UMA 2025 = $113.14 diaria → anual 113.14 × 365 = $41,296.10 → 5 UMA = $206,480.50. Para el ejercicio 2026: UMA $117.31 → anual $42,818.15 → 5 UMA = $214,090.75.

## Output

```json
{
  "ejercicio": 2025,
  "rfc_hash": "...",
  "regimen": "PFAE_612",
  "ingresos_acumulables_mxn": "1500000.00",
  "deducciones_autorizadas_mxn": "250000.00",
  "deducciones_personales_mxn": "60000.00",
  "tope_deducciones_personales_mxn": "206480.50",
  "base_gravable_mxn": "1190000.00",
  "tarifa_aplicada": "Art_152_LISR_2025_Anexo8_RMF2026",
  "isr_anual_causado_mxn": "291845.40",
  "pagos_provisionales_acumulados_mxn": "215000.00",
  "isr_retenido_acumulado_mxn": "12500.00",
  "diferencia_mxn": "64345.40",
  "resultado": "SALDO_A_PAGAR",
  "fecha_limite_presentacion": "2026-04-30",
  "advertencias": [
    "Saldos a favor altos o inconsistentes con CFDI suelen generar requerimientos del SAT antes de devolver"
  ],
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| RESICO PF que superó $3.5M a mitad de año | Régimen general desde el mes siguiente (Art. 113-I); calcular por periodo |
| Asalariado con 2 patrones simultáneos o que dejó de laborar antes del 31-dic | Obligado a declarar (Art. 98 fr. III); sumar ingresos y retenciones de ambos |
| Asalariado con ingresos > $400,000 | Obligado a presentar anual (Art. 98 fr. III) |
| Ingresos en USD | Convertir con el tipo de cambio DOF del día de cobro (`mp_banxico`) |
| Pérdida fiscal en 612 | Amortizable en ejercicios siguientes; no reduce ISR de salarios |
| Cambio de régimen a mitad de año | Calcular cada periodo por separado y sumar |

## Dependencias

- `mp_banxico` (`banxico_get_uma`, `banxico_get_tc_dof`) — UMA y tipo de cambio; requiere BANXICO_TOKEN
- Output de `recopilar-cfdis-anuales` + `identificar-deducciones-personales`
- Tracker local de pagos provisionales (del `core-mexico/cierre-fiscal-mensual`)

## ⚠ Compliance

- Tarifas verificadas contra Anexo 8 RMF 2026 (DOF 28-12-2025). Para ejercicios posteriores, confirmar el Anexo 8 vigente.
- `vigencia_validada: false` SIEMPRE en el output
- Es un estimado: **revisar con contador público antes de presentar**
