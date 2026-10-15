---
name: optimizador-deducciones-personales
description: Coach proactivo durante el año en curso para maximizar deducciones personales (Art. 151 LISR) antes de cerrar diciembre. Distinto a identificar-deducciones-personales del pf-anual-mx que opera sobre CFDIs ya emitidos. Este skill sugiere oportunidades NO aprovechadas (ej. tu seguro GMM lo pagas en efectivo — cámbialo a tarjeta) y simula impacto fiscal de cada cambio. Usar cuando el usuario diga cómo deducir más, optimizar deducciones, qué me falta deducir, ahorrar impuestos personales, deducciones antes de fin de año, aportación voluntaria AFORE deducible. No aplica a RESICO PF.
allowed-tools: Read, Write
---

# Optimizador deducciones personales

## Filosofía

Las deducciones personales son una oportunidad **anual** — debes accionar antes del 31 diciembre. Este skill opera durante el año (no en la declaración).

## Patrones comunes que se pueden corregir

### 1. Pagos médicos en efectivo
- Médicos / dentistas / hospitales NO aplican si pagas en efectivo, por cualquier monto (Art. 151 fr. I)
- **Sugerencia**: pagar con tarjeta de débito/crédito o transferencia y pedir CFDI con uso D01

### 2. Donativos sin elegir donataria autorizada
- Donar a fundación NO autorizada SAT = NO deducible
- **Sugerencia**: verificar con `mp_donatarias_sat.donatarias_consultar` (directorio SAT; no incluye revocaciones posteriores al corte) y donar antes de fin de año. Tope: 7% de ingresos acumulables del año anterior, dentro del tope global

### 3. Aportaciones voluntarias a AFORE sin maximizar
- Tope independiente: 10% de ingresos acumulables, sin exceder 5 UMA anuales ($214,090.75 en 2026); fuera del tope global
- **Sugerencia**: si no usas tope, aportar antes del 31 de diciembre (subcuenta de aportaciones complementarias o plan personal de retiro; CFDI/constancia D06)

### 4. Seguros GMM sin contratar
- Prima de seguro GMM deducible (dentro del tope global: menor de 5 UMA anuales o 15% de ingresos)
- **Sugerencia**: evaluar GMM si los gastos médicos son recurrentes; la decisión es de cobertura, no solo fiscal

### 5. Colegiaturas pagadas en efectivo
- Colegiaturas preescolar a bachillerato (Decreto DOF 26-12-2013), tope por alumno: preescolar $14,200, primaria $12,900, secundaria $19,900, profesional técnico $17,100, bachillerato $24,500; fuera del tope global
- **Sugerencia**: pagar con medio bancarizado y pedir CFDI uso D10 con CURP del alumno

### 6. Hipoteca sin pedir constancia intereses
- El banco emite constancia anual de intereses reales — si no llega, pedirla
- **Sugerencia**: solicitarla al inicio del año siguiente, antes de presentar la anual

## Algoritmo

```python
def analizar_oportunidades(historial_anual_actual) -> list[Oportunidad]:
    oportunidades = []

    # Pagos médicos efectivo
    medicos_efectivo = sum(c.total for c in cfdis_medicos if c.forma_pago == "01")
    if medicos_efectivo > 0:
        oportunidades.append({
            "tipo": "pagos_medicos_efectivo",
            "monto_no_deducible": str(medicos_efectivo),
            "ahorro_potencial_isr": str(medicos_efectivo * tasa_marginal),  # tasa marginal Art. 152 del usuario
            "accion": "Cambiar forma de pago a no-efectivo"
        })

    # Aporte AFORE sin maximizar
    aporte_actual = ...
    tope = min(ingresos * 0.10, 5 * UMA_ANUAL)
    if aporte_actual < tope:
        oportunidades.append({
            "tipo": "aporte_afore_sin_maximizar",
            "deficit_mxn": str(tope - aporte_actual),
            "ahorro_potencial_isr": str((tope - aporte_actual) * tasa_marginal),
            "accion": f"Aportar ${tope - aporte_actual} antes del 31 diciembre"
        })

    return oportunidades
```

## Output

```json
{
  "rfc_hash": "...",
  "ejercicio": 2026,
  "mes_actual": 6,
  "meses_restantes_para_cerrar": 6,
  "tasa_marginal_supuesta": 0.30,
  "oportunidades": [
    {
      "tipo": "pagos_medicos_efectivo",
      "descripcion": "$15,000 en pagos médicos pagados en efectivo no aplicarán",
      "ahorro_potencial_isr_mxn": "4500.00",
      "prioridad": "alta",
      "accion": "Pagar próximos médicos con tarjeta + obtener CFDI"
    },
    {
      "tipo": "aporte_afore_sin_maximizar",
      "descripcion": "$12,000 disponibles antes del tope de aportaciones al retiro",
      "ahorro_potencial_isr_mxn": "3600.00",
      "prioridad": "media",
      "accion": "Aportar $12,000 a AFORE antes del 31 diciembre 2026"
    },
    {
      "tipo": "gmm_no_contratado",
      "descripcion": "Gastos médicos recurrentes ($35k en el año): evaluar GMM; prima estimada $18k deducible",
      "ahorro_potencial_isr_mxn": "5400.00",
      "prioridad": "media",
      "accion": "Cotizar GMM 2027 — premium estimado $18k anuales"
    }
  ],
  "ahorro_total_potencial_mxn": "13500.00",
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Cliente en RESICO PF | NO aplica deducciones personales: informar y terminar (salvo que también tenga sueldos) |
| Cliente con saldo a favor previo | Optimización adicional puede generar saldo aún mayor (alerta auditoría) |
| Cliente sin ingresos formales | Deducciones no aplican (sin base sobre la que descontar) |

## ⚠ Compliance

- UMA 2026 = $117.31 (INEGI, vigente desde 01-02-2026); tope global 2026 = menor de $214,090.75 o 15% de ingresos
- `vigencia_validada: false` — contador valida en anual
