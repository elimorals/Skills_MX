---
name: ingresos-multi-plataforma
description: Consolida ingresos del conductor de múltiples plataformas (Uber + DiDi + Cabify + InDriver) en una sola vista por periodo (semana, mes, año). Permite el control real del income vs lo que cada plataforma reporta individualmente. Reconciliación necesaria para declaración anual (todos los ingresos suman). Usar cuando el usuario diga ingreso total plataformas, suma Uber DiDi, ingreso consolidado, total chofer.
allowed-tools: Read, Write
---

# Ingresos multi-plataforma — consolidación

## Por qué importa

El SAT considera **todos los ingresos** de plataformas en un solo régimen (RESICO PF 626 o PFAE 612). Si conduces en Uber + DiDi y solo declaras Uber → discrepancia fiscal.

## Output

```json
{
  "periodo": "2026-06",
  "rfc_hash": "...",
  "totales": {
    "ingresos_brutos_mxn": "26500.00",
    "comisiones_pagadas_mxn": "5300.00",
    "retenciones_isr_total_mxn": "1060.00",
    "retenciones_iva_total_mxn": "1060.00",
    "neto_recibido_mxn": "19080.00"
  },
  "por_plataforma": {
    "uber": {"viajes": 142, "bruto_mxn": "17800.00", "neto_mxn": "12816.00"},
    "didi": {"viajes": 65, "bruto_mxn": "8700.00", "neto_mxn": "6264.00"},
    "cabify": {"viajes": 0, "bruto_mxn": "0"},
    "indriver": {"viajes": 0, "bruto_mxn": "0"}
  },
  "vs_mes_anterior_pct": 8.5,
  "advertencias": [
    "Si ingresos anuales > $300,000 considera Art. 113-A reglas más estrictas",
    "Si ingresos anuales > $3.5M: pierdes RESICO PF, pasa a PFAE"
  ]
}
```

## Cómo obtener datos por plataforma

| Plataforma | Método |
|---|---|
| Uber | Panel conductor → reportes → CSV mensual |
| DiDi | App DiDi Driver → ingresos → exportar |
| Cabify | Panel partners → reporte mensual |
| InDriver | App → resumen mensual |

Manual por ahora (sin MCPs oficiales para los 4).
