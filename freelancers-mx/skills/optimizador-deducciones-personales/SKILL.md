---
name: optimizador-deducciones-personales
description: Coach proactivo durante el año en curso para maximizar deducciones personales (Art. 151 LISR) antes de cerrar diciembre. Distinto a identificar-deducciones-personales del pf-anual-mx que opera sobre CFDIs ya emitidos. Este skill sugiere oportunidades NO aprovechadas (ej. tu seguro GMM lo pagas en efectivo — cámbialo a tarjeta) y simula impacto fiscal de cada cambio. Usar cuando el usuario diga cómo deducir más, optimizar deducciones, qué me falta deducir, ahorrar impuestos personales.
allowed-tools: Read, Write
---

# Optimizador deducciones personales

## Filosofía

Las deducciones personales son una oportunidad **anual** — debes accionar antes del 31 diciembre. Este skill opera durante el año (no en la declaración).

## Patrones comunes que se pueden corregir

### 1. Pagos médicos en efectivo
- Médicos / dentistas / hospitales NO aplican si pagas efectivo
- **Sugerencia**: pagar con tarjeta de débito/crédito (no efectivo > $2k)

### 2. Donativos sin elegir donataria autorizada
- Donar a fundación NO autorizada SAT = NO deducible
- **Sugerencia**: lista de donatarias autorizadas y donar antes de fin de año

### 3. Aportaciones voluntarias a AFORE sin maximizar
- Tope independiente 10% ingresos ó 5 UMAs anuales
- **Sugerencia**: si no usas tope, aportar antes de diciembre

### 4. Seguros GMM sin contratar
- Prima de seguro GMM = 100% deducible
- **Sugerencia**: si gastos médicos > $20k/año, conviene contratar GMM

### 5. Colegiaturas pagadas en efectivo
- Colegiatura solo para hijos (preescolar a bachillerato) deducible — bachillerato $24,500 MXN/año tope
- **Sugerencia**: pagar con tarjeta y obtener CFDI

### 6. Hipoteca sin pedir constancia intereses
- Bank emite constancia anual — algunos no la mandan, hay que pedirla
- **Sugerencia**: solicitar antes del 31 enero del año siguiente

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
            "ahorro_potencial_isr": str(medicos_efectivo * 0.30),
            "accion": "Cambiar forma de pago a no-efectivo"
        })

    # Aporte AFORE sin maximizar
    aporte_actual = ...
    tope = min(ingresos * 0.10, 5 * UMA_ANUAL)
    if aporte_actual < tope:
        oportunidades.append({
            "tipo": "aporte_afore_sin_maximizar",
            "deficit_mxn": str(tope - aporte_actual),
            "ahorro_potencial_isr": str((tope - aporte_actual) * 0.30),
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
      "descripcion": "$12,000 disponibles antes del tope 5 UMAs",
      "ahorro_potencial_isr_mxn": "3600.00",
      "prioridad": "media",
      "accion": "Aportar $12,000 a AFORE antes del 31 diciembre 2026"
    },
    {
      "tipo": "gmm_no_contratado",
      "descripcion": "Gastos médicos del año $35k justifican contratar GMM",
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
| Cliente en RESICO PF | Solo aplica deducciones personales — mismas reglas Art. 151 |
| Cliente con saldo a favor previo | Optimización adicional puede generar saldo aún mayor (alerta auditoría) |
| Cliente sin ingresos formales | Deducciones no aplican (sin base sobre la que descontar) |

## ⚠ Compliance

- Topes UMA cambian anualmente — validar UMA vigente
- `vigencia_validada: false` — contador valida en anual
