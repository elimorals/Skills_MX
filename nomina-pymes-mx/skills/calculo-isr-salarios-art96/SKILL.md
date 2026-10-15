---
name: calculo-isr-salarios-art96
description: Calcula el ISR a retener sobre sueldos y salarios con la tarifa del Art. 96 LISR 2026 (Anexo 8 RMF 2026, actualizada por inflación) y el subsidio para el empleo 2026 (15.02% de la UMA mensual, ingresos hasta $11,492.66). Distinto al ISR de honorarios PFAE o RESICO. Da la retención por quincena o mes. Usar cuando el usuario diga calcular isr empleado, retención de sueldo, isr nómina, art 96 LISR, tabla isr 2026, subsidio al empleo, subsidio para el empleo, cuánto ISR le quito a mi trabajador.
allowed-tools: Read, Write
---

# Cálculo ISR salarios Art. 96 LISR (2026)

Tablas vigentes y fuentes: `references/tarifa-subsidio-2026.md` (este skill).
⚠ El archivo del plugin `nomina-pymes-mx/references/tarifa-art96-anual-2026.json` y `subsidio-empleo-2026.json` tienen la tarifa 2023-2025 y la tabla de subsidio anterior a mayo 2024: **no los uses**.

## Paso 1: base mensual

Suma las percepciones gravadas del periodo (sueldo + gravado de horas extra, aguinaldo, prima vacacional, etc., ya descontada la parte exenta del Art. 93 LISR).

- Nómina mensual: aplica la tarifa mensual directa.
- Nómina quincenal/semanal: lo usual es la tarifa del periodo (mensual ÷ 30.4 × días del periodo, Art. 96 LISR y regla del Anexo 8) o mensualizar y dividir. Usa **el mismo método todo el año** y ajusta en el cálculo anual (Art. 97 LISR).

## Paso 2: tarifa mensual Art. 96 (2026)

```python
from decimal import Decimal as D

def isr_art96_mensual(base: D, tabla: list[dict]) -> D:
    # tabla ordenada por li ascendente (ver references/)
    tramo = [t for t in tabla if base >= t["li"]][-1]
    return (tramo["cuota_fija"] + (base - tramo["li"]) * tramo["tasa"]).quantize(D("0.01"))
```

## Paso 3: subsidio para el empleo 2026

Decreto DOF 31-12-2025 (fuente secundaria: IDC, El Contribuyente; confianza media en los centavos):

- Aplica si los ingresos del mes por sueldos son **≤ $11,492.66**.
- Monto mensual = **15.02% de la UMA mensual** (UMA 117.31 × 30.4 = $3,566.22) = **$535.65**.
- **Enero 2026**: 15.59% de la UMA mensual 2025 ($3,439.46) = $536.21.
- Periodos menores a un mes: subsidio mensual ÷ 30.4 × días del periodo.
- Desde mayo 2024 el subsidio **solo se acredita contra el ISR**; si el subsidio excede el ISR, **la diferencia no se entrega al trabajador** (ya no hay "subsidio a pagar").

```python
def aplicar_subsidio(isr_causado: D, ingreso_mes: D, subsidio_mes: D = D("535.65")) -> dict:
    if ingreso_mes > D("11492.66"):
        return {"isr_a_retener": isr_causado, "subsidio_aplicado": D("0")}
    aplicado = min(subsidio_mes, isr_causado)
    return {"isr_a_retener": isr_causado - aplicado, "subsidio_aplicado": aplicado}
```

En el CFDI de nómina, el subsidio causado se reporta en `OtrosPagos` (tipo 002) con `SubsidioCausado`.

## Ejemplos (recalculados con la tarifa 2026)

| Sueldo mensual | Tramo (LI) | ISR causado | Subsidio | ISR a retener |
|---|---|---|---|---|
| $10,000.00 | 7,168.52 @ 10.88% | 420.95 + 2,831.48 × 10.88% = **$729.02** | $535.65 | **$193.37** |
| $30,000.00 | 17,533.65 @ 21.36% | 1,856.84 + 12,466.35 × 21.36% = **$4,519.65** | 0 (excede tope) | **$4,519.65** (≈ $2,259.83 por quincena) |

## Output

```json
{
  "empleado_id_hash": "...",
  "periodo": "2026-06-01_a_2026-06-15",
  "sueldo_quincenal_bruto": "15000.00",
  "base_mensual_equivalente": "30000.00",
  "tramo_art96_aplicado": "17533.65 - 35362.83",
  "tasa_excedente": 0.2136,
  "isr_causado_mensual": "4519.65",
  "subsidio_empleo_aplicable": "0.00",
  "isr_a_retener_quincena_actual": "2259.83",
  "fuente_tarifa": "Anexo 8 RMF 2026, DOF 28-12-2025",
  "vigencia_validada": true
}
```

## ⚠ Vigencia y validación

- La tarifa se actualiza cuando la inflación acumulada supera 10% (Art. 152 LISR); la de 2026 usa factor 1.13213 (INPC nov-2025 / nov-2022). Revisa el Anexo 8 cada diciembre.
- El subsidio se fija por decreto anual; revisa el DOF de fin de año.
- Resultado orientativo: valida con tu contador o software de nómina antes de timbrar.
