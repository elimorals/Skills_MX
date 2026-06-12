---
name: cfdis-medicos-deducibles-acumulados
description: Acumula los CFDIs médicos del paciente durante el año (médicos, hospitales, medicamentos, lentes, primas GMM) listos para deducción anual Art. 151 LISR. Valida que cada CFDI cumpla requisitos: forma de pago no efectivo, uso D01/D02/D07, RFC paciente correcto. Usar cuando el usuario diga deducibles medicos, acumular cfdis salud, declaracion anual medicos.
allowed-tools: Read, Write
---

# CFDIs médicos deducibles acumulados

## Categorías Art. 151

| Categoría | Uso CFDI | Tope |
|---|---|---|
| Honorarios médicos/dentales | D01 | Sin tope (sujeto a tope general) |
| Gastos hospitalarios | D01 | Sin tope |
| Lentes graduados | D01 (parte del paquete oftalmólogo) | Sin tope |
| Análisis clínicos | D01 | Sin tope |
| Prima GMM | D07 | Sin tope |
| Aportación AFORE voluntaria | (No CFDI, constancia AFORE) | Tope independiente |

## Tope general

5 UMAs anuales **o** 15% ingresos del año, **el menor**.

## Output

```json
{
  "ejercicio": 2026,
  "rfc_hash": "...",
  "categorias": {
    "honorarios_medicos_d01": {"cfdis": 8, "monto_mxn": "12500.00"},
    "hospitalarios": {"cfdis": 2, "monto_mxn": "45000.00"},
    "prima_gmm_d07": {"cfdis": 1, "monto_mxn": "32500.00"}
  },
  "total_acumulado_mxn": "90000.00",
  "ahorro_isr_estimado_mxn": "27000.00",
  "advertencias": [
    "2 CFDIs con forma pago efectivo NO aplicarán",
    "Topear contra 5 UMAs anuales en declaración"
  ]
}
```
