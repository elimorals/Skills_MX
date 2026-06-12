---
name: identificar-deducciones-personales
description: Identifica automáticamente CFDIs del año que califican como deducciones personales bajo Art. 151 LISR para personas físicas en México. Cubre las 8 categorías oficiales: honorarios médicos y dentales, gastos hospitalarios, gastos funerarios, donativos a donatarias autorizadas, intereses reales de créditos hipotecarios, primas de seguros de gastos médicos, transporte escolar obligatorio, y aportaciones complementarias para retiro. Aplica los topes vigentes (5 UMAs anuales o 15% de ingresos, el menor). Genera un dataset listo para integrar en la declaración. Usar cuando el usuario pregunte deducciones personales, art 151, gastos deducibles persona fisica, optimizar deducciones. NO usar para gastos de actividad empresarial (esos son deducciones acumulables, distinto).
allowed-tools: Read, Write
---

# Identificar deducciones personales — Art. 151 LISR

## Concepto

Art. 151 LISR permite a PF restar de su base gravable ciertos gastos personales del año. Aplica para:
- PFAE (612)
- RESICO PF (626) — desde 2023 también aplica con reglas específicas
- Asalariado (605)

## Topes vigentes (ejercicio 2025)

- **General**: 5 UMAs anuales ó 15% de ingresos totales, **el menor**
- **Aportaciones para retiro (Art. 151-V)**: 10% de ingresos ó 5 UMAs anuales, el menor (tope independiente)
- **Donativos**: 7% de ingresos del año anterior

⚠ UMA y tarifa Art. 96 cambian cada enero. **Validar con contador** antes de presentar.

## Categorías cubiertas (8)

### 1. Honorarios médicos y dentales
- Pagos a médicos, dentistas, psicólogos, enfermeras
- Para el contribuyente, cónyuge, ascendientes en línea recta, descendientes en línea recta
- **Forma de pago debe ser distinta a efectivo** (transferencia, tarjeta, cheque nominativo)
- CFDI: tipo I, uso D01 o D02

### 2. Gastos hospitalarios
- Hospital, análisis clínicos, ambulancia, lentes graduados
- CFDI: tipo I, uso D01

### 3. Gastos funerarios
- Hasta el equivalente a 1 UMA anual
- Cónyuge, ascendientes, descendientes
- CFDI: tipo I, uso D03

### 4. Donativos a donatarias autorizadas
- Hasta 7% del ingreso del año anterior
- Donataria debe aparecer en lista del SAT
- CFDI: tipo I, uso D04

### 5. Intereses reales de créditos hipotecarios
- Casa habitación
- Crédito hasta 750k UDIs
- El banco emite constancia anual de intereses reales (no es CFDI tipo I)

### 6. Primas de seguros de gastos médicos
- Mayores
- Pagados por el contribuyente, para sí o familiares dependientes
- CFDI: tipo I, uso D07

### 7. Transporte escolar obligatorio
- Solo si está obligado por la institución educativa
- Para descendientes directos del contribuyente
- CFDI: tipo I, uso D08

### 8. Aportaciones complementarias para retiro
- Subcuentas de retiro o planes personales
- Tope adicional: 10% ingresos o 5 UMAs anuales

## Algoritmo

### Paso 1 — Filtrar CFDIs recibidos
- `tipo == "I"` (ingreso para el emisor = egreso para el receptor)
- `uso_cfdi` ∈ `{D01, D02, D03, D04, D07, D08}` o derivados

### Paso 2 — Validar requisitos por categoría

Por cada CFDI:
- **Forma de pago**: debe ser 02 (cheque), 03 (transferencia), 04 (tarjeta crédito), 28 (tarjeta débito). Forma 01 (efectivo) **NO aplica** para D01/D02.
- **RFC emisor**: debe estar en padrón SAT activo (`mp_sat_portal.consultar_padron`)
- **Si donativo**: emisor debe estar en lista de donatarias autorizadas SAT
- **Si médico**: emisor debe tener actividad económica relevante (médico, dentista, psicólogo)

### Paso 3 — Sumar por categoría

| Categoría | Total bruto | Aplicable (sin tope) |
|---|---|---|
| Médicos | $80,000 | $80,000 |
| Hospitalarios | $120,000 | $120,000 |
| Funerarios | $25,000 | $25,000 (tope 1 UMA) |
| Donativos | $50,000 | $50,000 |
| Intereses hipotecarios | $35,000 | $35,000 |
| Primas seguros | $18,000 | $18,000 |
| Transporte escolar | $15,000 | $15,000 |
| Aportaciones retiro | $40,000 | $40,000 (tope independiente) |

### Paso 4 — Aplicar topes

```
UMA 2025 anual = $4,000 × 5 = $20,000 (ejemplo placeholder — validar)
15% ingresos = $1,200,000 × 0.15 = $180,000

Tope general = min($20,000, $180,000) = $20,000  ← este es el menor

Deducciones generales aplicables = min($343,000, $20,000) = $20,000
+ aportaciones retiro = $40,000 (tope independiente)
TOTAL deducciones personales aplicables = $60,000
```

### Paso 5 — Output

```json
{
  "ejercicio": 2025,
  "rfc_hash": "...",
  "categorias": {
    "medicos": {"cfdis_count": 12, "monto_bruto": "80000.00", "monto_aplicable": "80000.00"},
    "hospitalarios": {"cfdis_count": 5, "monto_bruto": "120000.00", "monto_aplicable": "120000.00"},
    ...
  },
  "totales_brutos_mxn": "343000.00",
  "deducciones_generales_aplicables_mxn": "20000.00",
  "aportaciones_retiro_aplicables_mxn": "40000.00",
  "deducciones_personales_totales_mxn": "60000.00",
  "tope_aplicado": "5_UMAs_anuales",
  "uma_anual_referencia_mxn": "TODO_VALIDAR_2025",
  "ahorro_isr_estimado_mxn": "21000.00",
  "vigencia_validada": false,
  "advertencias": [
    "Tope basado en UMA 2025 — confirmar con publicación INEGI vigente",
    "Médicos pagados en efectivo (forma 01): NO aplican — 3 CFDIs descartados"
  ]
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Médico/dentista en RESICO PF (factura simplificada) | Aplica igual, valida que tenga uso D01/D02 correctamente |
| CFDI tipo I emitido por persona física a otra persona física | Aplica si cumple todos los requisitos |
| Pago dividido (efectivo + transferencia) | Solo aplica la parte no-efectivo |
| Gastos en USD (médicos en el extranjero) | NO aplica — debe ser servicio en México |
| Aportación voluntaria a AFORE | Aplica con tope independiente |

## ⚠ Compliance

- Validar tope UMA cada enero
- `vigencia_validada: false` siempre — contador valida antes de presentar
- Forma de pago efectivo NO aplica para médicos/dentistas — verifica
