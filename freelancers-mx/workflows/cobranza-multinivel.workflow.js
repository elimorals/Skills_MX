// Workflow ejecutable: cobranza-multinivel
//
// Escalación de cobranza con etapas D+3 → D+7 → D+15 → D+30 → D+45 según mora.
// Para CADA factura vencida del usuario, determina etapa correcta y envía mensajes.
//
// args: { rfc_emisor, fecha_corte? (default: hoy), enviar_real?: boolean (default: false dry-run) }

export const meta = {
  name: 'cobranza-multinivel',
  description: 'Cobranza escalonada por etapas D+3/D+7/D+15/D+30/D+45 con tono progresivamente formal: WhatsApp cordial → email recordatorio → llamada → carta formal → opcional extrajudicial. Personaliza por cliente.',
  whenToUse: 'Cron día 1 y 15 del mes / /freelancers:cobranza-mensual.',
  phases: [
    { title: 'Cartera', detail: 'identificar facturas vencidas no pagadas' },
    { title: 'Clasificación', detail: 'asignar etapa por días de mora' },
    { title: 'Personalización', detail: 'tono según historial cliente' },
    { title: 'Envío', detail: 'parallel: enviar mensajes correspondientes' },
    { title: 'Bitácora', detail: 'registrar comunicaciones + agendar siguiente acción' },
  ],
}

const { rfc_emisor, fecha_corte, enviar_real = false } = args || {}
if (!rfc_emisor) throw new Error('args.rfc_emisor requerido')

const corte = fecha_corte || new Date().toISOString().slice(0, 10)
log(`Cobranza ${rfc_emisor} corte ${corte} | enviar_real=${enviar_real}`)

// ============================================================
// FASE 1: Identificar cartera vencida
// ============================================================
phase('Cartera')

const cartera = await agent(
  `Lee cartera/${rfc_emisor}/cartera-vencida.json. Si no existe, consolida desde cfdi/ todos los CFDIs tipo I PPD emitidos en últimos 60 días que aún no tienen REP o status="cobrado".
   Para cada uno calcula: dias_mora = (${corte} - fecha_cfdi).
   Devuelve array: [{ uuid, cliente_rfc, cliente_nombre, monto, fecha_cfdi, dias_mora, historial_morosidad: "limpio"|"intermitente"|"reincidente" }]`,
  { label: 'identificar-cartera', phase: 'Cartera', schema: { type: 'object', properties: { facturas: { type: 'array' }, total_vencido: { type: 'number' } } } }
)

if (!cartera.facturas || cartera.facturas.length === 0) {
  return { status: 'sin_cartera_vencida', total_vencido: 0 }
}

log(`Cartera vencida: ${cartera.facturas.length} facturas, total $${cartera.total_vencido}`)

// ============================================================
// FASE 2: Clasificar por etapa de escalación
// ============================================================
phase('Clasificación')

const clasificacion = await agent(
  `Para cada factura en ${JSON.stringify(cartera.facturas).slice(0, 2000)} asigna etapa:
   - dias_mora >= 3 y < 7 → etapa_1_recordatorio_cordial
   - dias_mora >= 7 y < 15 → etapa_2_recordatorio_formal
   - dias_mora >= 15 y < 30 → etapa_3_propuesta_pago_parcial
   - dias_mora >= 30 y < 45 → etapa_4_carta_formal_requerimiento
   - dias_mora >= 45 → etapa_5_escalacion_extrajudicial

   Si cliente reincidente: subir 1 etapa.
   Si cliente limpio histórico: bajar 1 etapa (max etapa_1).

   Devuelve mismo array enriquecido con campo "etapa".`,
  { label: 'clasificar', phase: 'Clasificación', schema: { type: 'object', properties: { facturas_clasificadas: { type: 'array' } } } }
)

// Agrupar por etapa para envío paralelo
const porEtapa = {
  etapa_1: clasificacion.facturas_clasificadas?.filter(f => f.etapa === 'etapa_1_recordatorio_cordial') || [],
  etapa_2: clasificacion.facturas_clasificadas?.filter(f => f.etapa === 'etapa_2_recordatorio_formal') || [],
  etapa_3: clasificacion.facturas_clasificadas?.filter(f => f.etapa === 'etapa_3_propuesta_pago_parcial') || [],
  etapa_4: clasificacion.facturas_clasificadas?.filter(f => f.etapa === 'etapa_4_carta_formal_requerimiento') || [],
  etapa_5: clasificacion.facturas_clasificadas?.filter(f => f.etapa === 'etapa_5_escalacion_extrajudicial') || [],
}

// ============================================================
// FASE 3: Personalización por cliente
// ============================================================
phase('Personalización')

const mensajes = await agent(
  `Para cada factura clasificada, genera mensaje personalizado usando skill cobranza-seguimiento con:
   - Tono según etapa (1=cordial, 2=formal pero amable, 3=firme con propuesta, 4=severo, 5=legal)
   - Datos del cliente (nombre, monto, días de mora, link de pago si aplica)
   - Canal: WhatsApp para etapas 1-3, email para 4, carta formal PDF + WA para 5

   Devuelve array: [{ uuid, cliente, canal, mensaje, asunto?, adjuntos? }]`,
  { label: 'personalizar-mensajes', phase: 'Personalización', schema: { type: 'object', properties: { mensajes: { type: 'array' } } } }
)

// ============================================================
// FASE 4: Envío (en modo real) o preview (dry-run)
// ============================================================
phase('Envío')

let resultados = []
if (enviar_real) {
  resultados = await parallel(
    (mensajes.mensajes || []).map(m => () =>
      agent(
        `Envía mensaje vía ${m.canal} usando skill whatsapp-business-mx (si WA) o servicio email correspondiente. ${JSON.stringify(m)}`,
        { label: `envio-${m.uuid?.slice(0, 8)}`, phase: 'Envío', schema: { type: 'object', properties: { enviado: { type: 'boolean' }, message_id: { type: 'string' } } } }
      )
    )
  )
} else {
  log('Modo dry-run: NO se envía nada. Mensajes preparados:')
  resultados = mensajes.mensajes?.map(m => ({ uuid: m.uuid, canal: m.canal, dry_run: true })) || []
}

// ============================================================
// FASE 5: Bitácora + agendar siguiente acción
// ============================================================
phase('Bitácora')

await agent(
  `Persiste resultados en cobranza/${rfc_emisor}/${corte}-ciclo.json con:
   - Total facturas procesadas
   - Por etapa: cantidad + monto + status envío
   - Próxima fecha de revisión sugerida (typicamente +3 días)
   - Recordatorio en calendario para escalación si no hay respuesta`,
  { label: 'bitacora', phase: 'Bitácora' }
)

return {
  status: 'completado',
  fecha_corte: corte,
  total_facturas: cartera.facturas.length,
  total_monto: cartera.total_vencido,
  por_etapa: {
    cordial: porEtapa.etapa_1.length,
    formal: porEtapa.etapa_2.length,
    parcial: porEtapa.etapa_3.length,
    requerimiento: porEtapa.etapa_4.length,
    extrajudicial: porEtapa.etapa_5.length,
  },
  enviados: resultados.length,
  dry_run: !enviar_real,
}
