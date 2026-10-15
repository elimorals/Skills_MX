---
name: calculo-fiscal-conductor
description: Cálculo fiscal del conductor o repartidor de plataforma (Uber, DiDi, Cabify, inDrive, Rappi) bajo los Arts. 113-A a 113-C LISR (retención ISR 2.1%) y 18-J LIVA (retención IVA 8%). Determina si las retenciones pueden ser pago definitivo (opción 113-B, ingresos ≤ $300,000) o si debe presentar pago mensual adicional en régimen de plataformas (625) o RESICO PF (626), acreditando lo retenido. Usar cuando el usuario diga cuánto pago de impuestos, calcular ISR chofer, impuestos Uber, retenciones de la app, pago provisional mensual, retenciones art 113-A, régimen plataformas.
allowed-tools: Read, Write
---

# Cálculo fiscal conductor — Art. 113-A LISR

## Régimen aplicable

**Art. 113-A LISR** (Sección III, Cap. II; régimen 625 en la CSF): personas físicas que prestan servicios o enajenan bienes a través de plataformas tecnológicas (transporte, entrega, hospedaje, ventas). Texto sin reformas desde DOF 08-12-2020 (Cámara de Diputados, consulta 2026-10-15).

**Retención automática** (sobre ingresos cobrados sin IVA):
- ISR: tasa fija por tipo de servicio (Art. 113-A LISR, vigente desde 2021)
- IVA: 50% del IVA cobrado = 8% del ingreso (Art. 18-J fr. II inciso a) LIVA)
- Sin RFC proporcionado a la plataforma: ISR 20% (Art. 113-C LISR) e IVA 100% (Art. 18-J LIVA)

## Tasas ISR retenidas por la plataforma (Art. 113-A)

| Servicio | Tasa ISR |
|---|---|
| Transporte terrestre de pasajeros y entrega de bienes (Uber, DiDi, Rappi) | 2.1% |
| Hospedaje | 4% |
| Enajenación de bienes y prestación de servicios | 2.5% en 2026 (LIF 2026 Art. 25 fr. VI sustituye el 1% de la fr. III) |

**Pago definitivo (Art. 113-B LISR)**: si solo obtiene ingresos por plataformas (o además sueldos e intereses) y en el ejercicio anterior no excedieron $300,000, puede optar porque la retención sea pago definitivo → no hay ISR adicional ni anual por esos ingresos. Requiere aviso al SAT dentro de los 30 días siguientes al primer ingreso, no permite deducciones y la opción dura 5 años. Si no opta o excede, la retención es **pago provisional acreditable** contra el pago mensual de su régimen (y en la anual).

IVA: con la opción del Art. 18-M LIVA la retención de 8% también puede ser pago definitivo (mismas condiciones); si no, se declara el IVA mensual acreditando lo retenido.

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
| Conductor también cobra servicios directos (fuera de la app) | Si el total ≤ $300,000 puede pagar esos ingresos con la misma tasa como pago definitivo (Art. 113-A, último párrafo); si no, régimen normal |
| Cambio de régimen mid-año | Recalcular por periodo |
| Conductor en RESICO PF con ingresos > $3.5M | Sale de RESICO (Art. 113-I) |
| Plataforma retuvo con tasa distinta a 2.1% | Revisar el CFDI de retenciones. `mp_resico_sat.resico_retencion_plataforma` con plataforma `uber`/`didi` calcula 2.1% (fr. I) |

## ⚠ Compliance

- Validar tasas del Art. 113-A LISR cada enero: cambian por reforma a la LISR o por la Ley de Ingresos del año (en 2026 la LIF subió bienes y servicios a 2.5%; transporte sigue en 2.1%)
- `vigencia_validada: false` — contador valida en declaración anual
- Las retenciones de la plataforma SÍ se declaran (acreditan) — no se omiten
