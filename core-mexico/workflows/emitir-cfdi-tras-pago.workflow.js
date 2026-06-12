// Workflow ejecutable: emitir-cfdi-tras-pago
//
// Disparado por webhook handler de Stripe/MP/Conekta/Facturama tras confirmación de pago.
// Formaliza el flujo: webhook → cola → este workflow → CFDI timbrado → notificar cliente.
//
// args: { source, event_id, monto, fecha_pago, external_reference, cliente_rfc?, cliente_email?, cliente_wa? }

export const meta = {
  name: 'emitir-cfdi-tras-pago',
  description: 'Webhook de pago confirmado → emitir CFDI 4.0 automático + enviar al cliente. Formaliza la cola del webhook handler que estaba pendiente integrar con workflows.',
  whenToUse: 'Webhook handler post-pago tras retry queue exitoso.',
  phases: [
    { title: 'Lookup cliente', detail: 'recuperar datos fiscales del external_reference' },
    { title: 'Validar deducibilidad', detail: 'RFC + 69-B + status padrón' },
    { title: 'Emisión', detail: 'CFDI 4.0 con TipoComprobante I + MetodoPago PUE' },
    { title: 'Distribución', detail: 'enviar XML+PDF al cliente WA/email + bitácora' },
  ],
}

const { source, event_id, monto, fecha_pago, external_reference, cliente_rfc, cliente_email, cliente_wa } = args || {}
if (!source || !event_id || !monto) {
  throw new Error('args requeridos: { source, event_id, monto, fecha_pago, external_reference }')
}

log(`CFDI tras pago: ${source}:${event_id} | $${monto}`)

phase('Lookup cliente')

const cliente = await agent(
  `Busca datos fiscales del cliente correspondiente al external_reference="${external_reference}":
   1. Primero buscar en clientes/<external_reference>.json
   2. Si no existe, buscar por (monto=${monto}, fecha=${fecha_pago}) en ordenes/
   3. Si tampoco: usar cliente_rfc="${cliente_rfc || 'PUBLICO'}" (público en general XAXX010101000)

   Devuelve { rfc, razon_social, regimen, uso_cfdi_default, email, wa, encontrado: bool }`,
  { label: 'lookup-cliente', phase: 'Lookup cliente', schema: { type: 'object', properties: { rfc: { type: 'string' }, razon_social: { type: 'string' }, regimen: { type: 'string' }, encontrado: { type: 'boolean' } } } }
)

phase('Validar deducibilidad')

if (cliente.rfc !== 'XAXX010101000') {
  const validacion = await agent(
    `Valida RFC ${cliente.rfc} en padrón SAT + 69-B EFOS. Si está en 69-B definitivo: alertar que CFDI será no deducible.`,
    { label: 'validar-rfc', phase: 'Validar deducibilidad', schema: { type: 'object', properties: { en_padron: { type: 'boolean' }, en_69b_definitivo: { type: 'boolean' } } } }
  )

  if (validacion.en_69b_definitivo) {
    log(`⚠ Cliente ${cliente.rfc} en 69-B DEFINITIVO — CFDI será no deducible. Emitir igual.`)
  }
}

phase('Emisión')

const cfdi = await agent(
  `Emite CFDI 4.0 tipo I usando skill cfdi-emision + mp_facturama_extendido.timbrar_cfdi:
   - Emisor: configurado en .env (RFC + régimen del usuario)
   - Receptor: RFC ${cliente.rfc} | Razón social ${cliente.razon_social || 'PUBLICO EN GENERAL'} | Régimen ${cliente.regimen || '616'}
   - UsoCFDI: ${cliente.uso_cfdi_default || 'G03'}
   - MetodoPago: PUE (Pago en Una Exhibición — ya cobrado vía ${source})
   - FormaPago: ${source === 'spei' ? '03' : '04'} (SPEI o TDC)
   - Importe: ${monto}
   - Concepto: "Pago de servicios/productos (ref externa: ${external_reference})"
   - Moneda: MXN

   Devuelve { uuid, xml_b64, pdf_b64, fecha_timbrado, total }.`,
  { label: 'timbrar', phase: 'Emisión', schema: { type: 'object', properties: { uuid: { type: 'string' }, xml_b64: { type: 'string' }, pdf_b64: { type: 'string' } } } }
)

if (!cfdi.uuid) {
  return { status: 'fallo_timbrado', razon: 'PAC rechazó', detalle: cfdi }
}

log(`✅ CFDI timbrado: ${cfdi.uuid}`)

phase('Distribución')

const tasks = [
  () => agent(
    `Persiste el CFDI en cfdi/${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, '0')}/${cfdi.uuid}.json con xml + pdf + metadata { pago_fuente: "${source}", pago_id: "${event_id}", external_reference: "${external_reference}" }.`,
    { label: 'persistir', phase: 'Distribución' }
  ),
  () => agent(
    `Registra en bitácora webhooks/audit con webhook_event_id=${event_id} + cfdi_uuid=${cfdi.uuid} + monto=${monto}.`,
    { label: 'bitacora', phase: 'Distribución' }
  ),
]

const wa = cliente.wa || cliente_wa
const email = cliente.email || cliente_email

if (wa) {
  tasks.push(
    () => agent(
      `Envía CFDI al cliente vía WhatsApp al ${wa} con template "utility_cfdi_emitido" + PDF adjunto.`,
      { label: 'enviar-wa', phase: 'Distribución' }
    )
  )
}
if (email) {
  tasks.push(
    () => agent(
      `Envía CFDI al cliente vía email al ${email} con asunto "Tu factura CFDI ${cfdi.uuid}" + XML y PDF adjuntos.`,
      { label: 'enviar-email', phase: 'Distribución' }
    )
  )
}

await parallel(tasks)

return {
  status: 'completado',
  webhook_source: source,
  webhook_event_id: event_id,
  cfdi_uuid: cfdi.uuid,
  cliente_rfc: cliente.rfc,
  monto,
  enviado_wa: !!wa,
  enviado_email: !!email,
}
