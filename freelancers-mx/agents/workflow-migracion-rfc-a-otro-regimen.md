---
name: workflow-migracion-rfc-a-otro-regimen
description: Workflow guía para migrar un RFC entre regímenes fiscales (típico: 612 PFAE → 626 RESICO PF si baja a < $3.5M, o 626 RESICO → 612 PFAE si supera el tope). Cubre validación de elegibilidad, presentación aviso al SAT (Forma RFC), efectos fiscales del cambio, fecha de aplicación. Usar cuando el usuario diga cambiar regimen, migrar de PFAE a RESICO, pasar a otro regimen.
allowed-tools: Read, Write
---

# Workflow migración RFC entre regímenes

## Cambios típicos

### A. 612 PFAE → 626 RESICO PF
**Cuándo conviene**: ingresos < $3.5M anuales y operaciones simples.

**Elegibilidad RESICO PF**:
- Ingresos < $3,500,000 MXN/año
- Solo personas físicas
- No socio/accionista de PM
- No realizar actividades inmobiliarias de compraventa (sí arrendamiento)

### B. 626 RESICO PF → 612 PFAE
**Cuándo**:
- Superas tope $3.5M
- Necesitas deducciones (RESICO no permite)
- Vas a ser socio de PM

## Fases del workflow

### 1. Validar elegibilidad
Verificar contra reglas del régimen destino.

### 2. Calcular impacto fiscal
- Comparar tarifa actual vs nueva con simulación
- Identificar deducciones que perderías o ganarías

### 3. Presentar aviso
- Portal SAT → Trámites → RFC → Actualización de actividades y obligaciones
- Forma: RX (aviso de actualización)
- Plazo: dentro del mes siguiente al cambio
- Fecha efecto: típicamente el 1ro del mes siguiente

### 4. Ajustar configuración interna
- CFDI: actualizar régimen emisor
- Tracker fiscal: aplicar nuevas reglas a partir de fecha efecto
- Calendario obligaciones: ajustar fechas (RESICO presenta mensual, PFAE pago provisional + anual)

### 5. Periodo de transición
- Operaciones del mes de migración: criterio caso a caso
- Mejor: empezar nuevo régimen 1 enero del año siguiente para no mezclar

### 6. Output

```json
{
  "workflow": "migracion_regimen",
  "rfc_hash": "...",
  "regimen_origen": "612_PFAE",
  "regimen_destino": "626_RESICO_PF",
  "fecha_efecto_propuesta": "2027-01-01",
  "elegibilidad_validada": true,
  "ahorro_isr_estimado_anual_mxn": "45000.00",
  "aviso_sat_presentado": false,
  "siguiente_paso": "Presentar Forma RX antes de 2026-12-31",
  "vigencia_validada": false
}
```

## ⚠ Caso edge

Cambio mid-año = calcular ISR por periodos separados en declaración anual.
