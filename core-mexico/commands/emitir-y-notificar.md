---
description: Workflow end-to-end de emisión de CFDI con due-diligence, timbrado y notificación al cliente por WhatsApp. Despacha el subagent workflow-cfdi-emision-completa.
argument-hint: "[cliente RFC + descripción del comprobante a emitir]"
allowed-tools: Read, Write, Edit, Bash, Task
---

# /core:emitir-y-notificar

Emite una factura completa end-to-end y confirma entrega: $ARGUMENTS

## Lo que hace

1. **Due-diligence del receptor** (parallel):
   - Valida RFC estructural (skill `rfc-validacion`)
   - Consulta padrón SAT (tool `sat_consultar_padron`)
   - Verifica lista 69-B EFOS (tool `sat_consultar_69b_efos`)
   - Verifica lista 69 incumplidos (tool `sat_consultar_69_incumplidos`)
2. **Construye payload CFDI** con validaciones locales (skill `cfdi-emision` + `iva-retenciones-mx`).
3. **Timbra vía PAC** con `mp_facturama_extendido.timbrar_cfdi`.
4. **Notifica al cliente** vía WhatsApp con template aprobado UTILITY.
5. **Reporte ejecutivo** con UUID + estado de cada fase.

## Cómo lo ejecuta

Despacha al subagent `workflow-cfdi-emision-completa` (en `core-mexico/agents/`) para no inflar el contexto principal con los intercambios MCP.

## Cuándo usar este comando vs los individuales

| Caso | Comando recomendado |
|---|---|
| Factura ad-hoc rápida sin notificación | `/core:timbrar-cfdi` |
| Factura completa (timbra + notifica + bitácora) | `/core:emitir-y-notificar` |
| Lote de 5+ facturas en serie | `/core:emitir-y-notificar` por cada una (o crear lista) |
| Cliente nuevo (primera factura) | `/core:emitir-y-notificar` (corre due-diligence) |

## Output esperado

JSON resumen con UUID, folio, status de cada fase y alertas.

## Modo simulado

Si los MCPs corren sin credenciales reales, el workflow:
- Marca `simulated: true` en el reporte
- No envía mensajes reales por WhatsApp
- Usa UUID sintético del PAC mock
- Sugiere setup de credenciales en docs/integracion-pac.md y docs/integracion-whatsapp.md
