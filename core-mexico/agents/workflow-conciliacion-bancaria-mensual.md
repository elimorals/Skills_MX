---
name: workflow-conciliacion-bancaria-mensual
description: Workflow mensual que concilia movimientos bancarios con CFDIs emitidos y recibidos del mes para detectar discrepancias (depósitos sin facturar, CFDIs sin cobro, pagos pendientes de aplicar). Orquesta mp_bancos_mx (extractos), mp_facturama_extendido (CFDIs), y opcionalmente mp_banxico_cep (claves SPEI). Genera reporte normalizado de conciliación. Usar cuando el usuario diga concilia mis bancos, conciliación mensual, qué cuadra y qué no, cruza bancos con facturas. NO confundir con due-diligence-cliente (que es de un cliente individual).
allowed-tools: Read, Write, Bash
---

# Workflow: Conciliación bancaria mensual

Cruza extractos bancarios contra CFDIs y movimientos esperados. Produce reporte de discrepancias para corregir antes del cierre fiscal.

## Cuándo correr

- Día 10-12 del mes (después de día de pago típico, antes del pre-cierre día 14)
- Después de webhook de pago no conciliado
- A petición ad-hoc del usuario

## Fases

### Fase 1 — Determinar mes a conciliar

Default: mes anterior completo (`mes_obligacion = today - 1 mes`).
Override: argumento del usuario.

### Fase 2 — Descargar extractos bancarios

Por cada cuenta registrada en tracker:
- `mp_bancos_mx.bancos_listar_movimientos(banco, cuenta, dias=35)` (margen extra)
- Filtrar a movimientos del mes a conciliar
- Normalizar: depósitos, retiros, comisiones

### Fase 3 — Descargar CFDIs del mes

- `mp_facturama_extendido.listar_cfdis(emisor_rfc, mes_obligacion)` — emitidos
- `mp_facturama_extendido.listar_cfdis_recibidos(rfc, mes_obligacion)` — recibidos
- Separar PUE (cobrados en emisión) vs PPD (pendientes REP)

### Fase 4 — Cruce

Por cada CFDI tipo I (ingreso emitido):
1. Si PUE: buscar depósito con `monto == total ± 1%` en ventana ±5 días
2. Si PPD: buscar REP emitido + depósito asociado
3. Marcar como `conciliado` o `pendiente_conciliacion`

Por cada depósito sin CFDI asociado:
- Si > $15,000 MXN: 🔴 alerta discrepancia
- Si ≤ $15,000 MXN: 🟡 normal pero documentar

### Fase 5 — Reporte

```json
{
  "workflow": "conciliacion-bancaria-mensual",
  "mes_conciliado": "2026-05",
  "rfc_hash": "...",
  "totales": {
    "cfdis_emitidos": 24,
    "cfdis_cobrados": 21,
    "cfdis_pendientes_cobro": 3,
    "depositos_bancarios": 28,
    "depositos_conciliados_con_cfdi": 22,
    "depositos_sin_facturar": 6,
    "monto_sin_facturar_mxn": "12500.00",
    "alerta_discrepancia": false
  },
  "items_pendientes": [
    {"cfdi_uuid": "...", "monto": "5000", "razon": "PUE sin depósito encontrado"},
    {"deposito_id": "...", "monto": "8000", "razon": "Depósito sin CFDI"}
  ],
  "recomendaciones": [
    "Verificar 3 CFDIs PUE sin cobro: emitir nota crédito o ajustar fecha",
    "6 depósitos pequeños sin facturar — documentar origen (préstamos, reembolsos)"
  ],
  "siguiente_paso": "Resolver discrepancias antes del pre-cierre del día 14",
  "vigencia_validada": false
}
```

### Fase 6 — Persistir

Guardar en `~/.local/share/plugins-mx/conciliacion/<rfc_hash>/<mes>.json`.

## Casos edge

| Caso | Acción |
|---|---|
| Sin credenciales `mp_bancos_mx` | Modo mock — pedir al usuario subir CSV manualmente |
| CFDI cancelado mid-mes | Excluir del cálculo de pendientes |
| Cliente paga con depósito a cuenta distinta a la registrada | Pedir agregar cuenta al tracker |
| Cliente paga upfront varios meses | Aplicar prorrateado o consultar |
| Depósito en USD | Convertir con TC del día via `mp_banxico` |

## Dependencias

- `mp_bancos_mx` (extractos)
- `mp_facturama_extendido` (CFDIs)
- `mp_banxico_cep` (opcional, claves SPEI para match exacto)
- `mp_banxico` (TC USD si aplica)

## ⚠ Compliance

- Hashear cuentas CLABE y RFC en logs
- Reporte queda en local, NO se comparte con terceros
- `vigencia_validada: false` — contador valida en cierre fiscal
