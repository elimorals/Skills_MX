// Workflow ejecutable: cierre-fiscal-mensual
//
// Convierte el markdown declarativo `core-mexico/agents/workflow-cierre-fiscal-mensual.md`
// a un script ejecutable del skill `Workflow` con phase()/parallel()/pipeline().
//
// Invocar con: Workflow({scriptPath: "core-mexico/workflows/cierre-fiscal-mensual.workflow.js", args: {...}})
//
// Inputs esperados en `args`:
//   { rfc: string, ejercicio: number, mes: number, regimen: "RESICO_PF"|"PFAE"|"PM_GENERAL",
//     incluir_buzon?: boolean, incluir_aspel?: boolean }

export const meta = {
  name: 'cierre-fiscal-mensual',
  description: 'Cierre fiscal mensual: descarga CFDIs SAT + bancos + TCs, cruza ingresos/gastos, calcula pago provisional ISR/IVA, detecta alertas críticas, genera reporte ejecutivo.',
  whenToUse: 'Día 14 del mes (cron) o manual: "cerrar mes", "pago provisional marzo", "reporte fiscal".',
  phases: [
    { title: 'Recopilación', detail: 'parallel: CFDIs emitidos/recibidos + Buzón + TCs DOF + UMA + INPC' },
    { title: 'Cruce', detail: 'CFDIs emitidos vs depósitos bancarios y CFDIs recibidos vs cargos' },
    { title: 'Detección', detail: 'parallel: 69-B, retenciones no acreditadas, depósitos efectivo >$15k, multimoneda anómalo' },
    { title: 'Cálculo', detail: 'pago provisional ISR + IVA según régimen' },
    { title: 'Validación', detail: 'verificar pago > $50k con segundo método' },
    { title: 'Output', detail: 'reporte fiscal/YYYY-MM.md + alertas WhatsApp + recordatorio día 17' },
  ],
}

const { rfc, ejercicio, mes, regimen, incluir_buzon = true, incluir_aspel = false } = args || {}

if (!rfc || !ejercicio || !mes || !regimen) {
  throw new Error('args requeridos: { rfc, ejercicio, mes, regimen }')
}

log(`Cierre fiscal — RFC ${rfc} — ${ejercicio}-${String(mes).padStart(2, '0')} — régimen ${regimen}`)

// ============================================================
// FASE 1: Recopilación paralela
// ============================================================
phase('Recopilación')

const recopilacion = await parallel([
  () => agent(
    `Descarga masiva de CFDIs emitidos del RFC ${rfc} para ${ejercicio}-${mes}. Usa mp_sat_portal.descargar_cfdi_masivo con tipo="emitidos". Si retorna solicitud_id sin lista (async SAT), retorna {pending: true, solicitud_id}.`,
    { label: 'cfdis-emitidos', phase: 'Recopilación', schema: cfdiBatchSchema() }
  ),
  () => agent(
    `Descarga masiva de CFDIs recibidos del RFC ${rfc} para ${ejercicio}-${mes}. Usa mp_sat_portal.descargar_cfdi_masivo con tipo="recibidos".`,
    { label: 'cfdis-recibidos', phase: 'Recopilación', schema: cfdiBatchSchema() }
  ),
  ...(incluir_buzon ? [
    () => agent(
      `Consulta Buzón Tributario para RFC ${rfc} y devuelve notificaciones del mes ${ejercicio}-${mes} con días restantes para responder cada una.`,
      { label: 'buzon', phase: 'Recopilación', schema: buzonSchema() }
    ),
  ] : []),
  () => agent(
    `Obtén TCs DOF USD/EUR del mes ${ejercicio}-${mes} usando mp_banxico.get_tc_serie. Devuelve array por día hábil.`,
    { label: 'tcs-mes', phase: 'Recopilación', schema: tcSerieSchema() }
  ),
  () => agent(
    `Obtén UMA vigente para ${ejercicio} (mp_banxico.get_uma) e INPC del mes ${ejercicio}-${mes} (mp_banxico.get_inpc).`,
    { label: 'uma-inpc', phase: 'Recopilación', schema: umaInpcSchema() }
  ),
  ...(incluir_aspel ? [
    () => agent(
      `Lee balanza de comprobación de Aspel/ContPAQi para ${ejercicio}-${mes} usando mp_aspel_contpaqi. Devuelve saldos contables relevantes.`,
      { label: 'aspel-balanza', phase: 'Recopilación', schema: balanzaSchema() }
    ),
  ] : []),
])

const [cfdisEmitidos, cfdisRecibidos, buzon, tcsMes, umaInpc, balanza] = [
  recopilacion[0],
  recopilacion[1],
  incluir_buzon ? recopilacion[2] : null,
  recopilacion[incluir_buzon ? 3 : 2],
  recopilacion[incluir_buzon ? 4 : 3],
  incluir_aspel ? recopilacion[incluir_buzon ? 5 : 4] : null,
]

// Si SAT marca pending, abortar elegantemente y agendar retry
if (cfdisEmitidos?.pending || cfdisRecibidos?.pending) {
  log('⏸ SAT procesando descarga masiva (async). Reintentar en 1-4 hrs.')
  return {
    status: 'pendiente_datos_sat',
    solicitud_emitidos: cfdisEmitidos?.solicitud_id,
    solicitud_recibidos: cfdisRecibidos?.solicitud_id,
    siguiente_intento: 'cron retry en 2hrs',
  }
}

// ============================================================
// FASE 2: Cruce ingresos vs gastos
// ============================================================
phase('Cruce')

const crucesIngresos = await agent(
  `Cruza CFDIs emitidos (${cfdisEmitidos.total || 0} comprobantes) vs depósitos bancarios del mes. Identifica:
   - depositos_sin_cfdi: pagos recibidos sin factura emitida (potencial ingreso no facturado)
   - cfdis_sin_cobro: facturas emitidas sin depósito (cartera vencida)
   - matches: pareo correcto (1:1 o 1:N)
   Si no hay datos de banco (incluir_aspel=${incluir_aspel}), reporta solo CFDIs.`,
  { label: 'cruce-ingresos', phase: 'Cruce', schema: cruceSchema() }
)

const cruceGastos = await agent(
  `Cruza CFDIs recibidos vs cargos bancarios del mes para identificar:
   - cargos_sin_cfdi: gastos sin factura → NO deducibles
   - cfdis_sin_pago: facturas recibidas no pagadas en el mes (PPD pendientes)
   - matches`,
  { label: 'cruce-gastos', phase: 'Cruce', schema: cruceSchema() }
)

// ============================================================
// FASE 3: Detección de alertas críticas (parallel — independientes)
// ============================================================
phase('Detección')

const alertas = await parallel([
  () => agent(
    `Revisa los ${cfdisRecibidos.total || 0} CFDIs recibidos. Para cada RFC emisor, consulta mp_sat_portal.consultar_69b_efos. Identifica los que están en lista 69-B (presunción de inexistencia) — sus CFDIs NO son deducibles. Devuelve cantidad + monto total no deducible.`,
    { label: 'detector-69b', phase: 'Detección', schema: alertasSchema() }
  ),
  () => agent(
    `Identifica retenciones recibidas que NO se acreditaron en pagos provisionales previos del ejercicio ${ejercicio}. Para RESICO PF la retención típica es 1.25% por PMs receptoras; para PFAE 10%+10.67% ISR+IVA.`,
    { label: 'retenciones-no-acreditadas', phase: 'Detección', schema: alertasSchema() }
  ),
  () => agent(
    `Revisa depósitos bancarios del mes y suma los > $15,000 MXN en efectivo. Es discrepancia ISR (Art. 91 LISR). Devuelve total + lista.`,
    { label: 'depositos-efectivo', phase: 'Detección', schema: alertasSchema() }
  ),
  () => agent(
    `Identifica CFDIs en moneda extranjera. Para cada uno, verifica que TC usado esté dentro de ±2% del TC DOF correspondiente (TCs del mes: ${JSON.stringify(tcsMes).slice(0, 200)}). Reporta los que se salgan.`,
    { label: 'multimoneda-tc', phase: 'Detección', schema: alertasSchema() }
  ),
  () => agent(
    `Identifica CFDIs PPD (Pago en Parcialidades Diferido) emitidos en meses previos que aún no tienen su CFDI tipo P (REP) correspondiente. El plazo es máximo 5 días naturales después de recibido el pago. Reporta los que estén vencidos.`,
    { label: 'reps-pendientes', phase: 'Detección', schema: alertasSchema() }
  ),
])

const [alertas69b, alertasRetenciones, alertasEfectivo, alertasMultimoneda, alertasReps] = alertas

// ============================================================
// FASE 4: Cálculo del pago provisional
// ============================================================
phase('Cálculo')

const pagoProvisional = await agent(
  `Usando el skill freelance-tax-mx (o iva-retenciones-mx para PM), calcula el pago provisional del mes ${ejercicio}-${mes} para régimen ${regimen}.

  Inputs:
  - Ingresos cobrados: $${cfdisEmitidos.total_cobrado || 0} (CFDIs emitidos cobrados)
  - Gastos deducibles: $${cruceGastos?.deducibles_total || 0} (solo CFDIs recibidos pagados)
  - Retenciones acreditables: ${JSON.stringify(alertasRetenciones).slice(0, 300)}
  - Pagos provisionales previos del ejercicio: requiere lookup
  - Régimen: ${regimen}

  Devuelve desglose:
  { isr_calculado, iva_trasladado, iva_acreditable, iva_a_pagar, retenciones_aplicadas, total_a_pagar, fecha_limite, advertencias }

  ⚠ Marca vigencia_validada=false si las tarifas usadas no han sido confirmadas por contador.`,
  { label: 'pago-provisional', phase: 'Cálculo', schema: pagoProvisionalSchema() }
)

// ============================================================
// FASE 5: Validación cruzada (solo si monto > $50k)
// ============================================================
phase('Validación')

let validacionCruzada = null
if (pagoProvisional.total_a_pagar > 50000) {
  validacionCruzada = await agent(
    `Recalcula el pago provisional con método alternativo (proporcional al ejercicio acumulado). Si difiere >5% del cálculo principal ($${pagoProvisional.total_a_pagar}), reporta discrepancia.`,
    { label: 'validacion-cruzada', phase: 'Validación', schema: validacionSchema() }
  )
}

// ============================================================
// FASE 6: Output — reporte + alertas + recordatorio
// ============================================================
phase('Output')

const ruta = `fiscal/${ejercicio}-${String(mes).padStart(2, '0')}`

await agent(
  `Genera el reporte ejecutivo en \`${ruta}-pago-provisional.md\` con:
   - Resumen ejecutivo (total a pagar, fecha límite)
   - Desglose por concepto
   - Lista de alertas críticas
   - Recomendaciones de acción
   - Footer con marca de vigencia y disclaimer "consulta a tu contador"`,
  { label: 'reporte-md', phase: 'Output' }
)

await agent(
  `Genera \`${ruta}-alertas.md\` con SOLO las acciones inmediatas que requieren atención humana hoy (resolver buzón, refacturar 69-B, emitir REPs pendientes).`,
  { label: 'alertas-md', phase: 'Output' }
)

await agent(
  `Programa un recordatorio WhatsApp via mp_meta_whatsapp para el día 17 del mes ${ejercicio}-${mes}, contenido: "Último día para presentar declaración mensual ${regimen}. Total: $${pagoProvisional.total_a_pagar}. Línea de captura: <pendiente generación humana>".`,
  { label: 'recordatorio-wa', phase: 'Output' }
)

return {
  status: 'completado',
  ejercicio,
  mes,
  rfc,
  regimen,
  pago_provisional: pagoProvisional,
  alertas: {
    en_69b: alertas69b,
    retenciones_no_acreditadas: alertasRetenciones,
    depositos_efectivo: alertasEfectivo,
    multimoneda_tc_anomalo: alertasMultimoneda,
    reps_pendientes: alertasReps,
    buzon: buzon,
  },
  validacion_cruzada: validacionCruzada,
  reportes: {
    completo: `${ruta}-pago-provisional.md`,
    alertas: `${ruta}-alertas.md`,
  },
  vigencia_validada: pagoProvisional.vigencia_validada === true,
}

// ============================================================
// Schemas (helpers locales)
// ============================================================
function cfdiBatchSchema() {
  return {
    type: 'object',
    properties: {
      total: { type: 'number' },
      total_cobrado: { type: 'number' },
      solicitud_id: { type: 'string' },
      pending: { type: 'boolean' },
      cfdis: { type: 'array', items: { type: 'object' } },
    },
  }
}

function buzonSchema() {
  return {
    type: 'object',
    properties: {
      notificaciones: { type: 'array', items: { type: 'object' } },
      no_leidas: { type: 'number' },
      proximas_a_vencer: { type: 'array' },
    },
  }
}

function tcSerieSchema() {
  return {
    type: 'object',
    properties: {
      moneda_origen: { type: 'string' },
      moneda_destino: { type: 'string' },
      serie: { type: 'array', items: { type: 'object' } },
    },
  }
}

function umaInpcSchema() {
  return {
    type: 'object',
    properties: {
      uma_diario: { type: 'number' },
      uma_mensual: { type: 'number' },
      uma_anual: { type: 'number' },
      inpc_mes: { type: 'number' },
    },
  }
}

function balanzaSchema() {
  return {
    type: 'object',
    properties: {
      cuentas: { type: 'array', items: { type: 'object' } },
    },
  }
}

function cruceSchema() {
  return {
    type: 'object',
    properties: {
      matches: { type: 'array' },
      depositos_sin_cfdi: { type: 'array' },
      cfdis_sin_cobro: { type: 'array' },
      cargos_sin_cfdi: { type: 'array' },
      cfdis_sin_pago: { type: 'array' },
      deducibles_total: { type: 'number' },
    },
  }
}

function alertasSchema() {
  return {
    type: 'object',
    properties: {
      cantidad: { type: 'number' },
      monto_total: { type: 'number' },
      detalle: { type: 'array' },
      severidad: { enum: ['critica', 'alta', 'media', 'baja'] },
    },
  }
}

function pagoProvisionalSchema() {
  return {
    type: 'object',
    required: ['isr_calculado', 'total_a_pagar', 'fecha_limite'],
    properties: {
      isr_calculado: { type: 'number' },
      iva_trasladado: { type: 'number' },
      iva_acreditable: { type: 'number' },
      iva_a_pagar: { type: 'number' },
      retenciones_aplicadas: { type: 'number' },
      total_a_pagar: { type: 'number' },
      fecha_limite: { type: 'string' },
      tasa_aplicada: { type: 'string' },
      vigencia_validada: { type: 'boolean' },
      advertencias: { type: 'array', items: { type: 'string' } },
    },
  }
}

function validacionSchema() {
  return {
    type: 'object',
    properties: {
      metodo_alternativo: { type: 'number' },
      diferencia_pct: { type: 'number' },
      coincide: { type: 'boolean' },
      nota: { type: 'string' },
    },
  }
}
