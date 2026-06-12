---
name: cruzar-bancos-vs-cfdis
description: Cruza extractos bancarios con CFDIs emitidos del año para detectar depósitos que NO tienen factura emitida. El SAT marca como ingreso fiscal todo depósito > $15,000 MXN/mes acumulado sin justificación documental, lo que puede generar discrepancia fiscal y multa. Este skill genera un reporte de depósitos sin facturar, su monto acumulado por mes, y recomendación de acción (facturar retroactivamente, registrar como préstamo, etc.). Requiere extractos bancarios del año (via mp_bancos_mx o subidos manualmente). Usar cuando el usuario pregunte por discrepancia, depósitos sin facturar, ingresos no declarados, cruce bancos. NO usar para conciliar pagos puntuales (mp_banxico_cep es para eso).
allowed-tools: Read, Write
---

# Cruzar bancos vs CFDIs

## Por qué importa

El SAT puede determinar **discrepancia fiscal** si tus depósitos bancarios exceden tus ingresos declarados. Penalización: ISR + actualización + recargos + multa hasta 100% del omitido.

Umbral común: $15,000 MXN/mes en depósitos sin justificar. Por debajo se considera tolerancia.

## Trigger

- "¿tengo depósitos sin facturar?"
- "cruza mis bancos con mis facturas"
- "detecta discrepancia fiscal"

## Inputs

- Extractos bancarios del año (12 meses, por cuenta)
- CFDIs emitidos del año (output de `recopilar-cfdis-anuales`)
- Tolerancia configurable (default $15,000 MXN/mes)

## Algoritmo

### Paso 1 — Normalizar depósitos

Por cada movimiento del extracto bancario:
- Si `tipo == "deposito"` Y `monto > 0`: candidato a ingreso
- Excluir transferencias internas entre cuentas propias (mismo titular)
- Excluir comisiones reversadas
- Excluir reembolsos
- Excluir préstamos identificados (concepto contiene "prestamo", "credito personal", etc.)

### Paso 2 — Matchear con CFDIs

Por cada depósito candidato:
- Buscar CFDI tipo I (ingreso) emitido en ventana ±30 días con `total == monto_deposito ± 1%`
- Si encuentra match: marcar como `facturado`
- Si no encuentra: marcar como `sin_facturar`

### Paso 3 — Acumular por mes

```
Mes      | Depósitos | Facturados | Sin facturar | Acumulado sin facturar
---------|-----------|------------|--------------|----------------------
Enero    |  $250,000 |  $230,000  |  $20,000     | $20,000
Febrero  |  $180,000 |  $180,000  |  $0          | $20,000
Marzo    |  $320,000 |  $295,000  |  $25,000     | $45,000
...
```

### Paso 4 — Alertar por exceder umbral

Si `acumulado_sin_facturar > 15,000 * meses_acumulados`: alerta crítica.

## Output

```json
{
  "ejercicio": 2025,
  "rfc_hash": "...",
  "total_depositos_mxn": "2500000.00",
  "total_facturado_mxn": "2350000.00",
  "total_sin_facturar_mxn": "150000.00",
  "porcentaje_sin_facturar": 6.0,
  "meses_con_exceso": [3, 7, 11],
  "depositos_sin_factura_top10": [
    {"fecha": "2025-03-15", "monto": "25000.00", "concepto_hash": "...", "banco_origen": "BBVA"}
  ],
  "recomendaciones": [
    "Facturar retroactivamente los depósitos de marzo si corresponden a servicios reales",
    "Documentar préstamos personales con contrato + transferencia origen",
    "Considerar abrir cuenta separada para movimientos no fiscales"
  ],
  "riesgo_discrepancia_fiscal": "MEDIO",
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Cliente paga con depósito + factura por monto distinto (anticipo + finiquito) | Buscar suma de CFDIs en ventana |
| Cliente paga vía OXXO/PayPal/Stripe | Buscar comisión de procesador antes del depósito limpio |
| Familiar deposita para gasto compartido | Tratar como préstamo familiar (no ingreso) si hay claridad |
| Banco etiqueta múltiples depósitos del mismo cliente como "varios" | Sumar agregado del mes |
| Sueldo (régimen 605) en cuenta del freelancer | NO contar como ingreso por honorarios |

## Dependencias

- `mp_bancos_mx` (extracto del año por cuenta — vía Playwright si disponible, o CSV subido)
- Output de `recopilar-cfdis-anuales`
- `mp_banxico_cep` (opcional) — para confirmar claves rastreo

## ⚠ Limitaciones

- Match exacto requiere disciplina en la facturación (mismos montos, fechas cercanas)
- Anticipos + finiquitos pueden generar falsos positivos
- Resultado es **indicativo**, no concluyente — un contador valida
- `vigencia_validada: false` por default
