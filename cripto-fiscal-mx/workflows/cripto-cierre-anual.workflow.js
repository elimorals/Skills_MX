// Workflow ejecutable: cripto-cierre-anual
//
// Variante específica de cierre cripto enfocada en preparar la INFORMACIÓN
// que se va a comparar contra los reportes CARF 2026 que los exchanges
// enviarán al SAT (vs declaracion-anual-cripto.workflow.js que enfatiza
// el cálculo fiscal completo).
//
// Objetivo: dejar al cliente listo para "no sorpresas" cuando llegue la
// notificación del SAT con los datos que el exchange reportó.
//
// Invocar con: Workflow({scriptPath: "cripto-fiscal-mx/workflows/cripto-cierre-anual.workflow.js", args: {...}})
//
// Inputs en `args`:
//   {
//     rfc: string,
//     ejercicio: number,
//     exchanges_reportables?: string[],  // ["bitso", "binance", "coinbase", "kraken"]
//   }

export const meta = {
  name: 'cripto-cierre-anual',
  description: 'Cierre anual cripto enfocado en preparar conciliación contra reportes CARF que los exchanges enviarán al SAT en 2026+. Identifica exposición vs declarado.',
  whenToUse: 'Diciembre o enero — antes que el exchange envíe su reporte CARF al SAT',
  phases: [
    { title: 'Saldos', detail: 'parallel: pull saldos al 31-dic por exchange + wallets propias' },
    { title: 'Operaciones', detail: 'fetch ops del año por exchange' },
    { title: 'Estimación', detail: 'qué reportará cada exchange al SAT según umbrales CARF' },
    { title: 'Comparación', detail: 'qué declarará el cliente vs qué verá el SAT' },
    { title: 'Output', detail: 'plan de regularización + estimación riesgo' },
  ],
}

const {
  rfc,
  ejercicio,
  exchanges_reportables = ['bitso', 'binance', 'coinbase', 'kraken'],
} = args || {}

if (!rfc || !ejercicio) {
  throw new Error('args requeridos: { rfc, ejercicio, [exchanges_reportables] }')
}

log(`Cierre cripto CARF — RFC ${rfc.slice(0, 4)}*** — ejercicio ${ejercicio}`)

// ============================================================
// FASE 1: Saldos al 31-dic por exchange
// ============================================================
phase('Saldos')

const saldos = await parallel(exchanges_reportables.map((exch) => () => agent(
  `Obtén saldo al 31-dic-${ejercicio} en ${exch} para el RFC ${rfc}.
   Si ${exch} tiene MCP dedicado (mp_bitso), úsalo. Si no, instruir al usuario que provea export oficial.
   Devuelve: { exchange: "${exch}", saldo_total_mxn, por_activo: {BTC: 0.5, ETH: 2.3, USDC: 1500} }`,
  { label: `saldo-${exch}`, phase: 'Saldos', schema: saldoSchema() }
)))

const porExchange = Object.fromEntries(exchanges_reportables.map((e, i) => [e, saldos[i]]))
const saldoTotalMxn = saldos.reduce((sum, s) => sum + (s?.saldo_total_mxn || 0), 0)

log(`Saldo cripto total al 31-dic: $${Math.round(saldoTotalMxn).toLocaleString('es-MX')} MXN`)

// ============================================================
// FASE 2: Operaciones del año
// ============================================================
phase('Operaciones')

const operaciones = await parallel(exchanges_reportables.map((exch) => () => agent(
  `Cuenta operaciones totales del año ${ejercicio} en ${exch}: compras, ventas, permutas.
   Devuelve metadata sin detalle (sólo conteos + sumas).
   { exchange: "${exch}", ops_count, volumen_mxn_anio, ultima_op_fecha }`,
  { label: `ops-${exch}`, phase: 'Operaciones', schema: opsSchema() }
)))

// ============================================================
// FASE 3: Estimación qué reportará cada exchange al SAT
// ============================================================
phase('Estimación')

const estimacionCarf = await agent(
  `Estima qué reportará cada exchange al SAT bajo CARF 2026 para el ejercicio ${ejercicio}:

   Umbrales CARF:
   - Saldo > $200,000 MXN al cierre: SE REPORTA (regla Ley Fintech para ITF, equivalente CARF)
   - Movimientos totales > $50,000 USD anuales: SE REPORTA cualquier saldo
   - Cuenta abierta < 1 año: revisión adicional

   Para cada exchange:
   ${exchanges_reportables.map((e, i) => `
   - ${e}: saldo $${(porExchange[e] || {}).saldo_total_mxn || 0} MXN, ops ${(operaciones[i] || {}).ops_count || 0}, volumen $${(operaciones[i] || {}).volumen_mxn_anio || 0}
   `).join('')}

   Devuelve por exchange: { reportara: bool, razon, datos_estimados_que_envia_al_sat: {...} }`,
  { label: 'estimacion-carf', phase: 'Estimación', schema: estimacionSchema() }
)

// ============================================================
// FASE 4: Comparación qué el cliente va a declarar vs qué verá el SAT
// ============================================================
phase('Comparación')

const comparacion = await agent(
  `Lee el reporte de la última declaración del cliente (si existe en cripto-fiscal/${ejercicio}/${rfc.slice(0, 4)}-resumen-${ejercicio}.md).
   Compara:
   - Ingresos cripto declarados por cliente
   - Saldos finales declarados
   - vs estimación de qué reportarán los exchanges

   Identifica gaps:
   - Diferencia > 5%: alerta para revisar
   - Diferencia > 20%: alerta crítica — el cliente podría enfrentar requerimiento SAT
   - Exchange reportable no incluido en declaración: alerta crítica

   Estimación exchange-SAT: ${JSON.stringify(estimacionCarf).slice(0, 2000)}`,
  { label: 'comparacion-carf', phase: 'Comparación', schema: comparacionSchema() }
)

// ============================================================
// FASE 5: Output
// ============================================================
phase('Output')

const ruta = `cripto-fiscal/${ejercicio}/${rfc.slice(0, 4)}-cierre-carf`

await parallel([
  () => agent(
    `Genera \`${ruta}.md\` con plan de regularización:
     - Resumen saldos al 31-dic por exchange
     - Qué reportará cada exchange al SAT (estimación)
     - Brecha vs lo declarado
     - Plan para regularizar antes de que llegue notificación SAT
     - Cronograma sugerido (declaración complementaria, papel de trabajo, etc.)`,
    { label: 'plan-regularizacion', phase: 'Output' }
  ),
  () => agent(
    `Genera \`${ruta}-checklist.md\` con acciones inmediatas:
     [ ] Validar saldos con captura oficial del exchange (PDF)
     [ ] Si exchange reportará > $200k MXN: confirmar declaración del periodo
     [ ] Si hay self-custody no declarado: agregar a expediente
     [ ] Programar revisión con contador cripto en enero
     [ ] Conservar expediente firmado (Art. 30 CFF — 5 años)`,
    { label: 'checklist', phase: 'Output' }
  ),
])

return {
  status: 'completado',
  rfc: rfc.slice(0, 4) + '***',
  ejercicio,
  saldo_total_31dic_mxn: saldoTotalMxn,
  exchanges_reportables_segun_carf: (estimacionCarf.por_exchange || []).filter(e => e.reportara).map(e => e.exchange),
  brecha_critica: comparacion.brecha_critica || false,
  recomendacion_principal: comparacion.recomendacion_principal || 'Validar con contador cripto especializado',
  artefactos: {
    plan: `${ruta}.md`,
    checklist: `${ruta}-checklist.md`,
  },
}

// ============================================================
// Schemas
// ============================================================
function saldoSchema() {
  return {
    type: 'object',
    properties: {
      exchange: { type: 'string' },
      saldo_total_mxn: { type: 'number' },
      por_activo: { type: 'object' },
    },
  }
}

function opsSchema() {
  return {
    type: 'object',
    properties: {
      exchange: { type: 'string' },
      ops_count: { type: 'number' },
      volumen_mxn_anio: { type: 'number' },
      ultima_op_fecha: { type: 'string' },
    },
  }
}

function estimacionSchema() {
  return {
    type: 'object',
    properties: {
      por_exchange: { type: 'array' },
      total_reportable_mxn: { type: 'number' },
    },
  }
}

function comparacionSchema() {
  return {
    type: 'object',
    properties: {
      brecha_critica: { type: 'boolean' },
      diferencia_pct: { type: 'number' },
      gaps: { type: 'array' },
      recomendacion_principal: { type: 'string' },
    },
  }
}
