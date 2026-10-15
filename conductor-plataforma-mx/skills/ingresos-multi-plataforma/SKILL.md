---
name: ingresos-multi-plataforma
description: Consolida ingresos del conductor de múltiples plataformas (Uber + DiDi + Cabify + InDriver) en una sola vista por periodo (semana, mes, año). Permite el control real del income vs lo que cada plataforma reporta individualmente. Reconciliación necesaria para declaración anual (todos los ingresos suman). Usar cuando el usuario diga ingreso total plataformas, suma Uber DiDi, ingreso consolidado, total chofer, cuánto gané en todas las apps, juntar mis ingresos.
allowed-tools: Read, Write
---

# Ingresos multi-plataforma — consolidación

## Por qué importa

El SAT recibe de **cada** plataforma la información y el CFDI de retenciones; todos los ingresos se suman en un mismo régimen (plataformas 625, RESICO PF 626 o actividad empresarial 612). Si conduces en Uber + DiDi y solo declaras Uber → discrepancia. El límite de $300,000 de la opción 113-B se mide con el total de todas las plataformas.

## Output

```json
{
  "periodo": "2026-06",
  "rfc_hash": "...",
  "totales": {
    "ingresos_brutos_mxn": "26500.00",
    "comisiones_pagadas_mxn": "5300.00",
    "retenciones_isr_total_mxn": "556.50",
    "retenciones_iva_total_mxn": "2120.00",
    "neto_recibido_mxn": "18523.50"
  },
  "por_plataforma": {
    "uber": {"viajes": 142, "bruto_mxn": "17800.00", "neto_mxn": "12442.20"},
    "didi": {"viajes": 65, "bruto_mxn": "8700.00", "neto_mxn": "6081.30"},
    "cabify": {"viajes": 0, "bruto_mxn": "0"},
    "indriver": {"viajes": 0, "bruto_mxn": "0"}
  },
  "vs_mes_anterior_pct": 8.5,
  "advertencias": [
    "Si los ingresos del año superan $300,000, el año siguiente ya no puedes optar por retención como pago definitivo (Art. 113-B)",
    "Neto = bruto − comisión 20% − ISR 2.1% − IVA retenido 8% (supuesto de comisión: usar la real de cada app)"
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

Manual: `mp_didi_partners` existe pero DiDi no publica API para conductores (devuelve `ConfigError`); `mp_cabify_business` es para empresas que piden viajes, no para conductores. Pide al usuario los resúmenes o CSV.
