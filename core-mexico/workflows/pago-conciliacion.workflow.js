// Workflow ejecutable: pago-conciliacion
//
// Disparado por webhook de pasarela (MP/Conekta) o SPEI recibido. Concilia el pago con CFDI emitido,
// emite REP (CFDI tipo P) si era PPD, notifica al cliente.
//
// args: { pago_id, fuente: "mercadopago"|"conekta"|"spei"|"stripe", monto, fecha, external_reference }

export const meta = {
  name: 'pago-conciliacion',
  description: 'Pago entrante → match con CFDI → REP si PPD → notificar cliente. Disparado por webhook pasarela o SPEI manual.',
  whenToUse: 'Webhook handler post-pago confirmado o /core:conciliar-pago manual.',
  phases: [
    { title: 'Match', detail: 'parear pago con CFDI emitido por external_reference o monto+fecha' },
    { title: 'CFDI tipo P', detail: 'emitir REP si era PPD' },
    { title: 'Notificación', detail: 'WA al cliente confirmando recepción + REP' },
    { title: 'Bitácora', detail: 'actualizar status del CFDI a cobrado' },
  ],
}

const { pago_id, fuente, monto, fecha, external_reference } = args || {}
if (!pago_id || !fuente || !monto) {
  throw new Error('args requeridos: { pago_id, fuente, monto, fecha?, external_reference? }')
}

log(`Conciliando pago ${fuente}:${pago_id} | $${monto}`)

// ============================================================
// FASE 1: Match con CFDI emitido
// ============================================================
phase('Match')

const match = await agent(
  `Busca CFDI emitido que corresponda al pago:
   - Si external_reference="${external_reference}" coincide con un UUID o folio interno: match exacto
   - Si no, busca por (monto=${monto}, fecha entre ${fecha} y ${fecha} - 5 días) entre CFDIs status="pendiente_cobro"
   - Si encuentras 1 candidato único: devuelve { match: "exacto", uuid, metodo_pago_cfdi: "PUE"|"PPD" }
   - Si encuentras varios: devuelve { match: "ambiguo", candidatos: [...] }
   - Si no encuentras: devuelve { match: "sin_cfdi", accion_sugerida: "registrar como ingreso sin facturar — alerta" }`,
  { label: 'match-cfdi', phase: 'Match', schema: { type: 'object', properties: { match: { type: 'string' }, uuid: { type: 'string' }, metodo_pago_cfdi: { type: 'string' } } } }
)

if (match.match === 'sin_cfdi') {
  log('⚠ Pago recibido sin CFDI emitido — alerta al usuario')
  return { status: 'sin_cfdi', pago_id, monto, alerta: 'Ingreso sin facturar — emitir CFDI o solicitar al cliente datos' }
}

if (match.match === 'ambiguo') {
  return { status: 'ambiguo', pago_id, candidatos: match.candidatos, accion: 'Requiere intervención humana para elegir UUID correcto' }
}

// ============================================================
// FASE 2: Emisión de REP si era PPD
// ============================================================
phase('CFDI tipo P')

let rep = null
if (match.metodo_pago_cfdi === 'PPD') {
  rep = await agent(
    `Emite CFDI tipo P (REP - Recibo Electrónico de Pago) usando mp_facturama_extendido.timbrar_con_pagos20 vinculado al UUID ${match.uuid}:
     - Monto del pago: ${monto}
     - Fecha: ${fecha}
     - Forma de pago: deducir de fuente (${fuente}) — MP/Conekta=04, SPEI=03, Stripe=04
     - DoctoRelacionado: ${match.uuid} con ImpPagado=${monto}

     Devuelve { uuid_rep, fecha_timbrado, status }.`,
    { label: 'timbrar-rep', phase: 'CFDI tipo P', schema: { type: 'object', properties: { uuid_rep: { type: 'string' }, status: { type: 'string' } } } }
  )
  log(`✅ REP emitido: ${rep.uuid_rep}`)
} else {
  log('CFDI original era PUE — no requiere REP')
}

// ============================================================
// FASE 3: Notificación al cliente
// ============================================================
phase('Notificación')

await agent(
  `Envía notificación al cliente vía WhatsApp confirmando recepción del pago:
   - "✅ Hemos recibido tu pago de $${monto}. Gracias!"
   - Si emitimos REP (${rep?.uuid_rep}): adjuntar PDF del REP
   - Template aprobable Meta: "utility_pago_confirmado"`,
  { label: 'notificar', phase: 'Notificación' }
)

// ============================================================
// FASE 4: Bitácora + actualización de status CFDI
// ============================================================
phase('Bitácora')

await agent(
  `Actualiza el CFDI ${match.uuid} en cfdi/.../${match.uuid}.json:
   - status: "cobrado"
   - pago_relacionado: { fuente: "${fuente}", pago_id: "${pago_id}", monto: ${monto}, fecha: "${fecha}" }
   - rep_uuid: "${rep?.uuid_rep || null}"

   Registra entrada en bitácora cobranza con timestamp.`,
  { label: 'actualizar-cfdi', phase: 'Bitácora' }
)

return {
  status: 'conciliado',
  cfdi_original_uuid: match.uuid,
  rep_uuid: rep?.uuid_rep,
  pago_id,
  fuente,
  monto,
}
