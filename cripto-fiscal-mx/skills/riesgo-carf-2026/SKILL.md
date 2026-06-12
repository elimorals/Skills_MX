---
name: riesgo-carf-2026
description: Evalúa qué saldos y operaciones del usuario están en zona reportable al SAT bajo el CARF (Common Reporting Framework de OCDE) que entró en vigor 2026. Bitso ya reporta saldos > $200k MXN y operaciones individuales > $50k USD. Si no se declara y SAT recibe el reporte: discrepancia automática + auditoría. Usar cuando el usuario diga CARF, reporte exchange al SAT, va a reportar bitso.
allowed-tools: Read, Write
---

# Riesgo CARF 2026

## Qué es CARF

Common Reporting Framework para activos cripto, desarrollado por OCDE. México adoptó.

A partir de 2026: TODOS los exchanges con clientes mexicanos deben reportar al SAT:
- Saldos a fin de año
- Operaciones individuales > umbral
- Identidad del cliente (KYC)

## Umbrales reportables Bitso (ya reportando desde 2021)

| Trigger | Acción |
|---|---|
| Saldo > $200k MXN al cierre año | Reporte anual |
| Operación individual > $50k USD | Reporte inmediato |
| Múltiples ops mismo día = transacción estructurada | Reporte |

## Riesgo de no declarar

Si el SAT recibe el reporte CARF y el contribuyente no declaró:
- Discrepancia fiscal automática
- Multa: 100-200% del impuesto omitido
- Recargos + actualización
- Auditoría completa probable

## Output

```json
{
  "rfc_hash": "...",
  "ejercicio": 2026,
  "exchanges_con_saldo_reportable": [
    {
      "exchange": "bitso",
      "saldo_cierre_mxn": "312000.00",
      "umbral_reporte": "200000 MXN",
      "estado": "REPORTABLE — declarar obligatorio"
    }
  ],
  "operaciones_grandes_reportadas": [
    {"fecha": "2026-03-15", "monto_usd": "65000", "exchange": "bitso", "tipo": "venta_btc"}
  ],
  "riesgo_no_declarar": "ALTO",
  "recomendacion": "Declarar TODAS las operaciones del año en anual 2026 (vence abril 2027)",
  "vigencia_validada": false
}
```
