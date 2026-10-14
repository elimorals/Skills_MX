---
name: calculo-fiscal-conductor
description: Cálculo fiscal específico para conductor de plataforma bajo Art. 113-A LISR (retención automática de la plataforma) + Régimen 626 RESICO PF. Determina si el conductor debe declaración mensual adicional (sí, si va más allá de la retención de la plataforma) y calcula ISR neto a pagar tras acreditar las retenciones que ya hicieron las plataformas. Usar cuando el usuario diga cuánto pago de impuestos, calcular ISR chofer, pago provisional mensual, retenciones art 113-A.
allowed-tools: Read, Write
---

# Cálculo fiscal conductor — Art. 113-A LISR

## Régimen aplicable

**Art. 113-A LISR**: aplica a personas físicas que prestan servicios de manera autónoma por internet a través de plataformas tecnológicas (transporte, entrega, hospedaje).

**Retención automática** (sobre ingresos cobrados sin IVA):
- ISR: tasa fija por tipo de servicio (Art. 113-A LISR, vigente desde 2021; ya no hay tabla progresiva)
- IVA: 50% del IVA cobrado = 8% del ingreso (Art. 18-M LIVA)
- Sin RFC proporcionado a la plataforma: ISR 20% e IVA 100% (Art. 113-C LISR / 18-M LIVA)

## Tasas ISR retenidas por la plataforma (Art. 113-A)

| Servicio | Tasa ISR |
|---|---|
| Transporte terrestre de pasajeros y entrega de bienes (Uber, DiDi, Rappi) | 2.1% |
| Hospedaje | 4% |
| Enajenación de bienes y prestación de servicios | 1% |

**Pago definitivo (Art. 113-B LISR)**: si los ingresos del ejercicio anterior por plataformas no excedieron $300,000, el conductor puede optar porque la retención sea pago definitivo → no hay ISR adicional que pagar. Si no opta o excede, la retención es **pago provisional acreditable** contra el pago mensual de su régimen.

## Algoritmo

```python
TASA_113A = {"transporte": Decimal("0.021"), "hospedaje": Decimal("0.04"), "otros": Decimal("0.01")}

def retencion_isr_plataforma(ingresos_mes_sin_iva: Decimal, servicio: str = "transporte") -> Decimal:
    return (ingresos_mes_sin_iva * TASA_113A[servicio]).quantize(Decimal("0.01"))

def isr_a_pagar_mes(isr_causado_regimen: Decimal, retenciones_plataformas: Decimal, opcion_definitiva: bool) -> Decimal:
    # isr_causado_regimen: pago provisional calculado según el régimen del conductor (no con la tasa 113-A)
    if opcion_definitiva:
        return Decimal("0")
    return max(Decimal("0"), isr_causado_regimen - retenciones_plataformas)
```

## Output

```json
{
  "rfc_hash": "...",
  "mes": "2026-06",
  "servicio": "transporte",
  "ingresos_mes_sin_iva_mxn": "26500.00",
  "tasa_isr_art_113A": 0.021,
  "retencion_isr_plataforma_mxn": "556.50",
  "retencion_iva_plataforma_mxn": "2120.00",
  "opcion_pago_definitivo_113B": true,
  "isr_a_pagar_adicional_mxn": "0.00",
  "deadline_pago": "2026-07-17",
  "advertencias": [
    "Opción 113-B solo si ingresos del ejercicio anterior <= $300,000",
    "Sumar retenciones de TODAS las plataformas (CFDI de retenciones que emite cada una)"
  ],
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Múltiples plataformas | Sumar retenciones de TODAS antes de acreditar |
| Conductor también factura otros servicios | Sumar al ingreso total — sale del simplificado |
| Cambio de régimen mid-año | Recalcular por periodo |
| Ingresos anuales > $3.5M | NO aplica RESICO PF — recalcular como PFAE |

## ⚠ Compliance

- Validar tasas del Art. 113-A LISR cada enero (cambian por reforma a la LISR, no por RMF)
- `vigencia_validada: false` — contador valida en declaración anual
- Las retenciones de la plataforma SÍ se declaran (acreditan) — no se omiten
