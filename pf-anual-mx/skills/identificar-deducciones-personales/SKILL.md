---
name: identificar-deducciones-personales
description: Identifica los CFDI del año que califican como deducciones personales del Art. 151 LISR (más colegiaturas por decreto) para personas físicas en México, valida requisitos (uso CFDI, forma de pago no efectivo, parentesco) y aplica los topes vigentes (menor entre 5 UMA anuales o 15% de ingresos; donativos y aportaciones al retiro con tope propio). Genera un dataset listo para la declaración anual 2025 (abril 2026) o 2026. Usar cuando el usuario pregunte deducciones personales, art 151, qué gastos personales deduzco, gastos médicos deducibles, colegiaturas, tope de deducciones, optimizar deducciones. NO usar para gastos de la actividad empresarial (deducciones autorizadas) ni para RESICO PF (no aplica deducciones personales).
allowed-tools: Read, Write
---

# Identificar deducciones personales — Art. 151 LISR

## A quién aplica

- Sueldos y salarios (605), actividad empresarial/profesional (612), arrendamiento y demás capítulos que acumulan en la anual (Art. 152).
- **RESICO PF (626): NO aplica.** Sus ingresos en RESICO no admiten deducciones personales; si además tiene sueldos, las deducciones personales solo reducen la base de la anual de sueldos.

## Topes (Art. 151, último párrafo)

- **Tope general**: el menor entre 5 UMA anuales y 15% del total de ingresos del año (incluidos exentos).
  - Ejercicio 2025: UMA $113.14 × 365 = $41,296.10 → 5 UMA = **$206,480.50**
  - Ejercicio 2026: UMA $117.31 × 365 = $42,818.15 → 5 UMA = **$214,090.75**
- **Donativos (fr. III)**: además de entrar al tope general, no pueden exceder 7% de los ingresos acumulables del ejercicio anterior (4% si el donativo es a la Federación, estados o municipios).
- **Fuera del tope general** (tope propio):
  - Aportaciones complementarias/voluntarias al retiro (fr. V): hasta 10% de ingresos acumulables del ejercicio, sin exceder 5 UMA anuales.
  - Gastos médicos por incapacidad o discapacidad (uso D02), con certificado.
  - Colegiaturas (Decreto DOF 26-12-2013): tope anual por alumno según nivel (preescolar $14,200; primaria $12,900; secundaria $19,900; profesional técnico $17,100; bachillerato $24,500).

## Categorías y uso de CFDI

| Categoría | Uso CFDI | Requisito clave |
|---|---|---|
| Honorarios médicos, dentales, psicólogos, nutriólogos y gastos hospitalarios (incluye análisis, prótesis, enfermería) | D01 | Prestador con título profesional en México; pago no efectivo |
| Lentes ópticos graduados | D01 | Hasta $2,500 por persona al año; diagnóstico de oftalmólogo u optometrista |
| Gastos médicos por incapacidad/discapacidad | D02 | Certificado de incapacidad ≥ 50% o de discapacidad |
| Gastos funerales | D03 | Hasta 1 UMA anual ($41,296.10 en 2025; $42,818.15 en 2026) |
| Donativos | D04 | Donataria autorizada vigente (`mp_donatarias_sat.donatarias_consultar`) |
| Intereses reales de crédito hipotecario | D05 | Casa habitación; crédito ≤ 750,000 UDIS; constancia anual del banco |
| Aportaciones voluntarias / complementarias al retiro | D06 | Permanencia hasta retiro |
| Primas de seguros de gastos médicos | D07 | Aseguradora mexicana |
| Transporte escolar obligatorio | D08 | Obligatorio por la escuela; separado en el CFDI |
| Depósitos en cuentas especiales para el ahorro / planes de pensiones | D09 | Art. 185 LISR; cuenta dentro del tope general |
| Colegiaturas | D10 | Escuela con RVOE; solo la colegiatura (no inscripción) |

**Beneficiarios**: el contribuyente, cónyuge o concubino, ascendientes y descendientes en línea recta, siempre que el beneficiario no perciba en el año ingresos iguales o mayores al salario mínimo general elevado al año (texto del Art. 151 fr. I; hay criterios que usan UMA — verificar con contador).

**Forma de pago**: médicos, dentales, hospitalarios y funerales deben pagarse con cheque nominativo, transferencia, tarjeta de crédito/débito/servicios (formas 02, 03, 04, 28, 29). Efectivo (01) no procede. Aplica el mismo criterio por prudencia al resto.

## Algoritmo

1. **Filtrar CFDI recibidos**: tipo I, receptor = RFC del contribuyente, `uso_cfdi` ∈ {D01…D10}, no cancelados.
2. **Validar** por CFDI: forma de pago, emisor activo (`mp_sat_portal.sat_consultar_padron` requiere e.firma; sin ella, marcar "verificar manualmente"), emisor fuera de 69-B (`sat_consultar_69b_efos`), donataria vigente si D04.
3. **Topes de renglón**: lentes $2,500/persona, funerales 1 UMA anual, colegiaturas por nivel.
4. **Tope general** a la suma de D01, D03, D04 (ya topado al 7%), D05, D07, D08, D09 y lentes.
5. **Sumar** lo que va fuera del tope (D02 por incapacidad/discapacidad, D06 topado, D10 colegiaturas).

## Ejemplo (ejercicio 2025, ingresos $1,200,000; ingresos acumulables 2024 $1,200,000)

| Categoría | Bruto | Aplicable |
|---|---:|---:|
| Médicos (D01) | 80,000 | 80,000 |
| Hospitalarios (D01) | 120,000 | 120,000 |
| Funerales (D03) | 25,000 | 25,000 (< 1 UMA) |
| Intereses hipotecarios reales (D05) | 35,000 | 35,000 |
| Primas GMM (D07) | 18,000 | 18,000 |
| Transporte escolar (D08) | 15,000 | 15,000 |
| Donativos (D04) | 50,000 | 50,000 (7% × 1,200,000 = 84,000) |
| **Sujeto a tope general** | **343,000** | |
| Aportaciones retiro (D06) | 40,000 | 40,000 (10% = 120,000; 5 UMA = 206,480.50) |

```
Tope general = min(5 UMA 206,480.50 ; 15% × 1,200,000 = 180,000) = 180,000
Aplicable sujeto a tope = min(343,000 ; 180,000) = 180,000
+ Aportaciones retiro 40,000 (fuera del tope)
= Deducciones personales totales 220,000
```

## Output

```json
{
  "ejercicio": 2025,
  "rfc_hash": "...",
  "totales_brutos_mxn": "383000.00",
  "sujeto_tope_general_mxn": "343000.00",
  "tope_general_mxn": "180000.00",
  "tope_aplicado": "15_por_ciento_ingresos",
  "fuera_de_tope_mxn": {"retiro": "40000.00", "colegiaturas": "0.00", "discapacidad": "0.00"},
  "deducciones_personales_totales_mxn": "220000.00",
  "uma_anual_mxn": "41296.10",
  "cfdis_descartados": [{"motivo": "forma de pago 01 efectivo", "cantidad": 3}],
  "siguiente_skill": "calculadora-isr-anual",
  "vigencia_validada": false
}
```

El ahorro de ISR se obtiene con `calculadora-isr-anual` (con y sin deducciones), no con una tasa fija.

## Casos edge

| Caso | Acción |
|---|---|
| Contribuyente en RESICO PF únicamente | No aplica: informar y terminar |
| Pago dividido (efectivo + transferencia) | Solo procede la parte no efectivo |
| Médico en el extranjero | No procede (título expedido conforme a leyes mexicanas) |
| Dependiente con ingresos ≥ salario mínimo anual | Sus gastos no son deducibles para el contribuyente |
| Colegiatura con inscripción/reinscripción en el mismo CFDI | Solo la colegiatura; pedir CFDI desglosado |
| CFDI a nombre de otra persona | No procede: el receptor debe ser el contribuyente |

## ⚠ Compliance

- Topes verificados: Art. 151 LISR (texto vigente, Cámara de Diputados, última reforma DOF 01-04-2024), UMA INEGI 2025/2026, Decreto de colegiaturas DOF 26-12-2013.
- `vigencia_validada: false` siempre — el contador valida antes de presentar.
