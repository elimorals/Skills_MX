// Workflow ejecutable: cobranza-renta-mensual
//
// Cobranza recurrente de rentas para inmobiliario residencial/comercial.
// Incluye recordatorios escalados WhatsApp, generación CFDI tipo I, conciliación
// banco, y detección de inquilinos en mora con disparador de recuperación.
//
// Invocar con: Workflow({scriptPath: "inmobiliaria-mx/workflows/cobranza-renta-mensual.workflow.js", args: {...}})
//
// Inputs en `args`:
//   {
//     arrendador_rfc: string,        // RFC del propietario (PF o PM)
//     ejercicio: number,              // año
//     mes: number,                    // 1-12
//     contratos?: object[],           // [{contrato_id, inquilino_nombre, tel, monto_mxn, dia_pago, propiedad}]
//     dia_recordatorio_1?: number,    // default 3 (3 días antes vencimiento)
//     dia_recordatorio_2?: number,    // default 0 (día de vencimiento)
//     dia_recordatorio_3?: number,    // default 3 (3 días después - moratoria)
//   }

export const meta = {
  name: 'cobranza-renta-mensual',
  description: 'Cobranza recurrente de rentas: recordatorios escalados WhatsApp + emisión CFDI tipo I + conciliación banco + detección morosos.',
  whenToUse: 'Cron mensual día 1 o manual cuando comienza el mes',
  phases: [
    { title: 'Setup', detail: 'cargar contratos vigentes + TC + UMA' },
    { title: 'Recordatorios', detail: 'pipeline: pre-vencimiento → vencimiento → post-vencimiento' },
    { title: 'Conciliación', detail: 'parallel: bancos + emisión CFDI por cada pago detectado' },
    { title: 'Morosidad', detail: 'identificar inquilinos sin pago > 5 días, generar recuperación' },
    { title: 'Output', detail: 'reporte mensual + dashboard cartera + alertas' },
  ],
}

const {
  arrendador_rfc,
  ejercicio,
  mes,
  contratos = [],
  dia_recordatorio_1 = 3,
  dia_recordatorio_2 = 0,
  dia_recordatorio_3 = 3,
} = args || {}

if (!arrendador_rfc || !ejercicio || !mes) {
  throw new Error('args requeridos: { arrendador_rfc, ejercicio, mes, [contratos] }')
}

log(`Cobranza renta — ${arrendador_rfc.slice(0, 4)}*** — ${ejercicio}-${String(mes).padStart(2, '0')}`)

// ============================================================
// FASE 1: Setup — cargar contexto
// ============================================================
phase('Setup')

const setup = await parallel([
  () => agent(
    contratos.length > 0
      ? `Recibido lista explícita de ${contratos.length} contratos. Devolver tal cual con validación: ${JSON.stringify(contratos).slice(0, 2000)}`
      : `Cargar contratos de arrendamiento vigentes del RFC ${arrendador_rfc} de la base local (inmobiliaria-mx/contratos.json o equivalente). Filtrar solo vigentes al ${ejercicio}-${mes}.`,
    { label: 'contratos', phase: 'Setup', schema: contratosSchema() }
  ),
  () => agent(
    `Obtén TC DOF y UMA vigente para ${ejercicio} via mp_banxico (necesario si hay rentas indexadas a UMA).`,
    { label: 'tc-uma', phase: 'Setup', schema: tcUmaSchema() }
  ),
])

const [ctx, tcUma] = setup
const contratosVigentes = ctx.contratos || []

log(`Contratos a procesar: ${contratosVigentes.length}`)

// ============================================================
// FASE 2: Recordatorios (pipeline por contrato)
// ============================================================
phase('Recordatorios')

const recordatorios = await pipeline(
  contratosVigentes,
  (contrato) => agent(
    `Para contrato ${contrato.contrato_id} del inquilino ${contrato.inquilino_nombre} (tel hash: ${contrato.tel?.slice(-4) || 'sin'}):
     - Fecha vencimiento: ${ejercicio}-${mes}-${String(contrato.dia_pago).padStart(2, '0')}
     - Monto: $${contrato.monto_mxn}
     - Propiedad: ${contrato.propiedad}

     Programa 3 recordatorios WhatsApp via mp_meta_whatsapp usando templates aprobadas:
     1. ${dia_recordatorio_1} días antes: template "recordatorio_renta_pre"
     2. Día de vencimiento: template "recordatorio_renta_dia"
     3. ${dia_recordatorio_3} días después si no se pagó: template "recordatorio_renta_mora"

     Devuelve mensajes programados con IDs.`,
    { label: `recordatorio-${contrato.contrato_id}`, phase: 'Recordatorios', schema: recordatorioSchema() }
  ),
)

// ============================================================
// FASE 3: Conciliación banco + emisión CFDI por pago detectado
// ============================================================
phase('Conciliación')

const conciliacion = await agent(
  `Consulta movimientos bancarios del arrendador ${arrendador_rfc} en mp_bancos_mx para ${ejercicio}-${mes}.
   Cruza cada depósito con un contrato:
   - Match por monto exacto + referencia (típicamente contrato_id en concepto)
   - Match aproximado por monto + nombre inquilino en concepto
   - Sin match → reportar para investigación manual

   Devuelve: { pagos_identificados: [{contrato_id, monto_mxn, fecha, banco, referencia}], pagos_sin_identificar: [...], contratos_no_pagados: [...] }
   Contratos: ${JSON.stringify(contratosVigentes.map(c => ({id: c.contrato_id, monto: c.monto_mxn, nombre: c.inquilino_nombre}))).slice(0, 3000)}`,
  { label: 'conciliacion-bancos', phase: 'Conciliación', schema: conciliacionSchema() }
)

const cfdisEmitidos = await parallel(
  (conciliacion.pagos_identificados || []).map((pago) => () => agent(
    `Emite CFDI tipo I (Ingreso) en mp_facturama_extendido para el pago detectado:
     - Receptor: ${pago.inquilino_rfc || 'XAXX010101000 (público en general)'}
     - Monto: $${pago.monto_mxn}
     - Uso CFDI: G03 (Gastos en general) o D10 si renta habitación casa-habitación
     - Forma pago: 03 (transferencia)
     - Método pago: PUE
     - Concepto: "Arrendamiento ${ejercicio}-${mes} contrato ${pago.contrato_id}"
     Devuelve UUID + XML link.`,
    { label: `cfdi-${pago.contrato_id}`, phase: 'Conciliación', schema: cfdiSchema() }
  ))
)

// ============================================================
// FASE 4: Detección de morosidad
// ============================================================
phase('Morosidad')

const morosos = await agent(
  `Identifica inquilinos morosos: contratos vigentes en ${ejercicio}-${mes} sin pago detectado tras día ${dia_recordatorio_3} de venc.

   Contratos no pagados: ${JSON.stringify(conciliacion.contratos_no_pagados || []).slice(0, 2000)}

   Para cada moroso calcula:
   - Días en mora
   - Recargo aplicable (típicamente 10% mensual proporcional o lo que diga el contrato)
   - Si > 30 días: marcar para gestión legal
   - Si > 90 días: recomendar inicio de juicio de desocupación

   Genera lista priorizada con acción recomendada por inquilino.`,
  { label: 'morosos', phase: 'Morosidad', schema: morososSchema() }
)

// ============================================================
// FASE 5: Output
// ============================================================
phase('Output')

const ruta = `inmobiliaria/${arrendador_rfc.slice(0, 4)}/${ejercicio}-${String(mes).padStart(2, '0')}`

await parallel([
  () => agent(
    `Genera \`${ruta}-cobranza.md\` con resumen ejecutivo:
     - Total contratos: ${contratosVigentes.length}
     - Pagos identificados: ${conciliacion.pagos_identificados?.length || 0} ($${conciliacion.monto_total_cobrado_mxn || 0})
     - Pagos sin identificar: ${conciliacion.pagos_sin_identificar?.length || 0}
     - Morosos: ${morosos.morosos?.length || 0}
     - CFDIs emitidos: ${cfdisEmitidos.filter(Boolean).length}
     - Eficiencia cobranza: %`,
    { label: 'reporte', phase: 'Output' }
  ),
  () => agent(
    `Genera \`${ruta}-cartera.csv\` con columnas: contrato_id, inquilino, propiedad, monto_mxn, status (pagado/moroso/pendiente), dias_mora, recargo_mxn, accion_recomendada.`,
    { label: 'cartera-csv', phase: 'Output' }
  ),
  () => agent(
    `Si hay morosos > 30 días, envía alerta resumen al arrendador ${arrendador_rfc}: "Reporte ${ejercicio}-${mes}: N morosos > 30 días requieren gestión legal. Ver ${ruta}-cobranza.md".`,
    { label: 'alerta-arrendador', phase: 'Output' }
  ),
])

return {
  status: 'completado',
  arrendador_rfc: arrendador_rfc.slice(0, 4) + '***',
  ejercicio,
  mes,
  contratos_procesados: contratosVigentes.length,
  pagos_identificados: conciliacion.pagos_identificados?.length || 0,
  cfdis_emitidos: cfdisEmitidos.filter(Boolean).length,
  morosos: morosos.morosos?.length || 0,
  eficiencia_cobranza_pct: contratosVigentes.length > 0
    ? Math.round(((conciliacion.pagos_identificados?.length || 0) / contratosVigentes.length) * 100)
    : 0,
}

// ============================================================
// Schemas
// ============================================================
function contratosSchema() {
  return {
    type: 'object',
    properties: {
      contratos: { type: 'array', items: { type: 'object' } },
      total_count: { type: 'number' },
    },
  }
}

function tcUmaSchema() {
  return {
    type: 'object',
    properties: {
      tc_usd_mxn: { type: 'number' },
      uma_diario: { type: 'number' },
      inpc_ejercicio: { type: 'number' },
    },
  }
}

function recordatorioSchema() {
  return {
    type: 'object',
    properties: {
      contrato_id: { type: 'string' },
      mensajes_programados: { type: 'array' },
    },
  }
}

function conciliacionSchema() {
  return {
    type: 'object',
    properties: {
      pagos_identificados: { type: 'array' },
      pagos_sin_identificar: { type: 'array' },
      contratos_no_pagados: { type: 'array' },
      monto_total_cobrado_mxn: { type: 'number' },
    },
  }
}

function cfdiSchema() {
  return {
    type: 'object',
    properties: {
      uuid: { type: 'string' },
      xml_url: { type: 'string' },
      contrato_id: { type: 'string' },
    },
  }
}

function morososSchema() {
  return {
    type: 'object',
    properties: {
      morosos: { type: 'array' },
      total_monto_mora_mxn: { type: 'number' },
      contratos_para_gestion_legal: { type: 'array' },
    },
  }
}
