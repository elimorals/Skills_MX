// Workflow ejecutable: donativo-anual
//
// Cierre anual para donatarias autorizadas SAT: consolida donativos recibidos,
// emite CFDI tipo D (Donativos) pendientes, valida que donantes deduzcan
// correctamente, prepara informe de transparencia obligatorio.
//
// Invocar con: Workflow({scriptPath: "donatarias-ongs-mx/workflows/donativo-anual.workflow.js", args: {...}})
//
// Inputs en `args`:
//   {
//     donataria_rfc: string,
//     ejercicio: number,
//     incluir_no_recibos?: boolean,  // donativos sin CFDI pendientes
//   }

export const meta = {
  name: 'donativo-anual',
  description: 'Cierre anual donatarias autorizadas SAT: consolida donativos, emite CFDIs pendientes, valida deducibilidad, prepara informe transparencia.',
  whenToUse: 'Enero-marzo del año siguiente al ejercicio fiscal',
  phases: [
    { title: 'Recopilación', detail: 'parallel: depósitos del año + CFDIs D emitidos + padrón donantes' },
    { title: 'Conciliación', detail: 'cruzar donativos recibidos vs CFDIs emitidos' },
    { title: 'Emisión', detail: 'pipeline: emitir CFDIs faltantes con datos completos del donante' },
    { title: 'Transparencia', detail: 'informe anual SAT + cumplimiento Art. 82 LISR' },
    { title: 'Output', detail: 'reporte ejecutivo + informe SAT + cartas agradecimiento' },
  ],
}

const {
  donataria_rfc,
  ejercicio,
  incluir_no_recibos = true,
} = args || {}

if (!donataria_rfc || !ejercicio) {
  throw new Error('args requeridos: { donataria_rfc, ejercicio }')
}

log(`Donativo anual — donataria ${donataria_rfc.slice(0, 4)}*** — ejercicio ${ejercicio}`)

// ============================================================
// FASE 1: Recopilación
// ============================================================
phase('Recopilación')

const recopilacion = await parallel([
  () => agent(
    `Obtén movimientos bancarios entrantes (depósitos) del RFC ${donataria_rfc} para ejercicio ${ejercicio} via mp_bancos_mx.
     Filtra solo movimientos de tipo "abono" o "depósito". Excluye traspasos internos entre cuentas propias.
     Devuelve: [{fecha, monto_mxn, banco, concepto, contraparte_inferida}].`,
    { label: 'depositos-anuales', phase: 'Recopilación', schema: depositosSchema() }
  ),
  () => agent(
    `Descarga CFDIs emitidos tipo D (Donativos) del RFC ${donataria_rfc} para ejercicio ${ejercicio} usando mp_sat_portal.descargar_cfdi_masivo con tipo="emitidos" + filtro tipo_comprobante="D".
     Devuelve: [{uuid, receptor_rfc, fecha, monto_mxn, deducible}].`,
    { label: 'cfdis-d-emitidos', phase: 'Recopilación', schema: cfdisSchema() }
  ),
  () => agent(
    `Consulta padrón de donantes recurrentes registrados localmente (donatarias-ongs-mx/padron-donantes.json).
     Para donatarias nuevas o sin padrón, devolver lista vacía.`,
    { label: 'padron', phase: 'Recopilación', schema: padronSchema() }
  ),
  () => agent(
    `Valida vigencia de la autorización SAT como donataria autorizada (Art. 82 LISR).
     Consulta el padrón oficial vía mp_sat_portal. Si NO está vigente, esta donataria PERDIÓ deducibilidad — alerta crítica.`,
    { label: 'autorizacion-sat', phase: 'Recopilación', schema: autorizacionSchema() }
  ),
])

const [depositos, cfdisD, padron, autorizacion] = recopilacion

if (autorizacion && !autorizacion.vigente) {
  log('⚠ CRÍTICO: Donataria sin autorización vigente para el ejercicio — TODOS los CFDIs son inválidos')
  return {
    status: 'autorizacion_no_vigente',
    advertencia: 'Donataria NO vigente como donataria autorizada SAT. No procesar cierre anual hasta regularizar.',
    autorizacion,
  }
}

log(`Depósitos: ${depositos?.total_count || 0} — CFDIs D: ${cfdisD?.total_count || 0}`)

// ============================================================
// FASE 2: Conciliación depósitos vs CFDIs D
// ============================================================
phase('Conciliación')

const conciliacion = await agent(
  `Cruza depósitos del ejercicio ${ejercicio} contra CFDIs D emitidos.
   Algoritmo:
   - Match exacto: monto idéntico + fecha ±3 días + (concepto banco contiene nombre/RFC del receptor del CFDI)
   - Match aproximado: monto idéntico + fecha en mismo mes
   - Sin match con CFDI: donativo sin recibo deducible emitido (potencial pendiente)

   Devuelve:
   {
     pareados: [{deposito_id, cfdi_uuid, monto_mxn}],
     depositos_sin_cfdi: [...],  // donativos recibidos sin recibo
     cfdis_sin_deposito: [...],  // recibos emitidos sin depósito (raro, investigar)
     total_donativos_pareados_mxn,
   }
   Depósitos: ${JSON.stringify((depositos?.depositos || []).slice(0, 50))}
   CFDIs: ${JSON.stringify((cfdisD?.cfdis || []).slice(0, 50))}`,
  { label: 'conciliar', phase: 'Conciliación', schema: conciliacionDonativoSchema() }
)

// ============================================================
// FASE 3: Emisión de CFDIs faltantes (si activado)
// ============================================================
phase('Emisión')

let cfdisEmitidosNuevos = []
if (incluir_no_recibos && conciliacion.depositos_sin_cfdi?.length > 0) {
  cfdisEmitidosNuevos = await pipeline(
    conciliacion.depositos_sin_cfdi,
    (deposito) => agent(
      `Para el depósito ${deposito.id} ($${deposito.monto_mxn} del ${deposito.fecha} banco ${deposito.banco}):
       1. Intenta identificar al donante desde el padrón o desde el concepto bancario
       2. Si se identifica, valida que tenga RFC válido (mp_curp_renapo o mp_sat_portal)
       3. Si todo OK, emite CFDI tipo D en mp_facturama_extendido:
          - Receptor: RFC identificado o XAXX010101000 si público en general
          - UsoCFDI: D04 (donativos)
          - Concepto: "Donativo a donataria autorizada ${donataria_rfc} — ejercicio ${ejercicio}"
          - TipoComprobante: D
       4. Si NO se puede identificar, deja pendiente para contacto manual
       Padrón ref: ${JSON.stringify(padron?.donantes_recurrentes || []).slice(0, 1000)}`,
      { label: `cfdi-d-${deposito.id}`, phase: 'Emisión', schema: cfdiEmisionSchema() }
    )
  )
}

// ============================================================
// FASE 4: Cumplimiento Art. 82 LISR + transparencia
// ============================================================
phase('Transparencia')

const transparencia = await agent(
  `Genera el informe anual de transparencia obligatorio para donatarias (Art. 82 LISR + RMF 3.10.10):
   - Total donativos recibidos en ejercicio ${ejercicio}: $${conciliacion.total_donativos_pareados_mxn || 0}
   - Donativos con recibo deducible emitido
   - Estructura de uso de fondos (estimación si no se proveen datos)
   - Listado donantes con > 5% del total (regla CARF + RMF)
   - Patrimonio al cierre + variación vs ejercicio anterior
   - Compromiso de no distribución de remanentes

   Genera markdown listo para subir a portal SAT (transparencia.donatariasautorizadas.sat.gob.mx).`,
  { label: 'transparencia-art82', phase: 'Transparencia', schema: transparenciaSchema() }
)

// ============================================================
// FASE 5: Output
// ============================================================
phase('Output')

const ruta = `donatarias/${donataria_rfc.slice(0, 4)}/${ejercicio}`

await parallel([
  () => agent(
    `Genera reporte ejecutivo \`${ruta}-cierre-anual.md\` con:
     - Resumen donativos
     - CFDIs D emitidos durante el año
     - CFDIs D emitidos ahora (cierre): ${cfdisEmitidosNuevos.filter(Boolean).length}
     - Compliance Art. 82
     - Próximos pasos`,
    { label: 'reporte', phase: 'Output' }
  ),
  () => agent(
    `Genera \`${ruta}-informe-sat-transparencia.md\` con el informe oficial listo para portal SAT. Datos: ${JSON.stringify(transparencia).slice(0, 2000)}`,
    { label: 'informe-sat', phase: 'Output' }
  ),
  () => agent(
    `Genera cartas de agradecimiento personalizadas para donantes con > $10,000 anuales: \`${ruta}-cartas/\`.
     Una carta por donante con monto consolidado del año, lista de UUIDs y mensaje agradecimiento.`,
    { label: 'cartas', phase: 'Output' }
  ),
])

return {
  status: 'completado',
  donataria_rfc: donataria_rfc.slice(0, 4) + '***',
  ejercicio,
  total_donativos_mxn: conciliacion.total_donativos_pareados_mxn || 0,
  cfdis_d_emitidos_durante_anio: cfdisD?.total_count || 0,
  cfdis_d_emitidos_ahora: cfdisEmitidosNuevos.filter(Boolean).length,
  pendientes_contacto_manual: conciliacion.depositos_sin_cfdi?.length - cfdisEmitidosNuevos.filter(Boolean).length,
  artefactos: {
    reporte: `${ruta}-cierre-anual.md`,
    informe_sat: `${ruta}-informe-sat-transparencia.md`,
  },
}

// ============================================================
// Schemas
// ============================================================
function depositosSchema() {
  return {
    type: 'object',
    properties: {
      total_count: { type: 'number' },
      total_mxn: { type: 'number' },
      depositos: { type: 'array' },
    },
  }
}

function cfdisSchema() {
  return {
    type: 'object',
    properties: {
      total_count: { type: 'number' },
      total_mxn: { type: 'number' },
      cfdis: { type: 'array' },
    },
  }
}

function padronSchema() {
  return {
    type: 'object',
    properties: {
      donantes_recurrentes: { type: 'array' },
      total_count: { type: 'number' },
    },
  }
}

function autorizacionSchema() {
  return {
    type: 'object',
    properties: {
      vigente: { type: 'boolean' },
      fecha_autorizacion: { type: 'string' },
      anio_vigencia: { type: 'number' },
      observaciones: { type: 'array' },
    },
  }
}

function conciliacionDonativoSchema() {
  return {
    type: 'object',
    properties: {
      pareados: { type: 'array' },
      depositos_sin_cfdi: { type: 'array' },
      cfdis_sin_deposito: { type: 'array' },
      total_donativos_pareados_mxn: { type: 'number' },
    },
  }
}

function cfdiEmisionSchema() {
  return {
    type: 'object',
    properties: {
      uuid: { type: 'string' },
      receptor_rfc: { type: 'string' },
      monto_mxn: { type: 'number' },
      status: { enum: ['emitido', 'pendiente_contacto_manual'] },
    },
  }
}

function transparenciaSchema() {
  return {
    type: 'object',
    properties: {
      cumple_art_82: { type: 'boolean' },
      donantes_mayores: { type: 'array' },
      estructura_gastos: { type: 'object' },
      observaciones_sat: { type: 'array' },
    },
  }
}
