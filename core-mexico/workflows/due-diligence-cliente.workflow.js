// Workflow ejecutable: due-diligence-cliente
//
// Verifica un RFC contra todas las fuentes públicas SAT antes de aceptar al cliente.
// Si está en 69-B definitivo o tiene riesgo alto → ABORTAR.
//
// args: { rfc, nombre_aceptado?, autorizado_buro?: boolean }

export const meta = {
  name: 'due-diligence-cliente',
  description: 'Due diligence pre-onboarding cliente: RFC + padrón SAT + 69-B EFOS + 69 incumplidos + CSF + opcional Buró de Crédito (con autorización). Devuelve score riesgo y veredicto GO/HOLD/STOP.',
  whenToUse: '/core:due-diligence antes de aceptar cliente nuevo (especialmente PMs con tickets > $50k MXN).',
  phases: [
    { title: 'Estructural', detail: 'validación RFC formato' },
    { title: 'SAT públicos', detail: 'parallel: padrón + 69-B + 69 incumplidos' },
    { title: 'Buró', detail: 'opcional con autorización formal del cliente' },
    { title: 'Score', detail: 'consolidación + veredicto' },
  ],
}

const { rfc, nombre_aceptado, autorizado_buro = false } = args || {}
if (!rfc) throw new Error('args.rfc requerido')

log(`Due diligence: ${rfc}`)

// ============================================================
// FASE 1: Validación estructural (local, gratis)
// ============================================================
phase('Estructural')

const estructura = await agent(
  `Valida estructura del RFC ${rfc} con skill rfc-validacion. Devuelve { valido: bool, tipo: "PF"|"PM", advertencias: [] }`,
  { label: 'estructura', phase: 'Estructural', schema: { type: 'object', properties: { valido: { type: 'boolean' }, tipo: { enum: ['PF', 'PM'] } } } }
)

if (!estructura.valido) {
  return { veredicto: 'STOP', razon: 'RFC inválido estructuralmente', score: 0 }
}

// ============================================================
// FASE 2: Verificaciones públicas SAT (paralelo — todas son independientes)
// ============================================================
phase('SAT públicos')

const satChecks = await parallel([
  () => agent(
    `Consulta RFC ${rfc} en padrón SAT (mp_sat_portal.consultar_padron). Devuelve { en_padron: bool, razon_social: string, regimen: string, status: "activo"|"suspendido" }`,
    { label: 'padron', phase: 'SAT públicos', schema: { type: 'object', properties: { en_padron: { type: 'boolean' }, razon_social: { type: 'string' }, status: { type: 'string' } } } }
  ),
  () => agent(
    `Consulta RFC ${rfc} en lista 69-B EFOS (mp_sat_portal.consultar_69b_efos). Devuelve { en_69b: bool, estado: "presunto"|"definitivo"|"desvirtuado"|null, fecha_publicacion: string }`,
    { label: '69b', phase: 'SAT públicos', schema: { type: 'object', properties: { en_69b: { type: 'boolean' }, estado: { type: 'string' } } } }
  ),
  () => agent(
    `Consulta RFC ${rfc} en lista 69 (incumplidos firmes). Devuelve { en_69: bool, motivo: string }`,
    { label: '69-incumplidos', phase: 'SAT públicos', schema: { type: 'object', properties: { en_69: { type: 'boolean' }, motivo: { type: 'string' } } } }
  ),
])

const [padron, lista69b, lista69] = satChecks

// Veredicto temprano: 69-B definitivo es STOP automático
if (lista69b.en_69b && lista69b.estado === 'definitivo') {
  return {
    veredicto: 'STOP',
    razon: 'RFC en 69-B DEFINITIVO: operar con este cliente expone a no deducibilidad e incluso multas',
    detalle: { lista69b, padron },
    score: 0,
  }
}

if (!padron.en_padron) {
  return {
    veredicto: 'STOP',
    razon: 'RFC no encontrado en padrón SAT',
    score: 5,
  }
}

if (nombre_aceptado && padron.razon_social && !padron.razon_social.toLowerCase().includes(nombre_aceptado.toLowerCase())) {
  log(`⚠ Razón social del padrón (${padron.razon_social}) no coincide con esperado (${nombre_aceptado})`)
}

// ============================================================
// FASE 3: Buró de Crédito (opcional, requiere autorización)
// ============================================================
phase('Buró')

let buroResult = null
if (autorizado_buro) {
  buroResult = await agent(
    `Consulta el Buró de Crédito del RFC ${rfc} via mp_buro_credito_personal con autorización del titular ya documentada. Devuelve { score_credito: number, mop_grave_ultimo_anio: number, monto_atraso_total: number }`,
    { label: 'buro', phase: 'Buró', schema: { type: 'object', properties: { score_credito: { type: 'number' } } } }
  )
} else {
  log('Buró de Crédito omitido (sin autorización del titular)')
}

// ============================================================
// FASE 4: Consolidación + veredicto
// ============================================================
phase('Score')

let score = 100
const motivos = []

if (lista69b.en_69b && lista69b.estado === 'presunto') {
  score -= 40
  motivos.push('RFC en 69-B PRESUNTO (-40)')
}
if (lista69.en_69) {
  score -= 25
  motivos.push('RFC en lista 69 incumplidos firmes (-25)')
}
if (padron.status === 'suspendido') {
  score -= 30
  motivos.push('RFC suspendido en padrón (-30)')
}
if (buroResult) {
  if (buroResult.mop_grave_ultimo_anio > 0) {
    score -= 20
    motivos.push(`MOP grave último año (-20)`)
  }
  if (buroResult.score_credito && buroResult.score_credito < 600) {
    score -= 15
    motivos.push(`Score buró < 600 (-15)`)
  }
}

const veredicto = score >= 80 ? 'GO' : score >= 50 ? 'HOLD' : 'STOP'

return {
  veredicto,
  score,
  motivos,
  rfc,
  razon_social: padron.razon_social,
  regimen: padron.regimen,
  detalle: { padron, lista69b, lista69, buro: buroResult },
  recomendaciones:
    veredicto === 'GO'
      ? ['Continuar onboarding normal']
      : veredicto === 'HOLD'
        ? ['Solicitar CSF reciente', 'Considerar anticipo', 'Limitar crédito si ticket > $50k']
        : ['NO aceptar al cliente', 'Documentar razón en bitácora'],
}
