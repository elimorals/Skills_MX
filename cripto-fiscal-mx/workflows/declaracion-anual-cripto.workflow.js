// Workflow ejecutable: declaracion-anual-cripto
//
// Orquesta la declaración anual completa de operaciones cripto para una PF mexicana.
//
// Invocar con: Workflow({scriptPath: "cripto-fiscal-mx/workflows/declaracion-anual-cripto.workflow.js", args: {...}})
//
// Inputs esperados en `args`:
//   {
//     rfc: string,                          // RFC del contribuyente (se hashea para bitácora)
//     ejercicio: number,                    // año fiscal a declarar
//     exchanges?: string[],                 // ["bitso", "binance", "coinbase", "kraken"]
//     wallets_self_custody?: Array<{cadena: string, address: string}>,
//     incluir_nfts?: boolean,               // default true
//     metodo_costo_base?: "FIFO" | "promedio_ponderado",  // default FIFO
//     regenerar?: boolean                   // si true ignora caché
//   }

export const meta = {
  name: 'declaracion-anual-cripto',
  description: 'Declaración anual completa de operaciones cripto: importa de exchanges, reconstruye self-custody desde blockchain explorers, aplica FIFO, identifica permutas gravables, suma staking/airdrops/NFTs, evalúa riesgo CARF 2026, genera reporte SAT presentable y expediente de pruebas.',
  whenToUse: 'Cierre fiscal anual de cliente cripto (PF) en periodo enero-abril. También sirve para análisis "qué pasa si vendo todo" o auditoría posterior.',
  phases: [
    { title: 'Importación', detail: 'parallel: CSVs por exchange + blockchain explorers self-custody + TCs DOF anuales' },
    { title: 'Clasificación', detail: 'normalizar a schema OperacionCripto + enriquecer con precios MXN' },
    { title: 'Cálculos fiscales', detail: 'parallel: FIFO costo base + permutas + staking/airdrops + NFTs' },
    { title: 'Síntesis', detail: 'sumar acumulables Cap II/VI/IX + riesgo CARF 2026' },
    { title: 'Output', detail: 'reporte ejecutivo + expediente SAT + checklist declaración' },
  ],
}

const {
  rfc,
  ejercicio,
  exchanges = [],
  wallets_self_custody = [],
  incluir_nfts = true,
  metodo_costo_base = 'FIFO',
  regenerar = false,
} = args || {}

if (!rfc || !ejercicio) {
  throw new Error('args requeridos: { rfc, ejercicio, [exchanges], [wallets_self_custody] }')
}

log(`Declaración anual cripto — RFC ${rfc.slice(0, 4)}*** — ejercicio ${ejercicio}`)
log(`Fuentes: ${exchanges.length} exchanges + ${wallets_self_custody.length} wallets self-custody`)

// ============================================================
// FASE 1: Importación paralela de todas las fuentes
// ============================================================
phase('Importación')

const importacion = await parallel([
  // Exchanges centralizados
  ...exchanges.map((exch) => () => agent(
    `Importa todas las operaciones del exchange ${exch} para el ejercicio ${ejercicio} del RFC ${rfc}.
     Si ${exch} tiene MCP dedicado (mp_bitso para bitso, mp_binance_account para binance), úsalo.
     De lo contrario, usa el skill importar-operaciones-exchange con CSV oficial.
     Normaliza a schema OperacionCripto: {fecha_hora, exchange, tipo, activo_dado, cantidad_dada, activo_recibido, cantidad_recibida, valor_mxn_dia, fee_mxn, txid}.
     Si regenerar=${regenerar}, ignora caché.`,
    { label: `import-${exch}`, phase: 'Importación', schema: operacionesSchema() }
  )),
  // Wallets self-custody
  ...wallets_self_custody.map((w) => () => agent(
    `Reconstruye historial de la wallet ${w.address} en ${w.cadena} para ejercicio ${ejercicio}.
     Usa el skill tracking-wallets-self-custody con el explorer correspondiente (Etherscan, Polygonscan, Solscan, etc.).
     Clasifica cada tx: transferencia_in/out, permuta (DEX swap), stake_recompensa, airdrop, nft_mint/compra/venta.
     Enriquece con valor MXN del día (TC DOF + CoinGecko).`,
    { label: `wallet-${w.cadena}-${w.address.slice(0, 6)}`, phase: 'Importación', schema: operacionesSchema() }
  )),
  // TCs DOF del año completo
  () => agent(
    `Obtén la serie diaria USD/MXN del DOF para todo el ejercicio ${ejercicio} usando mp_banxico.get_tc_serie.
     Devuelve objeto {YYYY-MM-DD: tc_dof_usd_mxn}.`,
    { label: 'tcs-dof-anuales', phase: 'Importación', schema: tcsAnualesSchema() }
  ),
  // CFDIs recibidos por servicios cripto (comisiones)
  () => agent(
    `Descarga CFDIs recibidos por servicios del RFC ${rfc} de exchanges con CFDI (Bitso principalmente)
     durante ejercicio ${ejercicio} usando mp_sat_portal.descargar_cfdi_masivo.
     Filtra por uso "G03" (gastos en general) o emisor conocido como exchange.`,
    { label: 'cfdis-comisiones', phase: 'Importación', schema: cfdisSchema() }
  ),
])

const tcsDof = importacion[importacion.length - 2]
const cfdisComisiones = importacion[importacion.length - 1]
const fuentesOperaciones = importacion.slice(0, -2).filter(Boolean)

// Aplanar todas las operaciones de todas las fuentes
const todasOperaciones = fuentesOperaciones.flatMap((f) => f?.operaciones || [])
log(`Importación completa: ${todasOperaciones.length} operaciones agregadas`)

if (todasOperaciones.length === 0) {
  log('⚠ Sin operaciones para procesar. Verifica fuentes configuradas.')
  return { status: 'sin_operaciones', advertencia: 'Configura exchanges o wallets en args' }
}

// ============================================================
// FASE 2: Clasificación y enriquecimiento
// ============================================================
phase('Clasificación')

const clasificacion = await agent(
  `Toma las ${todasOperaciones.length} operaciones consolidadas y:
   1. Detecta duplicados entre exchange CSV y blockchain explorer (misma tx_id o monto+fecha+activo)
   2. Verifica que cada operación tenga valor_mxn_dia. Si falta, calcula con TC DOF correspondiente
   3. Clasifica explícitamente: compra, venta, permuta, stake_recompensa, lending_interes, airdrop, transferencia_in/out, nft_mint, nft_compra, nft_venta
   4. Identifica operaciones con costos_base_indeterminados (no se sabe cuánto se pagó) — alerta crítica

   Operaciones (primeras 20 como muestra): ${JSON.stringify(todasOperaciones.slice(0, 20))}
   TCs DOF disponibles: ${Object.keys(tcsDof?.serie || {}).length} fechas`,
  { label: 'clasificar', phase: 'Clasificación', schema: clasificacionSchema() }
)

const operacionesLimpias = clasificacion.operaciones_clasificadas

// ============================================================
// FASE 3: Cálculos fiscales paralelos (4 dimensiones independientes)
// ============================================================
phase('Cálculos fiscales')

const calculos = await parallel([
  () => agent(
    `Aplica skill calcular-costo-base-fifo a las ${operacionesLimpias.length} operaciones.
     Método: ${metodo_costo_base}.
     Reporta ganancia_realizada, perdida_realizada, neto_gravable, inventario_final.`,
    { label: 'fifo', phase: 'Cálculos fiscales', schema: fifoSchema() }
  ),
  () => agent(
    `Aplica skill permuta-cripto-cripto-gravable.
     Identifica todas las operaciones tipo "permuta" donde ambos activos son cripto (no MXN).
     Calcula ganancia/pérdida por permuta usando costo base FIFO del lado entregado.
     Reporta neto_gravable_permutas_mxn.`,
    { label: 'permutas', phase: 'Cálculos fiscales', schema: permutasSchema() }
  ),
  () => agent(
    `Aplica skill staking-y-airdrops-ingreso.
     Identifica stake_recompensa, lending_interes, airdrop.
     Separa por régimen: Cap IX (demás ingresos) vs Cap VI (intereses con CFDI).
     Reporta acumulables por categoría.`,
    { label: 'rendimientos', phase: 'Cálculos fiscales', schema: rendimientosSchema() }
  ),
  ...(incluir_nfts ? [
    () => agent(
      `Aplica skill nft-enajenacion-bienes.
       Identifica operaciones NFT (mint, compra, venta, royalty_recibido).
       Calcula ganancia/pérdida por NFT con costo base + gas + comisión marketplace.
       Reporta neto_gravable_enajenacion + royalties_acumulables.`,
      { label: 'nfts', phase: 'Cálculos fiscales', schema: nftsSchema() }
    ),
  ] : []),
])

const [fifo, permutas, rendimientos, nfts] = [
  calculos[0],
  calculos[1],
  calculos[2],
  incluir_nfts ? calculos[3] : null,
]

// ============================================================
// FASE 4: Síntesis fiscal y CARF
// ============================================================
phase('Síntesis')

const sintesis = await agent(
  `Consolida todos los resultados en un resumen fiscal:

   FIFO: ${JSON.stringify(fifo)}
   Permutas: ${JSON.stringify(permutas)}
   Rendimientos: ${JSON.stringify(rendimientos)}
   NFTs: ${incluir_nfts ? JSON.stringify(nfts) : 'no incluidos'}
   Comisiones CFDI deducibles: ${JSON.stringify(cfdisComisiones)}

   Genera estructura:
   {
     ingresos_acumulables_cap_ix: ganancia_FIFO + permutas_neto + staking + airdrops + (royalties_NFT si aplica),
     intereses_cap_vi: lending_interes,
     enajenacion_bienes_cap_iv: ventas_FIFO + nfts_enajenacion,
     gastos_deducibles: fees + comisiones + gas_self_custody,
     utilidad_gravable_mxn,
     isr_estimado_aplicar_art_152_tarifa,
   }

   Además calcula riesgo CARF 2026 con skill riesgo-carf-2026:
   - Saldos al 31-dic-${ejercicio} en exchanges centralizados regulados
   - ¿Algún exchange reportará al SAT por > $50k USD?
   - Identificar exposición vs lo declarado.`,
  { label: 'sintesis', phase: 'Síntesis', schema: sintesisSchema() }
)

// ============================================================
// FASE 5: Output — reporte + expediente
// ============================================================
phase('Output')

const ruta = `cripto-fiscal/${ejercicio}/${rfc.slice(0, 4)}`

await parallel([
  () => agent(
    `Genera el reporte ejecutivo en \`${ruta}-resumen-${ejercicio}.md\` con:
     - Total operaciones procesadas
     - Ingresos acumulables por capítulo (II, VI, IX)
     - ISR estimado con detalle de cálculo
     - Riesgo CARF: qué exchange reportará qué saldos
     - Top 5 operaciones más impactantes
     - Recomendaciones para declaración anual
     - Disclaimer: requiere validación contador certificado.

     Datos: ${JSON.stringify(sintesis)}`,
    { label: 'reporte-md', phase: 'Output' }
  ),
  () => agent(
    `Aplica skill documento-pruebas-sat para generar expediente completo en \`${ruta}-expediente/\`.
     Incluye CSVs originales, hojas FIFO, justificación de criterios, conciliación XLSX.
     Output: hash SHA256 del ZIP + checklist pre-envío.`,
    { label: 'expediente-sat', phase: 'Output', schema: expedienteSchema() }
  ),
  () => agent(
    `Genera checklist accionable en \`${ruta}-checklist-declaracion.md\`:
     [ ] Validar criterios con contador certificado cripto
     [ ] Subir expediente firmado con e.firma a backup off-site
     [ ] Capturar acumulables Cap IX en DeclaraSAT línea X
     [ ] Capturar intereses Cap VI en DeclaraSAT línea Y
     [ ] Si CARF aplicable: preparar conciliación vs reporte exchange
     [ ] Conservar expediente 5 años (Art. 30 CFF)`,
    { label: 'checklist', phase: 'Output' }
  ),
])

return {
  status: 'completado',
  ejercicio,
  rfc_hash: rfc.slice(0, 4) + '***',
  metodo_costo_base,
  operaciones_procesadas: operacionesLimpias.length,
  fuentes_usadas: exchanges.length + wallets_self_custody.length,
  resumen_fiscal: sintesis,
  artefactos: {
    reporte: `${ruta}-resumen-${ejercicio}.md`,
    expediente: `${ruta}-expediente/`,
    checklist: `${ruta}-checklist-declaracion.md`,
  },
  vigencia_validada: false,
  siguiente_paso: 'Validar con contador certificado cripto antes de presentar declaración',
}

// ============================================================
// Schemas
// ============================================================
function operacionesSchema() {
  return {
    type: 'object',
    properties: {
      fuente: { type: 'string' },
      operaciones_count: { type: 'number' },
      operaciones: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            fecha_hora: { type: 'string' },
            exchange: { type: 'string' },
            tipo: { type: 'string' },
            activo_dado: { type: ['string', 'null'] },
            cantidad_dada: { type: ['string', 'number', 'null'] },
            activo_recibido: { type: 'string' },
            cantidad_recibida: { type: ['string', 'number'] },
            valor_mxn_dia: { type: ['string', 'number', 'null'] },
            fee_mxn: { type: ['string', 'number'] },
            txid: { type: ['string', 'null'] },
          },
        },
      },
    },
  }
}

function tcsAnualesSchema() {
  return {
    type: 'object',
    properties: {
      ejercicio: { type: 'number' },
      moneda: { type: 'string' },
      serie: { type: 'object' },
      dias_habil: { type: 'number' },
    },
  }
}

function cfdisSchema() {
  return {
    type: 'object',
    properties: {
      cfdis_count: { type: 'number' },
      total_mxn: { type: 'number' },
      iva_acreditable_mxn: { type: 'number' },
      cfdis: { type: 'array' },
    },
  }
}

function clasificacionSchema() {
  return {
    type: 'object',
    properties: {
      operaciones_clasificadas: { type: 'array' },
      duplicados_eliminados: { type: 'number' },
      sin_valor_mxn: { type: 'number' },
      costos_base_indeterminados: { type: 'number' },
      advertencias: { type: 'array', items: { type: 'string' } },
    },
  }
}

function fifoSchema() {
  return {
    type: 'object',
    properties: {
      metodo: { type: 'string' },
      operaciones_procesadas: { type: 'number' },
      ganancia_realizada_mxn: { type: 'string' },
      perdida_realizada_mxn: { type: 'string' },
      neto_gravable_mxn: { type: 'string' },
      holdings_finales_valor_mxn: { type: 'string' },
      ganancia_latente_mxn: { type: 'string' },
    },
  }
}

function permutasSchema() {
  return {
    type: 'object',
    properties: {
      permutas_detectadas: { type: 'number' },
      valor_mxn_total_realizado: { type: 'string' },
      neto_gravable_permutas_mxn: { type: 'string' },
      permutas: { type: 'array' },
    },
  }
}

function rendimientosSchema() {
  return {
    type: 'object',
    properties: {
      staking_acumulable_mxn: { type: 'string' },
      lending_acumulable_mxn: { type: 'string' },
      airdrops_acumulable_mxn: { type: 'string' },
      total_cap_ix_mxn: { type: 'string' },
      total_cap_vi_mxn: { type: 'string' },
      detalle: { type: 'array' },
    },
  }
}

function nftsSchema() {
  return {
    type: 'object',
    properties: {
      nfts_vendidos: { type: 'number' },
      ganancia_total_mxn: { type: 'string' },
      perdida_total_mxn: { type: 'string' },
      neto_gravable_mxn: { type: 'string' },
      royalties_acumulables_mxn: { type: 'string' },
      nfts_en_inventario: { type: 'number' },
    },
  }
}

function sintesisSchema() {
  return {
    type: 'object',
    required: ['ingresos_acumulables_cap_ix', 'utilidad_gravable_mxn'],
    properties: {
      ingresos_acumulables_cap_ix: { type: 'number' },
      intereses_cap_vi: { type: 'number' },
      enajenacion_bienes_cap_iv: { type: 'number' },
      gastos_deducibles: { type: 'number' },
      utilidad_gravable_mxn: { type: 'number' },
      isr_estimado_mxn: { type: 'number' },
      riesgo_carf: { type: 'object' },
      vigencia_validada: { type: 'boolean' },
    },
  }
}

function expedienteSchema() {
  return {
    type: 'object',
    properties: {
      expediente_path: { type: 'string' },
      archivos_count: { type: 'number' },
      tamanio_mb: { type: 'number' },
      hash_zip_sha256: { type: 'string' },
    },
  }
}
