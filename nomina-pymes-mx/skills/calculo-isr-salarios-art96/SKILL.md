---
name: calculo-isr-salarios-art96
description: Cálculo ISR mensual sobre sueldos aplicando tarifa Art. 96 LISR + subsidio para el empleo. Distinto al cálculo de honorarios PFAE — sueldos tienen su tarifa específica (LISR Cap. I) y subsidio. Genera ISR a retener por el patrón en cada quincena. Usar cuando el usuario diga calcular isr empleado, retencion sueldo, art 96 LISR, subsidio empleo.
allowed-tools: Read, Write
---

# Cálculo ISR salarios Art. 96 LISR

## Lógica

### Paso 1: Convertir quincenal a mensual

Si la nómina es quincenal: sueldo mensual = sueldo_quincenal × 2 (aproximadamente, ajustar por días reales).

### Paso 2: Aplicar tarifa Art. 96 mensual

Buscar el tramo de la tabla (referencias/tarifa-art96-anual-2026.json) donde cae el sueldo mensual.

```python
def aplicar_tarifa_art96(sueldo_mensual: Decimal, tabla: list[dict]) -> Decimal:
    for tramo in tabla:
        if tramo["li"] <= sueldo_mensual <= tramo["ls"]:
            excedente = sueldo_mensual - tramo["li"]
            return tramo["cuota_fija"] + (excedente * tramo["tasa_excedente"])
    return Decimal("0")  # no debe pasar
```

### Paso 3: Aplicar subsidio para el empleo

Buscar tramo de tabla subsidio. Si sueldo ≤ tope: restar subsidio del ISR causado.

```python
def aplicar_subsidio_empleo(isr_causado: Decimal, sueldo_mensual: Decimal, tabla_subsidio: list[dict]) -> dict:
    for tramo in tabla_subsidio:
        if tramo["li"] <= sueldo_mensual <= tramo["ls"]:
            subsidio = Decimal(str(tramo["subsidio_mensual"]))
            isr_neto = isr_causado - subsidio

            if isr_neto >= 0:
                return {
                    "isr_a_retener": str(isr_neto),
                    "subsidio_aplicado": str(subsidio),
                    "subsidio_a_pagar_trabajador": "0"
                }
            else:
                # Subsidio > ISR → patrón paga la diferencia al trabajador
                return {
                    "isr_a_retener": "0",
                    "subsidio_aplicado": str(isr_causado),
                    "subsidio_a_pagar_trabajador": str(abs(isr_neto))
                }
    return {"isr_a_retener": str(isr_causado), "subsidio_aplicado": "0"}
```

### Paso 4: Convertir a quincenal

ISR mensual ÷ 2 = ISR a retener cada quincena (ajustar redondeos).

## Output

```json
{
  "empleado_id_hash": "...",
  "periodo": "2026-06-01_a_2026-06-15",
  "sueldo_quincenal_bruto": "15000.00",
  "sueldo_mensual_equivalente": "30000.00",
  "tramo_art96_aplicado": "31236.50 - 49233.00",
  "tasa_excedente": 0.2352,
  "isr_causado_mensual": "5004.12",
  "subsidio_empleo_aplicable": "0.00",
  "isr_a_retener_mensual": "5004.12",
  "isr_a_retener_quincena_actual": "2502.06",
  "vigencia_validada": false
}
```

## ⚠ Tarifa Art. 96 cambia ANUALMENTE

- RMF publicada en DOF cada diciembre
- Hook `actualizar-tarifa-isr-enero` (futuro) — alerta cada enero
- Tarifa vigente está en `references/tarifa-art96-anual-2026.json`
