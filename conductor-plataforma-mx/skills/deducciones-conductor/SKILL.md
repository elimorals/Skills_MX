---
name: deducciones-conductor
description: Identifica gastos deducibles para el conductor de plataforma bajo régimen RESICO PF (limitado) o PFAE (completo). Cubre gasolina (con CFDI), mantenimiento del auto (con CFDI), seguro vehicular, lavados, comisiones de la plataforma (ya descontadas pero a documentar), y app subscriptions (Waze Premium, etc.). Aplica reglas específicas: gasto en efectivo > $2k NO deducible. Usar cuando el usuario diga deducciones chofer, gastos deducibles conductor, qué puedo deducir uber.
allowed-tools: Read, Write
---

# Deducciones conductor de plataforma

## Aplica si régimen 612 PFAE

En 626 RESICO PF: las deducciones NO aplican (régimen simplificado). Solo se permiten deducciones personales Art. 151 (médicos, etc.) y las retenciones acreditables.

En 612 PFAE: SÍ aplican las siguientes deducciones.

## Categorías deducibles

### 1. Gasolina
- **CRÍTICO**: requiere CFDI tipo I a tu RFC con uso G03
- Pago debe ser con tarjeta / transferencia (NO efectivo si > $2,000)
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
- 25% anual (5% × 5 años) sobre valor de factura
- Solo si auto está a tu nombre
- Documentado con factura original

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
    "depreciacion": {"prorrata_mensual_mxn": "5208.00"}
  },
  "total_deducible_mxn": "18057.00",
  "ingresos_mes_mxn": "26500.00",
  "utilidad_fiscal_estimada_mxn": "8443.00",
  "advertencias": [
    "$300 en lavados pagados en efectivo NO deducibles",
    "Verificar que todos los CFDIs tengan tu RFC + forma de pago no efectivo"
  ],
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Auto rentado | Renta sí deducible (con CFDI) — no depreciación |
| Auto a nombre del cónyuge | NO deducible (debe estar a tu nombre) |
| Gasolina en estación sin facturador | Solicitar CFDI por correo después (vence 30 días) |
| Conductor en RESICO PF | NO aplica este skill — RESICO no permite deducciones acumulables |

## ⚠ Compliance

- Forma de pago NO efectivo para > $2,000 = regla SAT
- `vigencia_validada: false` — contador valida
- Si auto > 9 años: depreciación 0 (ya completó vida útil fiscal)
