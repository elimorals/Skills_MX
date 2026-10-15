---
name: dashboard-donataria-mes
description: Status mensual de una donataria autorizada - donativos recibidos por canal (transferencia, tarjeta, efectivo, especie), donantes nuevos y recurrentes, proyectos activos, CFDI de donativo emitidos vs. pendientes, indicadores de cumplimiento (gastos de administración ≤ 5%, ingresos no relacionados ≤ 10%), efectivo > $100,000 a informar y próximos plazos (15-feb, transparencia en mayo). Usar cuando el usuario diga dashboard donataria mes, dashboard_donataria_mes, resumen mensual ONG, status de donativos, ayuda con dashboard donataria mes.
allowed-tools: Read, Write
---

# Dashboard donataria mes

## Bloques

1. **Donativos del mes** por canal y tipo (dinero/especie), nacional/extranjero.
2. **Donantes**: nuevos, recurrentes, sin RFC (CFDI a XAXX010101000, no deducible).
3. **CFDI**: emitidos con complemento Donatarias vs. donativos sin comprobante (skill `cfdi-donativo-d04`).
4. **Cumplimiento** (acumulado del ejercicio):
   - Gastos de administración / donativos ≤ 5% (Art. 138 RLISR; verificar).
   - Ingresos por actividades no relacionadas / ingresos totales ≤ 10% (Art. 80 LISR).
   - Donativos en efectivo > $100,000 del mes → informe al día 17 (skill `reporte-mensual-efectivo-100k`).
5. **Estado de la autorización**: `donatarias_consultar` (MCP `mp_donatarias_sat`) y próximos plazos (skill `renovacion-autorizacion-anual`).

## Output esperado

```json
{
  "operation": "dashboard-donataria-mes",
  "data": {
    "periodo": "2026-09",
    "donativos_total_mxn": "185000.00",
    "por_canal": {"transferencia": "120000.00", "tarjeta": "40000.00", "efectivo": "25000.00", "especie": "0.00"},
    "donantes_nuevos": 6,
    "cfdi_pendientes": 2,
    "pct_gastos_admin_ytd": 0.042,
    "pct_no_relacionados_ytd": 0.03,
    "efectivo_mayor_100k_a_informar": 0,
    "autorizacion_en_directorio_sat": true,
    "proximo_plazo": "2027-02-15 declaración anual informativa"
  },
  "vigencia_validada": false
}
```

Comprobación: 120,000 + 40,000 + 25,000 + 0 = 185,000.

## Casos edge

- Datos incompletos → solicitar al usuario. Modo mock por default si no hay credenciales.
- Indicador cerca del límite (≥ 4% gastos admin, ≥ 9% no relacionados): alerta temprana.

## Dependencias

- `core-mexico` (CFDI, RFC, mxn-formato)
- MCP `mp_donatarias_sat`; tracker local
