---
name: cruzar-bancos-vs-cfdis
description: Cruza extractos bancarios con CFDIs emitidos del año para detectar depósitos que NO tienen factura emitida. El SAT puede presumir como ingreso los depósitos no registrados ni respaldados (Art. 59 fr. III CFF) y determinar discrepancia fiscal (Art. 91 LISR); los bancos le informan los depósitos en efectivo que excedan $15,000 al mes (Art. 55 fr. IV LISR). Este skill genera un reporte de depósitos sin facturar, su monto acumulado por mes, y recomendación de acción (facturar retroactivamente, registrar como préstamo, etc.). Requiere extractos bancarios del año (via mp_bancos_mx o subidos manualmente). Usar cuando el usuario pregunte por discrepancia, depósitos sin facturar, ingresos no declarados, cruce bancos. NO usar para conciliar pagos puntuales (mp_banxico_cep es para eso).
allowed-tools: Read, Write
---

# Cruzar bancos vs CFDIs

## Por qué importa

- **Discrepancia fiscal (Art. 91 LISR)**: si tus erogaciones (gastos, compras, depósitos) superan tus ingresos declarados, el SAT puede gravar la diferencia.
- **Presunción de ingresos (Art. 59 fr. III CFF)**: depósitos en tus cuentas que no correspondan a registros contables o CFDI pueden presumirse ingresos.
- Consecuencia: ISR omitido + actualización + recargos + multa de 55% a 75% del omitido (Art. 76 CFF).

No hay "tolerancia" legal. Los $15,000 mensuales son solo el umbral a partir del cual el banco reporta **depósitos en efectivo** al SAT (Art. 55 fr. IV LISR); úsalo como umbral de alerta, no como exención.

## Trigger

- "¿tengo depósitos sin facturar?"
- "cruza mis bancos con mis facturas"
- "detecta discrepancia fiscal"

## Inputs

- Extractos bancarios del año (12 meses, por cuenta)
- CFDIs emitidos del año (output de `recopilar-cfdis-anuales`)
- Umbral de alerta configurable (default $15,000 MXN/mes)

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
    "Emitir CFDI de los depósitos de marzo si corresponden a servicios reales (la emisión tardía puede tener multa — consultar contador)",
    "Documentar préstamos con contrato + transferencia origen; préstamos, donativos o premios que sumen más de $600,000 se informan en la anual (Art. 90 LISR)",
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
| Familiar deposita para gasto compartido | No es ingreso si se documenta; donativos entre familiares en línea recta están exentos (Art. 93 fr. XXIII) |
| Banco etiqueta múltiples depósitos del mismo cliente como "varios" | Sumar agregado del mes |
| Sueldo (régimen 605) en cuenta del freelancer | NO contar como ingreso por honorarios |

## Dependencias

- `mp_bancos_mx` (estado "sin verificar" en el catálogo): si falla, pedir al usuario CSV/PDF de sus estados de cuenta
- Output de `recopilar-cfdis-anuales`
- `mp_banxico_cep.banxico_cep_consultar_pago_por_clave` (opcional) — confirmar un SPEI por clave de rastreo

## ⚠ Limitaciones

- Match exacto requiere disciplina en la facturación (mismos montos, fechas cercanas)
- Anticipos + finiquitos pueden generar falsos positivos
- Resultado es **indicativo**, no concluyente — un contador valida
- `vigencia_validada: false` por default
