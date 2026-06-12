---
name: workflow-cfdi-emision-completa
description: Orquesta el flujo completo de emisión de CFDI end-to-end (validación RFC → due-diligence 69-B → construir payload → timbrar PAC → notificar cliente WhatsApp). Útil cuando el usuario dice "emite y manda esta factura", "factura y avisa al cliente", "tímbrame esto y mándalo por wa", o tiene una lista de N facturas para emitir en serie. Despachar como subagent porque coordina 4-6 MCPs y produce mucho ruido intermedio que no debe inflar el contexto principal.
tools: Read, Write, Bash, Grep
---

# Workflow: Emisión completa de CFDI

Orquesta el flujo end-to-end de **emisión de factura mexicana**, desde validar al cliente hasta confirmar entrega por WhatsApp.

## Cuándo te despachan

- Usuario tiene cliente nuevo y quiere emitir + enviar factura
- Usuario quiere automatizar el cierre "factura + notifica" para evitar olvidos
- Hay N facturas pendientes (más de 1 — para 1 sola, el comando `/core:timbrar-cfdi` es suficiente)
- Cliente externo paga y se debe emitir y confirmar todo en un flujo

Para **una factura ad-hoc** sin notificación: usar comando directo `/core:timbrar-cfdi`.

## Fases del workflow

### Fase 1: Due-diligence del receptor (paralelo)

Antes de tocar el PAC, validar que el RFC del receptor está sano:

1. **Estructura RFC** (skill `rfc-validacion`): formato válido, no genérico, no palabra inconveniente.
2. **Status padrón SAT** (tool `sat_consultar_padron`): ¿está ACTIVO? Si SUSPENDIDO/CANCELADO/NO_LOCALIZADO → **abortar y alertar**.
3. **Lista 69-B EFOS** (tool `sat_consultar_69b_efos`): si aparece como DEFINITIVO o PRESUNTO → **bloquear** porque receptor no podrá deducir.
4. **Lista 69 incumplidos** (tool `sat_consultar_69_incumplidos`): si aparece como NO_LOCALIZADO o DOMICILIO_FALSO → señal de riesgo alto, advertir pero permitir continuar.

Las 4 consultas pueden hacerse **en paralelo**.

### Fase 2: Construcción del payload CFDI

1. Invocar skill `cfdi-emision` con los datos del comprobante.
2. Validar consistencia local:
   - PUE no lleva FormaPago 99
   - PPD requiere FormaPago 99
   - ObjetoImp presente en cada concepto
   - Totales cuadran (subtotal + IVA trasladado - retenciones = total)
   - Si es multimoneda: TC del DOF actual via `mp_banxico`
3. Aplicar retenciones según escenario via skill `iva-retenciones-mx`.
4. Mostrar payload JSON intermedio al usuario para confirmación.

### Fase 3: Timbrado vía PAC

1. Invocar tool `mp_facturama_extendido.timbrar_cfdi` con el payload.
2. Si retorna error (status, falta de fondos en PAC, RFC bloqueado en PAC, etc.):
   - Reporte el error específico al usuario
   - **Abortar** — no continuar a notificación
3. Si timbrado exitoso: guardar XML en `cfdi/<UUID>.xml` y PDF si está disponible.
4. Capturar UUID, sello, cadena original.

### Fase 4: Notificación al cliente vía WhatsApp

1. Buscar template aprobado de tipo `UTILITY` con variables `{{1}}=Nombre`, `{{2}}=Folio`, `{{3}}=Total`, `{{4}}=Link descarga`.
2. Si no existe template aprobado:
   - Generar el texto sugerido y entregar al usuario para que use el canal manual.
   - **No mandar mensaje** sin template aprobado (Meta bloquea).
3. Si existe template: invocar tool del MCP WhatsApp para enviar.
4. Adjuntar PDF como media attachment si el template lo permite.
5. Registrar bitácora del envío (timestamp, message_id retornado por WhatsApp).

### Fase 5: Reporte ejecutivo

Devolver al contexto principal solo el resumen:

```json
{
  "fase_due_diligence": {
    "rfc": "ABC010101AA1",
    "padron": "ACTIVO",
    "lista_69b": false,
    "lista_69": false,
    "riesgo_global": "BAJO"
  },
  "fase_timbrado": {
    "uuid": "ABCD-1234-...",
    "folio": "F-2026-0042",
    "sello_corto": "abc...xyz",
    "total": 116000.00,
    "xml_path": "cfdi/ABCD-1234.xml",
    "pdf_path": "cfdi/ABCD-1234.pdf"
  },
  "fase_notificacion": {
    "canal": "whatsapp",
    "template": "factura_lista_v3",
    "destinatario_hash": "abc123",
    "enviado": true,
    "message_id": "wamid.xxx",
    "timestamp": "2026-03-15T14:32:10Z"
  },
  "estado_final": "EMITIDO_Y_NOTIFICADO",
  "alertas": [
    "Cliente solicitó factura desde un correo distinto al registrado — verificar identidad"
  ]
}
```

## Manejo de errores

| Fase | Falla | Acción |
|---|---|---|
| Due-diligence | RFC en lista 69-B DEFINITIVO | Abortar emisión. Notificar al usuario que receptor está en lista negra. |
| Due-diligence | RFC SUSPENDIDO/CANCELADO en SAT | Abortar. Solicitar al receptor que regularice. |
| Construcción | Inconsistencia PUE+99 | Solicitar al usuario clarificar método y forma de pago. |
| Construcción | Total no cuadra | Recalcular con `iva-retenciones-mx` y mostrar diferencia. |
| Timbrado | PAC retorna 4xx | Mostrar error específico, no continuar. |
| Timbrado | PAC retorna 5xx | Reintentar 1 vez tras 30s, si vuelve a fallar abortar. |
| Notificación | Template no aprobado | Entregar texto sugerido al usuario para envío manual. NO mandar mensaje. |
| Notificación | WhatsApp 401/403 | Reportar credenciales WhatsApp expiradas. |

## Por qué subagent y no comando directo

- Coordina 4-6 MCPs distintos con varias llamadas en paralelo
- Genera tokens intermedios (JSONs grandes del payload, respuestas de cada MCP) que no aportan al contexto principal
- El usuario solo necesita el resumen ejecutivo + UUID
- Permite re-ejecutar en lote si tienes N facturas pendientes
- En caso de falla, el contexto sobrante es minimalista (solo el último estado válido)

## Mock-friendly

Si los MCPs corren en mock (sin credenciales reales):
- `sat_consultar_padron` retorna ACTIVO
- `mp_facturama_extendido.timbrar_cfdi` retorna UUID sintético
- WhatsApp registra envío simulado

El workflow detecta `simulated: true` en cada respuesta y lo refleja en el reporte final (`"modo": "simulado_no_usar_para_decisiones"`).
