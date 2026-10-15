---
name: cfdis-medicos-deducibles-acumulados
description: Acumula los CFDIs médicos del paciente durante el año (honorarios médicos, dentales, psicología, nutrición, hospital, análisis, lentes graduados, primas GMM) listos para las deducciones personales de la declaración anual (Art. 151 LISR). Valida que cada CFDI cumpla requisitos: pago con medio electrónico (no efectivo), uso D01/D02/D07, RFC del contribuyente, parentesco del beneficiario, y aplica el tope global de 5 UMA anuales o 15% de ingresos. Usar cuando el usuario diga deducibles médicos, acumular cfdis salud, declaración anual gastos médicos, deducir seguro GMM, facturas del doctor.
allowed-tools: Read, Write
---

# CFDIs médicos deducibles acumulados

> Orientación fiscal, no asesoría. Confirma con tu contador antes de presentar la anual.
> Fuente: LISR Art. 151 (texto vigente, última reforma DOF 01-04-2024; sin cambios al artículo identificados para 2026).

## Qué es deducible (Art. 151 LISR)

| Concepto | Fundamento | Uso CFDI | Notas |
|---|---|---|---|
| Honorarios médicos, dentales, psicología y nutrición | fr. I | D01 | Prestador con título profesional registrado |
| Gastos hospitalarios | fr. I | D01 | Incluye análisis, estudios clínicos, enfermería, prótesis, aparatos (RLISR Art. 264 — confianza media, verificar) |
| Lentes ópticos graduados | fr. I + RLISR | D01 | Hasta $2,500 por persona al año (RLISR — verificar vigencia) |
| Gastos por incapacidad (Art. 477 LFT) o discapacidad ≥ 50% | fr. I, 3er párrafo | D02 | Requiere certificado de institución pública; **no** sujeto al tope global |
| Primas de seguro de gastos médicos | fr. VI | D07 | Beneficiario: contribuyente, cónyuge/concubino, ascendientes o descendientes en línea recta |

**No deducibles**: medicinas compradas en farmacia (solo si vienen dentro de la factura del hospital), consultas pagadas en efectivo, gastos reembolsados por la aseguradora (solo se deduce la parte no recuperada — Art. 151, penúltimos párrafos).

## Requisitos que valida la skill

1. **Medio de pago (fr. I)**: cheque nominativo, transferencia desde cuenta a nombre del contribuyente, o tarjeta de crédito/débito/servicios. Forma de pago `01 Efectivo` → no procede.
   Para primas GMM (fr. VI) la ley no repite este requisito, pero paga bancarizado igual.
2. **CFDI a nombre del contribuyente** (RFC receptor = quien deduce), pagado en el año y a residentes en México.
3. **Dependientes**: cónyuge/concubino, padres, hijos, siempre que **no** perciban en el año ingresos ≥ 1 salario mínimo general anual (2026: $315.04 × 365 = $114,989.60).
4. **Uso CFDI** correcto: D01 / D02 / D07. Si viene `S01` o `G03`, pide al emisor sustituirlo antes de la anual.

## Tope global (último párrafo Art. 151)

Menor entre **5 UMA anuales** o **15% de los ingresos totales** (incluye exentos).
- Ejercicio 2026: UMA anual $42,794.64 (INEGI, DOF 09-01-2026) → 5 UMA = **$213,973.20**.
- No aplica a aportaciones complementarias de retiro (fr. V) ni a gastos por incapacidad/discapacidad (D02).

## Output

```json
{
  "ejercicio": 2026,
  "rfc_hash": "...",
  "ingresos_totales_mxn": "600000.00",
  "categorias": {
    "honorarios_medicos_d01": {"cfdis": 8, "monto_mxn": "12500.00"},
    "hospitalarios_d01": {"cfdis": 2, "monto_mxn": "45000.00"},
    "prima_gmm_d07": {"cfdis": 1, "monto_mxn": "32500.00"}
  },
  "total_acumulado_mxn": "90000.00",
  "tope_global_mxn": "90000.00",
  "deducible_aplicable_mxn": "90000.00",
  "ahorro_isr_estimado_mxn": "27000.00",
  "supuesto_ahorro": "tasa marginal 30% (ilustrativo; depende de la tarifa Art. 152)",
  "advertencias": [
    "2 CFDIs con forma de pago 01 Efectivo NO se incluyeron",
    "Tope = menor entre $213,973.20 (5 UMA) y 15% de $600,000 = $90,000"
  ]
}
```

Cálculo del ejemplo: 12,500 + 45,000 + 32,500 = 90,000; tope = min(213,973.20; 90,000) = 90,000; ahorro ≈ 90,000 × 30% = 27,000.
