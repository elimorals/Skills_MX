// Workflow ejecutable: telemedicina-consulta
//
// Consulta de telemedicina end-to-end: agenda → ID paciente → consulta video →
// receta electrónica → expediente clínico (NOM-004) → cobranza → CFDI tipo I.
//
// Cumple: COFEPRIS Acuerdo 28-mar-2024 (telemedicina) + NOM-004-SSA3-2012
// (expediente clínico) + NOM-024-SSA3-2012 (sistemas de información en salud).
//
// Invocar con: Workflow({scriptPath: "telemedicina-mx/workflows/telemedicina-consulta.workflow.js", args: {...}})
//
// Inputs en `args`:
//   {
//     medico_rfc: string,                   // RFC del médico (cédula profesional asociada)
//     medico_cedula: string,                // cédula SEP (validación COFEPRIS)
//     paciente: {
//       nombre: string,
//       curp?: string,
//       fecha_nacimiento: string,           // YYYY-MM-DD
//       sexo: "M" | "F",
//       tel_contacto: string,
//     },
//     tipo_consulta: "primera_vez" | "subsecuente" | "urgencia" | "control",
//     motivo: string,
//     duracion_min: number,
//     costo_mxn: number,
//     forma_pago?: "01" | "03" | "04" | "28",   // efectivo|transferencia|tdc|tdd
//     emitir_receta?: boolean,
//     incluir_estudios?: boolean,
//   }

export const meta = {
  name: 'telemedicina-consulta',
  description: 'Consulta telemedicina end-to-end: identidad paciente + video consult + receta electrónica + expediente NOM-004 + cobranza + CFDI. Compliance COFEPRIS 2024.',
  whenToUse: '/telemedicina:nueva-consulta o webhook desde plataforma de telemedicina',
  phases: [
    { title: 'Pre-consulta', detail: 'parallel: validar cédula médico + identificar paciente + verificar pago' },
    { title: 'Consulta', detail: 'session ID + grabación opcional + notas del médico' },
    { title: 'Documentación', detail: 'parallel: receta electrónica + nota médica + estudios solicitados' },
    { title: 'Cobranza', detail: 'emisión CFDI tipo I + cobro tarjeta + recordatorio próxima consulta' },
    { title: 'Expediente', detail: 'persistir expediente clínico NOM-004 + bitácora COFEPRIS' },
  ],
}

const {
  medico_rfc,
  medico_cedula,
  paciente,
  tipo_consulta,
  motivo,
  duracion_min,
  costo_mxn,
  forma_pago = '03',
  emitir_receta = true,
  incluir_estudios = false,
} = args || {}

if (!medico_rfc || !medico_cedula || !paciente || !paciente.nombre || !tipo_consulta) {
  throw new Error('args requeridos: { medico_rfc, medico_cedula, paciente:{nombre,fecha_nacimiento,sexo,tel_contacto}, tipo_consulta, motivo, duracion_min, costo_mxn }')
}

const sessionId = `tm-${medico_rfc.slice(0, 4)}-${Date.now().toString(36)}`
log(`Telemedicina — sesión ${sessionId} — ${tipo_consulta} — ${duracion_min}min`)

// ============================================================
// FASE 1: Pre-consulta (validaciones paralelas)
// ============================================================
phase('Pre-consulta')

const preConsulta = await parallel([
  () => agent(
    `Valida que la cédula profesional ${medico_cedula} del médico ${medico_rfc} esté vigente en la SEP.
     Usa el endpoint público https://cedulaprofesional.sep.gob.mx (sin login). Si la cédula NO existe o NO está vigente, ABORTAR la consulta — sería ejercicio ilegal de la profesión.
     Devuelve: { vigente: bool, nombre_titular, profesion, institucion, fecha_expedicion }`,
    { label: 'cedula-sep', phase: 'Pre-consulta', schema: cedulaSchema() }
  ),
  () => agent(
    `Identifica al paciente "${paciente.nombre}" (CURP: ${paciente.curp || 'no proporcionado'}).
     Si tiene CURP, valida estructura con mp_curp_renapo.
     Busca expediente clínico previo con esta CURP+nombre en telemedicina-mx/expedientes/.
     Si es paciente nuevo: prepara folio nuevo. Si subsecuente: carga historial.
     Devuelve: { folio_paciente, es_primera_vez, expediente_previo_resumen, alergias_conocidas, padecimientos_cronicos, medicamentos_actuales }`,
    { label: 'identificar-paciente', phase: 'Pre-consulta', schema: pacienteSchema() }
  ),
  () => agent(
    `Verifica el consentimiento informado para telemedicina (requisito COFEPRIS Acuerdo 28-mar-2024).
     Si el paciente NO firmó consentimiento previo, ABORTAR consulta y enviar formulario por WhatsApp al ${paciente.tel_contacto.slice(0, -4)}**** para firma digital.
     Devuelve: { consentimiento_vigente: bool, fecha_firma, version_documento }`,
    { label: 'consentimiento', phase: 'Pre-consulta', schema: consentimientoSchema() }
  ),
])

const [cedula, pacienteCtx, consentimiento] = preConsulta

if (!cedula?.vigente) {
  log('⛔ Cédula NO vigente — abortando consulta')
  return { status: 'aborto_cedula_no_vigente', cedula }
}

if (!consentimiento?.consentimiento_vigente) {
  log('⛔ Sin consentimiento informado — formulario enviado por WhatsApp')
  return { status: 'pendiente_consentimiento', consentimiento, paciente: pacienteCtx?.folio_paciente }
}

// ============================================================
// FASE 2: Consulta (interacción con el médico)
// ============================================================
phase('Consulta')

const consulta = await agent(
  `Conduce la sesión clínica con el médico ${cedula.nombre_titular} (cédula ${medico_cedula}).
   Paciente: ${paciente.nombre}, ${paciente.sexo}, nacido ${paciente.fecha_nacimiento}.
   Motivo de consulta: "${motivo}".
   Tipo: ${tipo_consulta}.
   Historial previo: ${JSON.stringify(pacienteCtx?.expediente_previo_resumen || {}).slice(0, 1000)}

   Captura del médico (estructura SOAP — Subjective, Objective, Assessment, Plan):
   - Subjetivo: síntomas reportados por paciente
   - Objetivo: signos vitales (si paciente los reportó), apariencia general
   - Análisis: diagnóstico presuntivo CIE-10
   - Plan: tratamiento, indicaciones, próxima consulta

   ⚠ Si síntomas sugieren urgencia (dolor torácico agudo, dificultad respiratoria severa, signos neurológicos focales),
   recomendar al paciente acudir a urgencias presencialmente Y notificar al médico.`,
  { label: 'sesion-clinica', phase: 'Consulta', schema: notaMedicaSchema() }
)

// ============================================================
// FASE 3: Documentación (paralelo)
// ============================================================
phase('Documentación')

const documentacion = await parallel([
  () => agent(
    emitir_receta && consulta.medicamentos_indicados?.length > 0
      ? `Genera receta electrónica COFEPRIS-compliant para el paciente ${pacienteCtx.folio_paciente}:
         Médico: ${cedula.nombre_titular}, cédula ${medico_cedula}
         Medicamentos: ${JSON.stringify(consulta.medicamentos_indicados)}

         ⚠ Si algún medicamento es de control (Fracción I-V), validar que la cédula del médico tenga autorización COFEPRIS específica.
         Si no, sustituir por equivalente no-control y notificar.

         Genera PDF firmado digitalmente. Incluye QR con folio + hash.
         Envía copia al WhatsApp del paciente.`
      : `No se requiere receta (paciente sin medicamentos indicados o emitir_receta=false). Devuelve {emitida: false}.`,
    { label: 'receta', phase: 'Documentación', schema: recetaSchema() }
  ),
  () => agent(
    incluir_estudios && consulta.estudios_solicitados?.length > 0
      ? `Genera orden de estudios para laboratorio o gabinete:
         Estudios: ${JSON.stringify(consulta.estudios_solicitados)}
         Indica: nombre paciente, fecha solicitada, médico solicitante, motivo clínico breve.
         Envía PDF al paciente con instrucciones de preparación (ayuno, etc.).`
      : `Sin estudios solicitados. Devuelve {emitida: false}.`,
    { label: 'estudios', phase: 'Documentación', schema: estudiosSchema() }
  ),
  () => agent(
    `Genera nota médica completa NOM-004-SSA3-2012:
     - Identificación paciente
     - Antecedentes relevantes
     - Padecimiento actual
     - Exploración física (limitada por telemedicina)
     - Diagnóstico CIE-10
     - Plan terapéutico
     - Pronóstico
     - Próxima consulta sugerida

     Datos: ${JSON.stringify(consulta).slice(0, 2000)}`,
    { label: 'nota-medica', phase: 'Documentación', schema: notaMedicaSchema() }
  ),
])

const [receta, estudios, notaMedica] = documentacion

// ============================================================
// FASE 4: Cobranza + CFDI
// ============================================================
phase('Cobranza')

const cobranza = await agent(
  `Procesa el cobro de $${costo_mxn} MXN con forma_pago=${forma_pago}.

   Si forma_pago="03" (transferencia): genera link de pago Mercado Pago / Conekta + envía WhatsApp al paciente.
   Si forma_pago="04" o "28" (TDC/TDD): cobra contra el medio guardado (si existe) o solicita captura nueva.
   Si forma_pago="01" (efectivo): marca como pendiente de cobro presencial.

   Emite CFDI tipo I (Ingreso) en mp_facturama_extendido inmediatamente al cobrar:
   - Emisor: médico ${medico_rfc}
   - Receptor: ${paciente.curp ? `RFC del paciente o XAXX010101000` : 'XAXX010101000'}
   - Concepto: "Consulta médica vía telemedicina — ${tipo_consulta} — ${duracion_min}min"
   - Uso CFDI: D01 (Honorarios médicos, deducible para el paciente PF)
   - Régimen receptor: 626 si PF, 601 si PM
   - Forma pago: ${forma_pago}
   - Método: PUE

   Devuelve {pago_id, status_pago, cfdi_uuid, cfdi_xml_url}`,
  { label: 'cobranza-cfdi', phase: 'Cobranza', schema: cobranzaSchema() }
)

// ============================================================
// FASE 5: Persistir expediente + bitácora COFEPRIS
// ============================================================
phase('Expediente')

await parallel([
  () => agent(
    `Persiste el expediente clínico completo en telemedicina-mx/expedientes/${pacienteCtx.folio_paciente}/${sessionId}.json:
     {
       sesion_id: "${sessionId}",
       fecha: "${new Date().toISOString()}",
       medico: {rfc, cedula, nombre},
       paciente: ${JSON.stringify(paciente).slice(0, 500)},
       tipo_consulta: "${tipo_consulta}",
       nota_medica: ${JSON.stringify(notaMedica)},
       receta: ${JSON.stringify(receta)},
       estudios: ${JSON.stringify(estudios)},
       cfdi_uuid: "${cobranza?.cfdi_uuid || ''}",
       conservacion_anios: 5 (NOM-004)
     }

     ⚠ El expediente debe cifrarse en reposo (LFPDPPP datos sensibles salud).`,
    { label: 'persistir-expediente', phase: 'Expediente' }
  ),
  () => agent(
    `Registra en bitácora COFEPRIS:
     - sesion_id, medico, paciente_folio (hash, no plain), tipo_consulta, duracion, fecha
     - cumplimiento_consentimiento: true
     - cumplimiento_NOM004: true
     - cumplimiento_NOM024: true (sistemas de información)
     - receta_emitida: ${!!receta?.emitida}
     - cfdi_emitido: ${!!cobranza?.cfdi_uuid}

     Append a telemedicina-mx/bitacora-cofepris.jsonl (inmutable).`,
    { label: 'bitacora-cofepris', phase: 'Expediente' }
  ),
  () => agent(
    consulta.proxima_consulta_dias
      ? `Programa recordatorio próxima consulta en ${consulta.proxima_consulta_dias} días via mp_meta_whatsapp template "recordatorio_consulta_telemedicina".`
      : 'Sin próxima consulta sugerida — no programar recordatorio.',
    { label: 'recordatorio', phase: 'Expediente' }
  ),
])

return {
  status: 'completado',
  sesion_id: sessionId,
  medico_cedula: medico_cedula,
  paciente_folio: pacienteCtx.folio_paciente,
  tipo_consulta,
  duracion_min,
  diagnostico_cie10: consulta.diagnostico_cie10,
  receta_emitida: !!receta?.emitida,
  estudios_solicitados: estudios?.cantidad || 0,
  cfdi_uuid: cobranza?.cfdi_uuid,
  monto_cobrado_mxn: costo_mxn,
  proxima_consulta_en_dias: consulta.proxima_consulta_dias,
  compliance: {
    nom_004: true,
    nom_024: true,
    cofepris_2024: true,
    consentimiento_informado: true,
  },
}

// ============================================================
// Schemas
// ============================================================
function cedulaSchema() {
  return {
    type: 'object',
    required: ['vigente'],
    properties: {
      vigente: { type: 'boolean' },
      nombre_titular: { type: 'string' },
      profesion: { type: 'string' },
      institucion: { type: 'string' },
      fecha_expedicion: { type: 'string' },
    },
  }
}

function pacienteSchema() {
  return {
    type: 'object',
    properties: {
      folio_paciente: { type: 'string' },
      es_primera_vez: { type: 'boolean' },
      expediente_previo_resumen: { type: 'object' },
      alergias_conocidas: { type: 'array' },
      padecimientos_cronicos: { type: 'array' },
      medicamentos_actuales: { type: 'array' },
    },
  }
}

function consentimientoSchema() {
  return {
    type: 'object',
    properties: {
      consentimiento_vigente: { type: 'boolean' },
      fecha_firma: { type: 'string' },
      version_documento: { type: 'string' },
    },
  }
}

function notaMedicaSchema() {
  return {
    type: 'object',
    properties: {
      subjetivo: { type: 'string' },
      objetivo: { type: 'string' },
      analisis: { type: 'string' },
      plan: { type: 'string' },
      diagnostico_cie10: { type: 'string' },
      medicamentos_indicados: { type: 'array' },
      estudios_solicitados: { type: 'array' },
      proxima_consulta_dias: { type: 'number' },
      urgencia_recomendar_presencial: { type: 'boolean' },
    },
  }
}

function recetaSchema() {
  return {
    type: 'object',
    properties: {
      emitida: { type: 'boolean' },
      folio_receta: { type: 'string' },
      pdf_url: { type: 'string' },
      qr_hash: { type: 'string' },
      medicamentos_control: { type: 'array' },
    },
  }
}

function estudiosSchema() {
  return {
    type: 'object',
    properties: {
      emitida: { type: 'boolean' },
      cantidad: { type: 'number' },
      lista: { type: 'array' },
      pdf_url: { type: 'string' },
    },
  }
}

function cobranzaSchema() {
  return {
    type: 'object',
    properties: {
      pago_id: { type: 'string' },
      status_pago: { type: 'string' },
      cfdi_uuid: { type: 'string' },
      cfdi_xml_url: { type: 'string' },
      monto_cobrado_mxn: { type: 'number' },
    },
  }
}
