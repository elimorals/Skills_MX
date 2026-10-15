---
name: recopilar-cfdis-anuales
description: Orquesta la descarga masiva de CFDIs emitidos y recibidos por una persona física durante un ejercicio fiscal completo (12 meses). Usa el web service de descarga masiva (mp_sat_ws, requiere e.firma) o, si no hay e.firma o falla, pide al usuario el ZIP del portal SAT. Parsea XMLs, clasifica por tipo (I=ingreso, E=egreso, T=traslado, P=pago, N=nómina), valida UUIDs contra el SAT, excluye CFDIs cuyo RFC emisor o receptor esté en lista 69-B definitivo, y entrega un dataset normalizado listo para calcular ISR anual. Usar cuando el usuario diga descargar CFDIs del año, recopilar facturas 2025, descarga masiva, bajar CFDIs del SAT, obtener todos los CFDIs. NO usar para descarga mensual (usar mp_sat_ws directamente).
allowed-tools: Read, Write
---

# Recopilar CFDIs anuales — orquestador

## Trigger

- "descarga todos mis CFDIs del año <ejercicio>"
- "recopilar facturas 2025"
- "necesito todos los CFDIs para mi declaración"

## Plan

### Phase 1 — Verificación de e.firma

1. Invocar `mp_sat_portal.sat_verificar_efirma_vigente(rfc)`
2. Si vencida (días_para_vencer ≤ 0): abortar + alertar
3. Si vence en < 30 días: warning pero continuar
4. Si modo mock: avisar al usuario que los datos serán sintéticos

### Phase 2 — Descarga emitidos (12 meses)

`mp_sat_ws` está en estado "real sin validar" (firma y autenticación probadas con e.firma de prueba; solicitud/descarga con e.firma real sin validar). Por cada mes 1-12:
- `mp_sat_ws.sat_ws_solicitar_descarga(...)` con tipo emitidos → guardar `id_solicitud`
- `sat_ws_verificar_solicitud(id_solicitud)` cada 30 min hasta que haya paquetes
- `sat_ws_descargar_paquete(id_paquete)` → ZIP con XML
- Si cualquier paso falla: pedir al usuario el ZIP desde el portal SAT (Factura electrónica → Consultar facturas emitidas/recibidas) y continuar con Phase 4

### Phase 3 — Descarga recibidos (12 meses)

Idéntico pero `tipo="recibidos"`.

### Phase 4 — Parsing y normalización

Por cada XML:
- Extraer: UUID, fecha, RFC emisor/receptor, total, subtotal, IVA, retenciones, tipo, uso CFDI, forma pago, método pago
- Validar estatus contra `mp_sat_portal.sat_verificar_cfdi_uuid`
- Si UUID cancelado: marcar `estado_cancelacion`
- Si RFC del emisor/receptor en lista 69-B definitivo (`mp_sat_portal.sat_consultar_69b_efos`, real validado en vivo): marcar `excluir_deducciones=true` + alerta

### Phase 5 — Dataset normalizado

```json
{
  "ejercicio": 2025,
  "rfc_hash": "...",
  "total_cfdis_emitidos": 245,
  "total_cfdis_recibidos": 387,
  "total_excluidos_69b": 3,
  "ingresos_mxn": "1234567.89",
  "egresos_mxn": "234567.00",
  "iva_trasladado_acumulado_mxn": "12345.67",
  "iva_acreditable_mxn": "23456.78",
  "isr_retenido_acumulado_mxn": "8500.00",
  "advertencias": [
    "3 CFDIs con RFC emisor en lista 69-B definitivo — excluidos",
    "5 CFDIs con UUID cancelado — verificar"
  ],
  "siguiente_skill": "identificar-deducciones-personales",
  "vigencia_validada": false
}
```

### Phase 6 — Hand-off

Sugerir al usuario el siguiente skill según contexto:
- Si quiere deducciones personales: `identificar-deducciones-personales`
- Si quiere cruzar con bancos: `cruzar-bancos-vs-cfdis`
- Si quiere calcular directo: `calculadora-isr-anual`

## Tiempo estimado

- Modo mock: < 30 seg
- Modo real (con e.firma + SAT real): 4-24h por la cola SAT (descargas son async)

## Casos edge

| Caso | Acción |
|---|---|
| Usuario sin e.firma | Pedir que suba ZIPs del portal SAT manualmente |
| Muchos CFDIs en un mes | El SAT divide la respuesta en varios paquetes: descargar todos |
| SAT down durante descarga | Reintentar polling con backoff exponencial |
| RFC emisor en 69-B presunto (no definitivo) | Incluir + warning, no excluir |
| CFDI tipo "T" (traslado) | Excluir del cálculo de ingresos/egresos |
| CFDI tipo "P" (pago — REP) | Tratar como confirmación de cobro de un PPD previo |

## ⚠ Compliance

- Hashear RFC, UUIDs y cantidades cuando se logueen
- Nunca commitear XMLs reales — guardar en `~/.local/share/plugins-mx/cfdis/<RFC_HASH>/<ejercicio>/`
- LFPDPPP: aviso de privacidad debe estar firmado por el usuario antes de invocar este skill
