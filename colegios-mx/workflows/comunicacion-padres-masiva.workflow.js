// Workflow ejecutable: comunicacion-padres-masiva
//
// Envía comunicado a padres de familia segmentado por grado/grupo/nivel.
// Cuida tasa de entrega, lectura, opt-out. Usa templates aprobables Meta.
//
// args: { tipo: "calendario"|"junta"|"calificaciones"|"cobranza"|"emergencia",
//         segmentacion: { grado?, grupo?, nivel?, todos? },
//         contenido, requiere_confirmacion?: bool }

export const meta = {
  name: 'comunicacion-padres-masiva',
  description: 'Comunicación masiva a padres con segmentación + template Meta aprobado + opt-out respetado + tracking de entrega/lectura/respuesta + reporte ejecutivo. Crítico cuidar LFPDPPP (datos menores) y no usar para marketing puro.',
  whenToUse: 'Apertura ciclo, juntas bimestrales, calificaciones, recordatorios cobranza, emergencias (suspensión clases por contingencia).',
  phases: [
    { title: 'Segmentación', detail: 'filtrar destinatarios + respetar opt-outs' },
    { title: 'Validación template', detail: 'verificar APPROVED en Meta' },
    { title: 'Envío por lotes', detail: 'pipeline en bloques de 50 con rate limiting' },
    { title: 'Tracking', detail: 'entrega + lectura + respuesta' },
    { title: 'Reporte', detail: 'tasa entrega + respuestas + opt-outs nuevos' },
  ],
}

const { tipo, segmentacion = { todos: true }, contenido, requiere_confirmacion = false } = args || {}
if (!tipo || !contenido) throw new Error('args requeridos: { tipo, contenido }')

log(`Comunicación masiva | tipo=${tipo} | segmentación=${JSON.stringify(segmentacion)}`)

phase('Segmentación')

const audiencia = await agent(
  `Filtra padres de familia según segmentación ${JSON.stringify(segmentacion)}:
   - Si todos=true → toda la base de padres
   - Si grado/grupo/nivel → solo padres de alumnos en esos grupos
   - SIEMPRE excluir padres en opt-out (LFPDPPP)
   - SIEMPRE excluir números con etiqueta "no_marketing" si tipo="calificaciones" o "junta"

   Devuelve { destinatarios: [{nombre_padre, telefono_wa, alumnos_relacionados: [...]}], total, excluidos_opt_out }`,
  { label: 'segmentar', phase: 'Segmentación', schema: { type: 'object', properties: { destinatarios: { type: 'array' }, total: { type: 'number' }, excluidos_opt_out: { type: 'number' } } } }
)

if (audiencia.total === 0) {
  return { status: 'audiencia_vacia', razon: 'Sin destinatarios tras segmentación' }
}

log(`Audiencia: ${audiencia.total} (excluidos por opt-out: ${audiencia.excluidos_opt_out})`)

phase('Validación template')

const template = await agent(
  `Selecciona template aprobable Meta correspondiente al tipo "${tipo}":
   - calendario → "utility_padres_calendario"
   - junta → "utility_padres_junta_grado"
   - calificaciones → "utility_padres_calificaciones_bimestre"
   - cobranza → "utility_padres_recordatorio_colegiatura"
   - emergencia → "utility_padres_emergencia"

   Verifica status del template via mp_meta_whatsapp_cloud.get_template_status:
   - Si APPROVED → continuar
   - Si PENDING → abortar (no enviar)
   - Si REJECTED → abortar y alertar admin

   Devuelve { template_name, status, variables_requeridas: [...] }`,
  { label: 'validar-template', phase: 'Validación template', schema: { type: 'object', properties: { status: { type: 'string' }, template_name: { type: 'string' } } } }
)

if (template.status !== 'APPROVED') {
  return { status: 'template_no_aprobado', detalle: template, accion: 'Esperar aprobación Meta o usar template alternativo' }
}

phase('Envío por lotes')

const resultadosEnvio = await pipeline(
  // Dividir en lotes de 50 para rate limiting de Meta (1000/seg max, conservador)
  chunks(audiencia.destinatarios, 50),
  (lote, idx) => agent(
    `Envía lote ${idx + 1} (${lote.length} destinatarios) usando mp_meta_whatsapp_cloud.send_template_message con:
     - template: ${template.template_name}
     - parámetros por destinatario (nombre, alumno, contenido específico)
     - rate limit interno: 5 mensajes/segundo

     Devuelve { enviados: number, fallos: number, message_ids: [...] }`,
    { label: `lote-${idx + 1}`, phase: 'Envío por lotes', schema: { type: 'object', properties: { enviados: { type: 'number' }, fallos: { type: 'number' } } } }
  )
)

const totalEnviados = resultadosEnvio.filter(Boolean).reduce((s, r) => s + (r.enviados || 0), 0)
const totalFallos = resultadosEnvio.filter(Boolean).reduce((s, r) => s + (r.fallos || 0), 0)

phase('Tracking')

await agent(
  `Programa tracking de status de cada mensaje enviado:
   - SENT → DELIVERED → READ → REPLIED (opcionales)
   - Webhook handler de Meta WA actualizará bitácora cuando lleguen eventos
   - Plazo de tracking: 48 horas tras envío
   - Si requiere_confirmacion=${requiere_confirmacion}: marcar pendientes los sin respuesta a las 24h`,
  { label: 'tracking-inicial', phase: 'Tracking' }
)

phase('Reporte')

const fecha = new Date().toISOString().slice(0, 10)
await agent(
  `Genera reporte en comunicaciones-masivas/${fecha}/reporte-${tipo}.md con:
   - Audiencia objetivo: ${audiencia.total} (${audiencia.excluidos_opt_out} opt-out)
   - Enviados: ${totalEnviados} | Fallos: ${totalFallos}
   - Tasa de entrega: ${((totalEnviados / audiencia.total) * 100).toFixed(1)}%
   - Tracking pendiente: 48 horas para lectura/respuesta
   - Si tipo="cobranza": recordatorio cron en D+3 para seguimiento etapa 2`,
  { label: 'reporte', phase: 'Reporte' }
)

return {
  tipo,
  segmentacion,
  audiencia_total: audiencia.total,
  enviados: totalEnviados,
  fallos: totalFallos,
  tasa_entrega_pct: ((totalEnviados / audiencia.total) * 100).toFixed(1),
  template_usado: template.template_name,
  tracking_activo_hasta: new Date(Date.now() + 48 * 3600 * 1000).toISOString(),
  reporte: `comunicaciones-masivas/${fecha}/reporte-${tipo}.md`,
}

function chunks(arr, size) {
  const result = []
  for (let i = 0; i < arr.length; i += size) {
    result.push(arr.slice(i, i + size))
  }
  return result
}
