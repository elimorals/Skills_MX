// Workflow ejecutable: cfdi-emision-completa
//
// Flujo end-to-end de emisión de CFDI: validar RFC receptor → calcular impuestos/retenciones →
// pre-validar payload → timbrar via Facturama → enviar XML+PDF al cliente.
//
// Invocar con: Workflow({scriptPath: "core-mexico/workflows/cfdi-emision-completa.workflow.js", args: {...}})
//
// args: { emisor_rfc, receptor_rfc, conceptos:[], uso_cfdi, metodo_pago, forma_pago, moneda, total_esperado,
//         enviar_por_wa?: boolean, telefono_wa?: string }

export const meta = {
  name: 'cfdi-emision-completa',
  description: 'Emisión CFDI 4.0 end-to-end: validación RFC + 69-B + cálculo impuestos + pre-validación payload + timbrado Facturama + envío al cliente WA/email.',
  whenToUse: '/core:emitir-y-notificar o trigger por venta confirmada / cobro recibido',
  phases: [
    { title: 'Validación RFC', detail: 'estructura + padrón SAT + 69-B EFOS' },
    { title: 'Construcción', detail: 'conceptos + impuestos + retenciones según régimen' },
    { title: 'Pre-validación', detail: 'reglas críticas locales antes de llamar PAC' },
    { title: 'Timbrado', detail: 'Facturama PAC autorizado' },
    { title: 'Distribución', detail: 'envío al cliente vía WhatsApp/email + bitácora' },
  ],
}

const {
  emisor_rfc,
  receptor_rfc,
  conceptos,
  uso_cfdi = 'G03',
  metodo_pago = 'PUE',
  forma_pago = '03',
  moneda = 'MXN',
  total_esperado,
  enviar_por_wa = false,
  telefono_wa,
} = args || {}

if (!emisor_rfc || !receptor_rfc || !conceptos?.length) {
  throw new Error('args requeridos: { emisor_rfc, receptor_rfc, conceptos: [...] }')
}

log(`CFDI ${emisor_rfc} → ${receptor_rfc} | ${conceptos.length} concepto(s) | ${moneda}`)

// ============================================================
// FASE 1: Validación RFC receptor (paralelo: padrón + 69-B + estructura)
// ============================================================
phase('Validación RFC')

const rfcChecks = await parallel([
  () => agent(
    `Valida estructura del RFC ${receptor_rfc} con skill rfc-validacion. Devuelve { valido: bool, tipo: "PF"|"PM", advertencias: [] }`,
    { label: 'rfc-estructura', phase: 'Validación RFC', schema: rfcEstructuraSchema() }
  ),
  () => agent(
    `Consulta el RFC ${receptor_rfc} en padrón SAT vía mp_sat_portal.consultar_padron. Devuelve { en_padron: bool, razon_social: string, regimen_fiscal: string }`,
    { label: 'rfc-padron', phase: 'Validación RFC', schema: rfcPadronSchema() }
  ),
  () => agent(
    `Verifica si RFC ${receptor_rfc} está en lista 69-B EFOS (presunción) o definitivos vía mp_sat_portal.consultar_69b_efos. Devuelve { en_69b: bool, estado: "presunto"|"definitivo"|"desvirtuado"|null }`,
    { label: 'rfc-69b', phase: 'Validación RFC', schema: rfc69bSchema() }
  ),
])

const [estructura, padron, lista69b] = rfcChecks

if (!estructura.valido) {
  return { status: 'abortado', razon: 'RFC inválido estructura', detalle: estructura.advertencias }
}
if (!padron.en_padron) {
  return { status: 'abortado', razon: 'RFC no encontrado en padrón SAT', detalle: padron }
}
if (lista69b.en_69b && lista69b.estado === 'definitivo') {
  return { status: 'abortado', razon: 'RFC en 69-B definitivo: CFDIs NO deducibles para receptor', detalle: lista69b }
}

const advertencias = []
if (lista69b.en_69b && lista69b.estado === 'presunto') {
  advertencias.push(`⚠ Receptor en 69-B PRESUNTO — alerta al usuario antes de proceder.`)
}

// ============================================================
// FASE 2: Construcción del payload + cálculo impuestos
// ============================================================
phase('Construcción')

const payload = await agent(
  `Construye payload CFDI 4.0 usando skill cfdi-emision con:
   - Emisor: ${emisor_rfc} (régimen consultado del padrón)
   - Receptor: ${receptor_rfc} (régimen: ${padron.regimen_fiscal})
   - Conceptos: ${JSON.stringify(conceptos)}
   - UsoCFDI: ${uso_cfdi}
   - MetodoPago: ${metodo_pago}
   - FormaPago: ${forma_pago}
   - Moneda: ${moneda}

   Si moneda != MXN: invocar mp_banxico.get_tc_dof para fecha de hoy y poblar TipoCambio.

   Calcula impuestos con skill iva-retenciones-mx:
   - IVA trasladado 16% por concepto (o 0% / 8% según ObjetoImp del concepto)
   - Retenciones aplicables según escenario (PF→PM honorarios profesionales: 10% ISR + 10.67% IVA; RESICO: 1.25% ISR)

   Devuelve payload JSON completo listo para Facturama + desglose de cálculos.`,
  { label: 'construir-payload', phase: 'Construcción', schema: payloadCfdiSchema() }
)

// ============================================================
// FASE 3: Pre-validación local (antes de llamar PAC)
// ============================================================
phase('Pre-validación')

const validacion = await agent(
  `Ejecuta validación local del payload con mp_facturama_extendido.validar_payload_local. Reglas:
   1. RFC emisor/receptor cumplen regex
   2. CP receptor 5 dígitos válidos
   3. Régimen fiscal emisor+receptor consistentes con UsoCFDI
   4. Método+Forma de pago consistencia (PUE↔específico, PPD↔99)
   5. Total = subtotal + IVA - retenciones (delta < 0.01)
   6. Fecha dentro de ±72h
   7. ObjetoImp por concepto presente
   8. Exportacion presente
   9. Si total_esperado=${total_esperado}: verificar coincidencia con total calculado

   Devuelve { ok: bool, errores: [], advertencias: [] }. Si !ok → abortar (no llamar Facturama).`,
  { label: 'pre-validacion', phase: 'Pre-validación', schema: validacionSchema() }
)

if (!validacion.ok) {
  return { status: 'abortado_pre_validacion', errores: validacion.errores, payload_revisado: payload }
}

// ============================================================
// FASE 4: Timbrado vía Facturama
// ============================================================
phase('Timbrado')

const timbrado = await agent(
  `Timbra el CFDI vía mp_facturama_extendido.timbrar_cfdi con el payload validado. Devuelve { uuid, xml_b64, pdf_b64, sello_sat, fecha_timbrado }.
   Si Facturama responde error → registrar en bitácora y abortar con detalle.`,
  { label: 'timbrar', phase: 'Timbrado', schema: timbradoSchema() }
)

if (!timbrado.uuid) {
  return { status: 'fallo_timbrado', razon: 'PAC rechazó payload', detalle: timbrado }
}

log(`✅ CFDI timbrado: UUID ${timbrado.uuid}`)

// ============================================================
// FASE 5: Distribución (WhatsApp/email + persistencia + bitácora)
// ============================================================
phase('Distribución')

const tasks = [
  () => agent(
    `Persiste el CFDI en cfdi/${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, '0')}/${timbrado.uuid}.json con XML+PDF anexos.`,
    { label: 'persistir-cfdi', phase: 'Distribución' }
  ),
  () => agent(
    `Registra el timbrado en bitácora con timestamp + UUID + RFC receptor hasheado + monto total.`,
    { label: 'bitacora-timbrado', phase: 'Distribución' }
  ),
]

if (enviar_por_wa && telefono_wa) {
  tasks.push(
    () => agent(
      `Envía CFDI al cliente vía WhatsApp usando skill whatsapp-business-mx + template "utility_cfdi_emitido". Adjunta PDF al teléfono ${telefono_wa}. Devuelve { enviado: bool, message_id }.`,
      { label: 'enviar-wa', phase: 'Distribución' }
    )
  )
}

await parallel(tasks)

return {
  status: 'completado',
  uuid: timbrado.uuid,
  emisor: emisor_rfc,
  receptor: receptor_rfc,
  total: payload.total,
  moneda,
  fecha_timbrado: timbrado.fecha_timbrado,
  advertencias,
  archivos: {
    xml: `cfdi/.../${timbrado.uuid}.xml`,
    pdf: `cfdi/.../${timbrado.uuid}.pdf`,
  },
}

// Schemas
function rfcEstructuraSchema() {
  return { type: 'object', properties: { valido: { type: 'boolean' }, tipo: { enum: ['PF', 'PM'] }, advertencias: { type: 'array' } } }
}
function rfcPadronSchema() {
  return { type: 'object', properties: { en_padron: { type: 'boolean' }, razon_social: { type: 'string' }, regimen_fiscal: { type: 'string' } } }
}
function rfc69bSchema() {
  return { type: 'object', properties: { en_69b: { type: 'boolean' }, estado: { enum: ['presunto', 'definitivo', 'desvirtuado', null] } } }
}
function payloadCfdiSchema() {
  return {
    type: 'object',
    required: ['conceptos', 'total'],
    properties: { conceptos: { type: 'array' }, total: { type: 'number' }, impuestos: { type: 'object' } },
  }
}
function validacionSchema() {
  return { type: 'object', required: ['ok'], properties: { ok: { type: 'boolean' }, errores: { type: 'array' }, advertencias: { type: 'array' } } }
}
function timbradoSchema() {
  return { type: 'object', properties: { uuid: { type: 'string' }, xml_b64: { type: 'string' }, pdf_b64: { type: 'string' }, sello_sat: { type: 'string' }, fecha_timbrado: { type: 'string' } } }
}
