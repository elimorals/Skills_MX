---
name: calculo-fiscal-conductor
description: Cálculo fiscal específico para conductor de plataforma bajo Art. 113-A LISR (retención automática de la plataforma) + Régimen 626 RESICO PF. Determina si el conductor debe declaración mensual adicional (sí, si va más allá de la retención de la plataforma) y calcula ISR neto a pagar tras acreditar las retenciones que ya hicieron las plataformas. Usar cuando el usuario diga cuánto pago de impuestos, calcular ISR chofer, pago provisional mensual, retenciones art 113-A.
allowed-tools: Read, Write
---

# Cálculo fiscal conductor — Art. 113-A LISR

## Régimen aplicable

**Art. 113-A LISR**: aplica a personas físicas que prestan servicios de manera autónoma por internet a través de plataformas tecnológicas (transporte, entrega, hospedaje).

**Retención automática**:
- ISR: 8% del ingreso (variable según monto si en RESICO, ver tabla)
- IVA: 8% del ingreso (la plataforma lo retiene y entera al SAT)

## Tabla ISR retenida por plataforma (art. 113-A)

| Ingresos mensuales | Tasa ISR retenida por plataforma |
|---|---|
| Hasta $5,500 | 2% |
| Hasta $15,000 | 3% |
| Hasta $21,000 | 4% |
| Más de $21,000 | 8% |

## Algoritmo

```python
def calcular_isr_conductor_mes(ingresos_mes: Decimal, retencion_acumulada: Decimal) -> dict:
    # 1. Aplicar tabla art. 113-A LISR
    if ingresos_mes <= 5500:
        tasa = 0.02
    elif ingresos_mes <= 15000:
        tasa = 0.03
    elif ingresos_mes <= 21000:
        tasa = 0.04
    else:
        tasa = 0.08

    isr_causado = ingresos_mes * Decimal(str(tasa))

    # 2. Acreditar retenciones que YA hicieron las plataformas
    isr_a_pagar = max(Decimal(0), isr_causado - retencion_acumulada)

    return {
        "tasa_aplicada": tasa,
        "isr_causado_mxn": str(isr_causado),
        "retencion_plataforma_mxn": str(retencion_acumulada),
        "isr_a_pagar_adicional_mxn": str(isr_a_pagar),
        "obligacion_declaracion": isr_a_pagar > 0 or ingresos_mes > 21000,
    }
```

## Output

```json
{
  "rfc_hash": "...",
  "mes": "2026-06",
  "regimen": "626_RESICO_PF",
  "ingresos_mes_mxn": "26500.00",
  "tasa_aplicable_art_113A": 0.08,
  "isr_causado_mxn": "2120.00",
  "retencion_plataformas_acumulada_mxn": "1060.00",
  "isr_a_pagar_adicional_mxn": "1060.00",
  "deadline_pago": "2026-07-17",
  "obligacion_declaracion": true,
  "advertencias": [
    "Ingresos > $21,000 mes: aplica tasa 8% completa",
    "Diferencia se paga vía declaración mensual estándar SAT"
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

- Validar tabla Art. 113-A vigente cada enero (puede cambiar en RMF)
- `vigencia_validada: false` — contador valida en declaración anual
- Las retenciones de la plataforma SÍ se declaran (acreditan) — no se omiten
