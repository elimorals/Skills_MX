---
name: deducciones-conductor
description: Identifica gastos deducibles del conductor de plataforma cuando tributa con deducciones (régimen de plataformas 625 sin la opción de pago definitivo, o actividad empresarial 612): gasolina, mantenimiento, seguro, comisiones de la plataforma, apps y depreciación del auto (25% anual, tope $175,000). Aplica requisitos: CFDI, pago no efectivo (combustible siempre; demás gastos > $2,000). En RESICO PF o con retención como pago definitivo no hay deducciones. Usar cuando el usuario diga deducciones chofer, gastos deducibles conductor, qué puedo deducir de Uber, deducir gasolina, deducir mi carro.
allowed-tools: Read, Write
---

# Deducciones conductor de plataforma

## Cuándo aplica

- **RESICO PF (626)**: NO hay deducciones (ni de la actividad ni personales del Art. 151). Solo se acreditan las retenciones.
- **Plataformas (625) con opción 113-B** (retención como pago definitivo): NO hay deducciones.
- **Plataformas (625) sin la opción, o actividad empresarial (612)**: SÍ aplican las deducciones siguientes.

## Categorías deducibles

### 1. Gasolina
- **CRÍTICO**: requiere CFDI tipo I a tu RFC con uso G03
- Combustible: pago **siempre** con tarjeta, transferencia o monedero electrónico autorizado, aunque sea menor a $2,000 (Art. 27 fr. III LISR)
- Estaciones que dan CFDI: la mayoría — pedir antes de pagar
- 100% deducible

### 2. Mantenimiento del auto
- Cambios de aceite, alineación, balanceo
- Reparaciones
- Pago no-efectivo
- CFDI con RFC del conductor + uso G03
- 100% deducible

### 3. Seguro vehicular
- Anual, 100% deducible (prorrateado por mes)
- CFDI de la aseguradora con uso G03

### 4. Lavados de auto
- Si tienes CFDI: deducible
- Pequeñas cuantías en efectivo: NO deducible

### 5. Comisiones de plataforma
- Ya están restadas del neto recibido
- Documentar en declaración como gasto deducible
- CFDI: la plataforma debería emitir CFDI tipo I por su comisión

### 6. App subscriptions
- Waze Premium, otras apps de navegación
- Cuotas mensuales
- CFDI del proveedor

### 7. Depreciación del auto
- 25% anual (Art. 34 fr. VI LISR) sobre el monto original de la inversión
- Tope del monto deducible: $175,000 por automóvil (Art. 36 fr. II LISR); con valor mayor, depreciar solo sobre $175,000 (híbridos/eléctricos: $250,000)
- Solo si el auto está a tu nombre y se usa en la actividad; CFDI de compra

## Output

```json
{
  "rfc_hash": "...",
  "mes": "2026-06",
  "regimen": "612_PFAE",
  "categorias": {
    "gasolina": {"cfdis": 12, "monto_mxn": "4800.00", "validados": 12},
    "mantenimiento": {"cfdis": 1, "monto_mxn": "1500.00", "validados": 1},
    "seguro": {"prorrata_mensual_mxn": "850.00"},
    "lavados": {"con_cfdi_mxn": "200.00", "sin_cfdi_excluidos_mxn": "300.00"},
    "comisiones_plataforma": {"monto_mxn": "5300.00"},
    "apps": {"monto_mxn": "199.00"},
    "depreciacion": {"moi_tope_mxn": "175000.00", "prorrata_mensual_mxn": "3645.83"}
  },
  "total_deducible_mxn": "16494.83",
  "ingresos_mes_mxn": "26500.00",
  "utilidad_fiscal_estimada_mxn": "10005.17",
  "advertencias": [
    "$300 en lavados pagados en efectivo NO deducibles",
    "Verificar que todos los CFDIs tengan tu RFC + forma de pago no efectivo",
    "Auto de $250,000: depreciación limitada a $175,000 × 25% / 12 = $3,645.83 al mes"
  ],
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Auto rentado | Renta sí deducible (con CFDI) — no depreciación |
| Auto a nombre del cónyuge | NO deducible (debe estar a tu nombre) |
| Gasolina sin CFDI al momento | Pedir el CFDI en el portal de la gasolinera dentro del plazo que fije (suele ser el mismo mes) |
| Conductor en RESICO PF o con opción 113-B | NO aplica este skill — no hay deducciones |

## ⚠ Compliance

- Pago no efectivo: gastos > $2,000 (Art. 27 fr. III LISR) y combustible siempre
- `vigencia_validada: false` — contador valida
- Al 25% anual el auto se deprecia por completo en 4 años; después ya no hay depreciación
