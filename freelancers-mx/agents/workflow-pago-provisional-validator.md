---
name: workflow-pago-provisional-validator
description: Workflow validador específico para pre-pago provisional. Toma el cálculo de freelance-tax-mx y verifica consistencia (ingresos vs CFDIs emitidos, retenciones vs CFDIs con retención, gastos deducibles vs CFDIs recibidos, depósitos sin facturar). Genera reporte de discrepancias antes de presentar el pago. Útil para evitar errores que el SAT detecte después. Usar cuando el usuario diga valida mi pago provisional, revisa antes de presentar, doble-check pago provisional. NO usar para el cálculo en sí (eso es freelance-tax-mx).
allowed-tools: Read, Write
---

# Workflow: Pago provisional validator

Capa de validación entre el cálculo (`freelance-tax-mx`) y la presentación al SAT. Catch typical errors antes de generar línea de captura.

## Trigger

- Antes de presentar pago provisional mensual
- Cron día 14 (`pre-cierre-fiscal.sh`)
- Manual: "valida mi pago provisional antes de presentar"

## Inputs

- Output de `freelance-tax-mx` (cálculo)
- CFDIs del mes (`mp_facturama_extendido`)
- Extractos bancarios (`mp_bancos_mx`, opcional)

## Checks

### Check 1 — Ingresos declarados vs CFDIs emitidos cobrados (base flujo)

```python
ingresos_calculados = output_freelance_tax['ingresos_mes']
cfdis_cobrados_mes = sum(cfdi.total for cfdi in cfdis_emitidos_mes if cfdi.metodo == 'PUE')
cfdis_ppd_con_rep_mes = sum(rep.monto for rep in reps_mes)

esperado = cfdis_cobrados_mes + cfdis_ppd_con_rep_mes
if abs(ingresos_calculados - esperado) > 10:
    discrepancia()
```

### Check 2 — Retenciones a cuenta declaradas vs CFDIs con retención

```python
retenciones_cfdi = sum(c.retenciones.isr for c in cfdis_recibidos_mes if c.retenciones.isr > 0)
# + retenciones que sus clientes le aplicaron en CFDIs emitidos donde son PM
retenciones_recibidas = sum(c.retenciones.isr for c in cfdis_emitidos_mes if c.receptor_tipo == "PM")
if abs(output_freelance_tax['retenciones_acreditables'] - retenciones_recibidas) > 10:
    discrepancia()
```

### Check 3 — Gastos deducibles vs CFDIs recibidos validados

```python
gastos_declarados = output_freelance_tax['gastos_deducibles']
cfdis_recibidos_validados = sum(
    c.total for c in cfdis_recibidos_mes
    if c.estado != 'cancelado'
    and c.emisor_rfc not in lista_69b_definitivo
    and c.forma_pago in ['02','03','04','28']  # no efectivo para gastos > $2000
)
if abs(gastos_declarados - cfdis_recibidos_validados) > 100:
    discrepancia()
```

### Check 4 — Depósitos bancarios sin facturar

Cruce con extracto banco (si disponible):
```python
depositos = sum(m.monto for m in movimientos_mes if m.tipo == "deposito")
delta = depositos - ingresos_calculados
if delta > 15000:
    alerta_discrepancia_fiscal()
```

### Check 5 — CFDI tipo I uso "P01 por definir"

Si hay CFDIs con `uso == "P01"`: ⚠ usuario debe corregir antes de presentar (no es usable).

### Check 6 — RFC propio en lista 69-B

`mp_sat_portal.consultar_69b_efos(rfc_propio)`. Si está en presuntos: 🟡 alerta. Si definitivo: 🔴 abortar — no presentar.

## Output

```json
{
  "workflow": "pago_provisional_validator",
  "mes": "2026-05",
  "rfc_hash": "...",
  "checks_realizados": 6,
  "checks_pasados": 4,
  "checks_fallados": 2,
  "discrepancias": [
    {
      "check": "depositos_sin_facturar",
      "severidad": "alta",
      "delta_mxn": "23000.00",
      "recomendacion": "Documentar origen de depósitos antes de presentar"
    },
    {
      "check": "cfdi_uso_P01",
      "severidad": "critica",
      "cantidad": 1,
      "recomendacion": "Re-emitir el CFDI con uso correcto"
    }
  ],
  "veredicto": "NO_PRESENTAR_HASTA_RESOLVER",
  "siguiente_paso": "Resolver 2 discrepancias antes del día 17"
}
```

Veredictos posibles:
- `OK_PRESENTAR` — todo pasó
- `OK_CON_ADVERTENCIAS` — pasó con notas menores
- `NO_PRESENTAR_HASTA_RESOLVER` — discrepancias críticas

## Casos edge

| Caso | Acción |
|---|---|
| CFDI emitido el último día del mes | Si PUE: cuenta como ingreso. Si PPD: NO cuenta hasta REP. |
| Cliente paga el día 1 del mes siguiente lo emitido el último día del mes | Aplicar criterio flujo: cobrado siguiente mes |
| Depósito retroactivo > 30 días | Investigar origen, no asumir ingreso del mes en curso |
| Sin acceso a banco | Saltar Check 4 con warning |

## Dependencias

- `freelance-tax-mx` (output del cálculo)
- `mp_facturama_extendido` (CFDIs)
- `mp_sat_portal` (69-B)
- `mp_bancos_mx` (opcional)

## ⚠ Compliance

- `vigencia_validada: false` — contador valida antes de presentar
- Discrepancia "alta" no es bloqueo absoluto si el contador firma OK
- Discrepancia "crítica" SÍ es bloqueo — no presentar sin resolver
