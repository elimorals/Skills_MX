---
name: workflow-pf-anual-completa
description: Orquesta declaración anual ISR para Persona Física (PFAE o RESICO PF). Descarga masiva CFDIs emitidos+recibidos del año completo, cruce con bancos para verificar pagos efectivos, cálculo de ingresos acumulables, identificación de deducciones autorizadas (gastos médicos, educación, hipoteca, donativos, intereses créditos), aplicación de tarifa Art. 96 LISR vigente, comparativa con pagos provisionales acumulados del año, generación de borrador de declaración. Despachar entre abril (presentación obligatoria PF) y mayo. Subagent porque procesa cientos de CFDIs.
tools: Read, Write, Bash, Grep
---

# Workflow: Declaración Anual ISR — Persona Física

Cierra el año fiscal de PF: descarga todo, cruza, calcula impuesto, genera borrador.

⚠ La declaración anual de PF en MX se presenta **en abril** del año siguiente. Para PFAE el plazo es **30 abril**.

## Cuándo te despachan

- Antes del 30 abril (deadline obligatorio)
- Después de cierre fiscal del último mes del año (diciembre)
- Para revisar año anterior antes de presentar
- Para PF con ingresos por:
  - Sueldos (si trabajan también otras actividades)
  - Honorarios PFAE
  - RESICO PF
  - Arrendamiento
  - Actividad empresarial
  - Enajenación de bienes

## Inputs

```json
{
  "rfc": "MAJG800101XYZ",
  "ejercicio": 2025,
  "regimen": "RESICO_PF | PFAE | GENERAL",
  "fuentes_ingreso": ["honorarios", "arrendamiento"],
  "incluir_deducciones_personales": true
}
```

## Fases del workflow

### Fase 1: Recopilación masiva (paralelo)

```
parallel([
  () => sat_descargar_cfdi_masivo(rfc, ejercicio=2025, mes=1, "emitidos"),
  () => sat_descargar_cfdi_masivo(rfc, ejercicio=2025, mes=1, "recibidos"),
  ...
  () => sat_descargar_cfdi_masivo(rfc, ejercicio=2025, mes=12, "emitidos"),
  () => sat_descargar_cfdi_masivo(rfc, ejercicio=2025, mes=12, "recibidos"),
  () => sat_descargar_buzon_tributario(rfc),
  () => banxico_get_uma_anual(2025),
  () => banxico_get_inpc_anual(2025)
])
```

⚠ Cada descarga masiva es async (1-4 hrs). El workflow puede tomar hasta 12 horas si la red SAT está lenta. Plan: arrancar el workflow día anterior a presentación.

### Fase 2: Consolidación de CFDIs

```
ingresos_emitidos = sum(CFDIs emitidos del año, tipo I, no cancelados)
gastos_recibidos = sum(CFDIs recibidos del año, tipo I, no cancelados)
retenciones_isr = sum(retenciones ISR en CFDIs recibidos)
retenciones_iva = sum(retenciones IVA en CFDIs recibidos)
```

### Fase 3: Cruce con bancos (si Aspel/ContPAQi configurado o si tiene MCPs bancos activados)

```
parallel([
  () => mp_bancos_mx.descargar_estado_cuenta_anual(banco_principal),
  () => aspel_obtener_balanza(2025, 12)
])
```

Calcular:
- **Ingresos efectivamente cobrados** (CFDIs PUE + REP de PPD)
- **Gastos efectivamente pagados** (CFDIs con pago bancarizado)
- **Discrepancias**: depósitos sin CFDI, gastos en efectivo > $2,000 (no deducibles)

### Fase 4: Identificación deducciones personales (Art. 151 LISR)

PF puede deducir personales (no de actividad):

| Deducción | Tope 2025 (referencia, validar 2026) |
|---|---|
| Gastos médicos + dentales + hospitalarios | 5 UMAs anuales × 365 días |
| Hospitalización por enfermedad grave | Sin tope |
| Lentes ópticos | $2,500 |
| Gastos funerarios | 1 UMA anual |
| Donativos a donatarias autorizadas | 7% ingresos del año anterior |
| Intereses reales hipotecarios (CASA HABITACION) | Tope $750k principal × tasa real |
| Aportaciones a SAR / planes personales | 10% ingresos sin pasar 5 UMAs |
| Primas seguro gastos médicos | Sin tope claro |
| Transporte escolar obligatorio | Tope variable |

⚠ Tope total deducciones personales: **5 UMAs anuales (~$200k MXN 2025)**

⚠ Tope total especial Art. 151: 15% de ingresos del ejercicio (lo menor entre los dos topes).

### Fase 5: Cálculo de ISR anual

#### RESICO PF (simple)
```
ingresos_efectivamente_cobrados_anual = sum del año
si ingresos <= $3,500,000:  // umbral 2025, verificar 2026
  tasa = ladder(
    25k*12 → 1.0%,
    50k*12 → 1.1%,
    83k*12 → 1.5%,
    208k*12 → 2.0%,
    > 208k*12 → 2.5%
  )
  isr_anual = ingresos × tasa
si > $3,500,000:
  ya no aplica RESICO, debe declarar bajo PFAE general
```

#### PFAE General
```
ingresos_acumulables = sum ingresos
deducciones_acumulables = sum gastos deducibles
deducciones_personales = min(sum, tope_5_uma o 15%)
utilidad_fiscal = ingresos - deducciones - personales
isr_anual = aplicar_tarifa_Art_96_LISR(utilidad_fiscal)
isr_pagado_provisional = sum pagos provisionales del año
diferencia = isr_anual - isr_pagado_provisional - isr_retenido

si diferencia > 0: pagar al SAT
si diferencia < 0: saldo a favor (solicitar devolución)
```

### Fase 6: Validación cruzada

- Si ingresos declarados < depósitos bancarios → riesgo de revisión
- Si gastos declarados > 80% ingresos → revisión probable
- Si saldo a favor > $50k → SAT revisa antes de devolver

### Fase 7: Generación de borrador

```
Generar archivo con:
- Resumen ingresos y deducciones
- ISR calculado
- Pagos provisionales acreditables
- Diferencia (a pagar o a favor)
- Línea de captura sugerida (pendiente generar real en portal SAT)
```

### Fase 8: Reporte ejecutivo

```json
{
  "declaracion_anual_pf": {
    "rfc_hash": "abc123",
    "ejercicio": 2025,
    "regimen": "PFAE",
    "ingresos_acumulables_mxn": 1_240_000,
    "deducciones_acumulables_mxn": 285_000,
    "deducciones_personales_mxn": 145_000,
    "deducciones_personales_aplicables_mxn": 145_000,
    "utilidad_fiscal_mxn": 810_000,
    "isr_anual_calculado_mxn": 165_000,
    "pagos_provisionales_acumulados_mxn": 145_000,
    "retenciones_isr_acumuladas_mxn": 24_000,
    "diferencia_mxn": -4_000,
    "resultado": "SALDO_A_FAVOR_4000_MXN",
    "fecha_limite_presentacion": "2026-04-30",
    "borrador_listo": true,
    "alertas": [
      "Saldo a favor — solicitar devolución vía portal SAT",
      "Validar tarifa Art. 96 LISR 2025 antes de presentar"
    ],
    "vigencia_validada": false,
    "advertencia_critica": (
      "Cálculo REFERENCIAL. NO presentar sin validación de contador. "
      "Tarifas usadas son las publicadas en RMF 2025 (verificar)."
    )
  }
}
```

## Manejo de errores

| Caso | Acción |
|---|---|
| Descarga masiva SAT no completada | Marcar pendiente, retry en 4 hrs |
| Régimen no soportado (ej. Repe, BSR) | Generar reporte parcial, recomendar consultor |
| Tarifa Art. 96 no validada | Reportar con advertencia explícita |
| Saldo a favor > $100k | Alertar al usuario — riesgo de auditoría detallada |

## Por qué subagent

- Cientos de CFDIs procesados
- Múltiples MCPs coordinados
- Cálculos críticos fiscales requieren aislamiento

## Validación pendiente

- Tarifas Art. 96 LISR 2025 y 2026 vigentes
- Topes deducciones personales 2025 y 2026
- Umbrales RESICO PF 2025 ($3.5M) y 2026
- Casos especiales (sueldos + honorarios + arrendamiento)
- **Crítico**: contador certificado validar antes de presentar al SAT
