---
name: workflow-cobranza-multinivel
description: Orquesta la cobranza escalonada de cartera vencida (D+3 WhatsApp suave, D+7 email formal, D+15 llamada/seguimiento, D+30 carta formal de requerimiento, D+45 escalación legal). Despachar cuando el usuario dice "córremos la cobranza del mes", "actualiza cartera vencida", "manda recordatorios a los morosos", "procesar cartera del mes pasado". Subagent porque toca N facturas en paralelo y produce mucho ruido por cada cliente.
tools: Read, Write, Bash, Grep
---

# Workflow: Cobranza escalonada multinivel

Procesa la cartera vencida de un freelancer/PyME en una sola pasada: detecta CFDIs PPD sin pago conciliado, calcula días de vencimiento, escala automáticamente al nivel correspondiente, ejecuta la acción de cobranza y registra bitácora.

## Cuándo te despachan

- Diario o semanal: corrida automática de cobranza
- Cierre de mes: revisar cartera completa antes de declaración
- Después de procesar pagos: identificar quién todavía falta
- Cliente nuevo en demora: empezar el ciclo

## Inputs aceptados

1. **Lista de CFDIs PPD emitidos** sin pago conciliado (de bitácora local)
2. **Fecha de corte** (default: hoy) — para calcular días desde emisión
3. **Filtro opcional**: cliente específico, monto mínimo, días mínimos

## Política de escalación

| Días vencido | Nivel | Acción | Canal |
|---|---|---|---|
| 0-3 | Sin acción | Esperar | — |
| 4-7 | Nivel 1 — recordatorio suave | "Hola, te recordamos tu factura X" | WhatsApp UTILITY template |
| 8-14 | Nivel 2 — recordatorio formal | "Tu factura X tiene 10 días vencidos" | Email + WhatsApp |
| 15-29 | Nivel 3 — llamada + seguimiento | Marcar para llamada del usuario + mensaje | WhatsApp + flag en bitácora |
| 30-44 | Nivel 4 — carta formal de requerimiento | Documento legal: requerimiento extrajudicial | Email + WhatsApp + PDF adjunto |
| 45+ | Nivel 5 — escalación legal | Marcar para abogado + suspender servicios | Bitácora + alerta crítica al usuario |

⚠ La carta formal de requerimiento (nivel 4) requiere revisión legal antes de uso real. Plantillas en `freelancers-mx/skills/cobranza-seguimiento` son scaffolding — validar con abogado mercantilista antes de mandar.

## Fases del workflow

### Fase 1: Inventario de cartera vencida

1. Leer bitácora local de CFDIs emitidos PPD (de los últimos 90 días).
2. Cruzar contra registro de pagos conciliados (workflow-pago-conciliacion).
3. Para cada CFDI sin pago: calcular días desde fecha de emisión.
4. Construir lista ordenada por días vencidos descendiente.

### Fase 2: Verificación de status del CFDI

Para cada CFDI vencido, verificar (en paralelo):

1. **Status SAT** (tool `sat_verificar_cfdi_uuid`): que no haya sido cancelado.
2. **Status RFC receptor** (tool `sat_consultar_padron`): ACTIVO/SUSPENDIDO.
3. **Pago tardío reciente** (tool `mp_banxico_cep.consultar_pago_por_clave` si el cliente reportó clave): por si llegó pago sin webhook.

Si el CFDI fue cancelado: **remover de cartera**, no escalar más.

### Fase 3: Asignar nivel por CFDI

Aplicar la matriz de escalación. Saltarse niveles ya ejecutados (revisar bitácora de cobranza).

### Fase 4: Ejecutar acciones por nivel

#### Nivel 1-2 (WhatsApp + email)

1. Buscar template aprobado tipo UTILITY para recordatorio del nivel.
2. Variables: nombre cliente, folio CFDI, monto, días vencidos, link payment_link (si existe).
3. Si no hay template aprobado: entregar texto sugerido para envío manual.
4. Para nivel 2: mandar también email con copia del PDF del CFDI.

#### Nivel 3 (llamada manual + mensaje)

1. Enviar WhatsApp escalado con tono más firme.
2. Crear ítem en lista de "llamadas pendientes" para el usuario.
3. Sugerir guión de llamada en bitácora.

#### Nivel 4 (carta formal de requerimiento)

1. Generar PDF de **requerimiento extrajudicial** usando skill `cobranza-seguimiento`.
2. Adjuntar:
   - Copia del CFDI original
   - Bitácora de comunicaciones previas (timestamps + canales)
   - Tasa moratoria aplicable (6% mercantil Art. 362 CCom)
3. Enviar por WhatsApp + email.
4. **Marcar bitácora**: "carta-formal-enviada: <fecha>".

#### Nivel 5 (escalación legal)

1. Alerta crítica al usuario.
2. Sugerir:
   - Suspender servicios al cliente
   - Reportar a Buró de Crédito si aplica
   - Consultar abogado mercantilista
   - Considerar Juicio Ejecutivo Mercantil (vía rápida)
3. **No mandar nada automático** — todo requiere acción del usuario.

### Fase 5: Bitácora consolidada

Por cada CFDI procesado, anotar:
- `nivel_asignado`: 1-5
- `accion_ejecutada`: "whatsapp_enviado" | "email_enviado" | "carta_pdf_generada" | "alerta_legal"
- `timestamp`
- `message_id` (si aplica)
- `proxima_revision`: fecha sugerida (ej. +7 días para nivel 2)

### Fase 6: Reporte ejecutivo

```json
{
  "fecha_corrida": "2026-03-15",
  "total_cfdis_vencidos": 23,
  "por_nivel": {
    "nivel_1": 5,
    "nivel_2": 8,
    "nivel_3": 6,
    "nivel_4": 3,
    "nivel_5": 1
  },
  "monto_total_cartera_vencida_mxn": 487500.00,
  "monto_critico_45_dias_mxn": 95000.00,
  "acciones_automaticas_ejecutadas": 19,
  "acciones_que_requieren_usuario": 4,
  "alertas": [
    "Cliente XYZ tiene $95k vencidos 50+ días — considerar escalación legal",
    "Cliente ABC tiene 3 CFDIs cancelados — remover de cartera y revisar relación"
  ],
  "siguiente_corrida_sugerida": "2026-03-22"
}
```

## Manejo de errores

| Caso | Acción |
|---|---|
| Template WhatsApp no aprobado para el nivel | Entregar texto al usuario para envío manual. No bloquear el batch. |
| Cliente respondió "ya pagué" pero sin webhook | Marcar como "pago_reportado_sin_validar" — workflow-pago-conciliacion lo resolverá. |
| CFDI cancelado | Remover de cartera. Si había escalación previa, anotar resolución. |
| RFC receptor SUSPENDIDO | Alertar — el receptor puede estar en problemas legales. |
| Carta formal sin abogado revisor | Generar y advertir explícitamente: "Esta carta es scaffolding — validar con abogado antes de enviar". |
| Tasa moratoria > techo legal | Reportar al usuario y sugerir consulta legal. |

## Por qué subagent

- Procesa N facturas en paralelo (puede ser 50-500 en una cartera grande)
- Cada CFDI requiere 3-5 verificaciones cruzadas
- Genera muchos mensajes/PDFs intermedios
- El usuario solo necesita el resumen + lista de acciones que requieren su input

## Mock-friendly

Sin credenciales reales:
- Tasas moratorias hardcoded
- Templates sugeridos (no enviados)
- PDFs generados con marca de agua "SIMULADO"
- Bitácora se escribe normal pero todas las entradas llevan `simulated: true`

## Validación legal pendiente

⚠ Para producción real con clientes externos:
- Revisión legal de plantilla de requerimiento (nivel 4)
- Confirmar tasa moratoria 6% mercantil Art. 362 CCom vigente
- Política de suspensión de servicios debe estar en contrato con cliente
- Reportar a Buró requiere autorización del cliente firmada
