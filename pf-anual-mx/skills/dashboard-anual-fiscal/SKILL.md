---
name: dashboard-anual-fiscal
description: Muestra el status fiscal del año en curso para una persona física en México. Reporta ingresos acumulados, deducciones capturadas, pagos provisionales hechos, ISR estimado al cierre, deducciones personales potenciales, y semáforo de alerta por mes. Útil al inicio de cada sesión durante el ciclo de declaración (enero-abril) y para checkpoints trimestrales del año en curso. Usar cuando el usuario pregunte como va mi declaración anual, status fiscal del año, dashboard año fiscal, status declaración. NO usar para pago provisional mensual (eso es cierre-fiscal-mensual del core-mexico).
allowed-tools: Read, Write
---

# Dashboard anual fiscal — PF México

Vista consolidada del año fiscal para decidir acciones antes del cierre de abril.

## Cuándo activar

- "¿cómo va mi declaración anual?"
- "muéstrame el status fiscal del año"
- "¿cuánto voy a pagar / cuánto saldo a favor?"
- "dashboard año fiscal"
- Inicio de sesión durante temporada (marzo-abril)

## Información a producir

### 1. Cabecera

```
RFC: <RFC>
Ejercicio: <2025>
Régimen: <PFAE 612 | RESICO PF 626 | Asalariado + honorarios>
Estado del archivo: borrador | calculado | presentado
Última actualización: <fecha>
Deadline: 30 abril <ejercicio+1>
```

### 2. Ingresos acumulados

| Mes | Facturado | Cobrado | Diferencia |
|---|---|---|---|
| Ene | $50,000 | $35,000 | $15,000 (PPD pendiente) |
| ... | ... | ... | ... |

**Total año en curso**: $X,XXX,XXX

### 3. Deducciones

| Categoría | CFDIs | Monto |
|---|---|---|
| Gastos operativos | 47 | $250,000 |
| Honorarios pagados | 12 | $80,000 |
| Inversiones (depreciables) | 3 | $90,000 |

⚠ Pendientes: <N> CFDIs sin clasificar → invocar `identificar-deducciones-personales`

### 4. Pagos provisionales hechos

| Mes | Línea captura | Monto pagado |
|---|---|---|
| Ene | LC-... | $5,000 |

**Total acreditable**: $X,XXX

### 5. Estimación ISR anual

```
Ingresos acumulables:          $XXX,XXX
- Deducciones acumulables:     -$XXX,XXX
- Deducciones personales:      -$XXX,XXX (tope: menor de 5 UMA anuales o 15% de ingresos)
= Base gravable:                $XXX,XXX
× Tarifa anual Art. 152 LISR del ejercicio (Anexo 8 RMF)
= ISR anual:                    $XXX,XXX
- Pagos provisionales:          -$XXX,XXX
- ISR retenido:                 -$XXX,XXX
= Saldo a favor / a pagar:      $XX,XXX
```

### 6. Semáforo de riesgos

- ✅ Tarjeta verde: ingresos, deducciones, retenciones documentadas y cuadran
- 🟡 Amarillo: depósitos bancarios sin CFDI que los respalde (el SAT puede presumirlos ingreso, Art. 59 fr. III CFF)
- 🔴 Rojo: CFDIs con RFC en lista 69-B definitivo → re-clasificar como NO deducibles

### 7. Acciones recomendadas

1. Si saldo a favor > $50,000: prepararse para revisión SAT
2. Si faltan CFDIs deducibles del año: invocar `identificar-deducciones-personales`
3. Si hay depósitos sin facturar: invocar `cruzar-bancos-vs-cfdis`
4. Usar la tarifa anual del ejercicio correcto: 2025 y 2026 son distintas (Anexo 8 RMF 2026 la actualizó) — ver `calculadora-isr-anual`
5. RESICO PF: no aplica tarifa Art. 152 ni deducciones; usar tabla Art. 113-F

## Data sources

- `mp_sat_ws` (`sat_ws_solicitar_descarga` → `sat_ws_verificar_solicitud` → `sat_ws_descargar_paquete`) — CFDIs emitidos+recibidos; requiere e.firma, real sin validar. Sin e.firma: ZIP descargado por el usuario del portal SAT
- `mp_banxico.banxico_get_uma` — UMA del ejercicio (5 × UMA × 365 para tope de deducciones personales)
- Pagos provisionales del tracker local del `core-mexico` (cierre-fiscal-mensual)
- `mp_bancos_mx` — extractos (estado "sin verificar" en el catálogo; si falla, pedir CSV/PDF al usuario)

## Output esperado

JSON estructurado + tabla markdown legible:

```json
{
  "rfc_hash": "...",
  "ejercicio": 2025,
  "regimen": "PFAE_612",
  "ingresos_acumulables_mxn": "1234567.89",
  "deducciones_acumulables_mxn": "234567.00",
  "deducciones_personales_aplicables_mxn": "50000.00",
  "tope_aplicado": "no_alcanzado",
  "utilidad_fiscal_mxn": "950000.89",
  "tarifa_aplicada": "Art_152_LISR_2025",
  "isr_anual_calculado_mxn": "218604.21",
  "pagos_provisionales_acumulados_mxn": "175000.00",
  "diferencia_mxn": "43604.21",
  "resultado": "SALDO_A_PAGAR",
  "fecha_limite_presentacion": "2026-04-30",
  "vigencia_validada": false,
  "alertas": ["depósitos sin facturar Q1", "CFDI RFC 69-B detectado"],
  "siguientes_pasos": ["..."]
}
```

## Cuándo NO usar

- Para pago provisional mensual → usar `cierre-fiscal-mensual` del core-mexico
- Para declaración de PM → distinta tarifa + cálculos
- Para impuestos estatales → fuera de scope (predial, ISN)

## ⚠ Compliance

Marca SIEMPRE `vigencia_validada: false`. La declaración anual tiene implicaciones legales — no actuar sobre el output sin validación de contador certificado.
