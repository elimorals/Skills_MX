// Workflow ejecutable: sync-multicanal
//
// Sincroniza inventario y pricing entre Mercado Libre, Shopify MX y Amazon MX.
// Detecta SKUs con discrepancias y consolida un reporte de acción.
//
// Invocar con: Workflow({scriptPath: "ecommerce-mx/workflows/sync-multicanal.workflow.js", args: {...}})
//
// Inputs esperados en `args`:
//   {
//     seller_id: string,                    // ID interno del seller
//     canales?: string[],                   // ["mercado_libre", "shopify", "amazon_mx"]
//     skus_focus?: string[],                // SKUs específicos; si vacío → top 50 vendedores
//     auto_corregir_stock?: boolean,        // default false — solo reporta
//     umbral_pricing_diff_pct?: number,     // default 5 — alerta si diff > 5%
//   }

export const meta = {
  name: 'sync-multicanal',
  description: 'Sincroniza inventario y pricing entre Mercado Libre, Shopify MX y Amazon MX. Detecta discrepancias de stock/precio, calcula impacto en pedidos pendientes, genera reporte ejecutivo con acciones priorizadas.',
  whenToUse: '/ecommerce:sync-inventario, cron diario, o detección de discrepancia por hook',
  phases: [
    { title: 'Fetch', detail: 'parallel: pull listings/inventory por canal' },
    { title: 'Cruce', detail: 'consolidar SKUs por canal, detectar discrepancias' },
    { title: 'Análisis', detail: 'parallel: impacto stock + impacto pricing + competencia' },
    { title: 'Acción', detail: 'auto-corregir si flag, genera órdenes correctivas' },
    { title: 'Output', detail: 'reporte + alertas WA + dashboard CSV' },
  ],
}

const {
  seller_id,
  canales = ['mercado_libre', 'shopify', 'amazon_mx'],
  skus_focus = [],
  auto_corregir_stock = false,
  umbral_pricing_diff_pct = 5,
} = args || {}

if (!seller_id) {
  throw new Error('args requeridos: { seller_id, [canales], [skus_focus] }')
}

log(`Sync multicanal — seller ${seller_id} — ${canales.length} canales`)

// ============================================================
// FASE 1: Fetch paralelo por canal
// ============================================================
phase('Fetch')

const fetches = await parallel(canales.map((canal) => () => {
  const mcp = {
    'mercado_libre': 'mp_mercado_libre',
    'shopify': 'mp_shopify_mx',
    'amazon_mx': 'mp_amazon_mx_seller',
  }[canal]

  if (!mcp) {
    throw new Error(`Canal no soportado: ${canal}`)
  }

  return agent(
    `Usa ${mcp} para listar inventario activo del seller ${seller_id}.
     Si skus_focus tiene contenido (${skus_focus.length} SKUs), filtra solo esos.
     Devuelve: { canal: "${canal}", listings: [{sku, titulo, precio_mxn, stock, status, comision_pct, link}] }`,
    { label: `fetch-${canal}`, phase: 'Fetch', schema: listingsSchema() }
  )
}))

const porCanal = Object.fromEntries(canales.map((c, i) => [c, fetches[i]]))

// ============================================================
// FASE 2: Cruce de SKUs
// ============================================================
phase('Cruce')

const cruce = await agent(
  `Consolida los listings de todos los canales por SKU. Para cada SKU presente en >= 2 canales calcula:
   - stock_diff: max - min entre canales
   - pricing_diff_pct: ((max_precio - min_precio) / min_precio) * 100
   - canales_presente: lista de canales donde aparece
   - canales_faltante: canales donde NO aparece

   Inputs:
   ${JSON.stringify(porCanal).slice(0, 3000)}

   Marca cada SKU con severidad:
   - critica: stock=0 en algún canal pero >0 en otro, o pricing_diff > 20%
   - alta: pricing_diff > ${umbral_pricing_diff_pct}% pero <= 20%
   - media: stock_diff > 5
   - baja: el resto
   `,
  { label: 'cruzar', phase: 'Cruce', schema: cruceSchema() }
)

// ============================================================
// FASE 3: Análisis paralelo
// ============================================================
phase('Análisis')

const analisis = await parallel([
  () => agent(
    `Analiza impacto de stock. De los SKUs marcados critica/alta:
     ¿Cuántas órdenes pendientes están en riesgo? Usa mp_mercado_libre.list_orders + mp_shopify_mx.list_orders + mp_amazon_mx_seller.list_orders con status="unshipped".
     Devuelve riesgo por SKU.

     SKUs críticos: ${JSON.stringify((cruce.skus || []).filter(s => s.severidad === 'critica').slice(0, 20))}`,
    { label: 'impacto-stock', phase: 'Análisis', schema: impactoSchema() }
  ),
  () => agent(
    `Analiza posicionamiento de pricing. Para los top 10 SKUs de mayor volumen:
     - Compara con competidores en ML (mp_mercado_libre.search by tipo + ubicación)
     - Identifica si estás 15%+ arriba o abajo del promedio
     - Recomienda ajuste de precio por canal
     `,
    { label: 'pricing-competidor', phase: 'Análisis', schema: pricingSchema() }
  ),
  () => agent(
    `Detecta canibalización entre canales: SKUs vendiendo en ML que también están en Shopify del mismo seller.
     Es problemático si: comisión ML es 13-16%, comisión Amazon 8-15%, Shopify 0% pero requiere ads.
     Recomienda canal óptimo por SKU según margen neto.`,
    { label: 'canibalizacion', phase: 'Análisis', schema: canibalizacionSchema() }
  ),
])

const [impactoStock, pricingCompetidor, canibalizacion] = analisis

// ============================================================
// FASE 4: Acción correctiva (si auto_corregir_stock)
// ============================================================
phase('Acción')

let correcciones = null
if (auto_corregir_stock) {
  correcciones = await agent(
    `Para los SKUs marcados severidad=critica con stock_diff > 0, propaga el stock_max al stock_min usando:
     - mp_mercado_libre.update_listing(stock)
     - mp_shopify_mx.update_inventory(quantity)
     - mp_amazon_mx_seller.update_inventory(sku, quantity)
     SOLO para discrepancias claras (no para los marcados "media" o "baja").
     Reporta ${JSON.stringify((cruce.skus || []).filter(s => s.severidad === 'critica').slice(0, 10))}`,
    { label: 'auto-corregir', phase: 'Acción', schema: correccionesSchema() }
  )
} else {
  log('auto_corregir_stock=false → solo reporta, no aplica cambios')
}

// ============================================================
// FASE 5: Output
// ============================================================
phase('Output')

const ruta = `ecommerce/${seller_id}/sync-${new Date().toISOString().slice(0, 10)}`

await parallel([
  () => agent(
    `Genera reporte ejecutivo \`${ruta}-report.md\`:
     - Total SKUs cruzados, con discrepancias críticas/altas/medias
     - Top 10 acciones priorizadas
     - Impacto stock en órdenes pendientes
     - Posicionamiento pricing vs competencia
     - Recomendación de canal óptimo por SKU TOP

     Datos: ${JSON.stringify({cruce: cruce?.resumen, impactoStock, pricingCompetidor, canibalizacion}).slice(0, 4000)}`,
    { label: 'reporte', phase: 'Output' }
  ),
  () => agent(
    `Genera CSV \`${ruta}-dashboard.csv\` con columnas: sku, titulo, canales_presente, stock_ml, stock_shopify, stock_amazon, precio_ml, precio_shopify, precio_amazon, pricing_diff_pct, severidad.`,
    { label: 'csv-dashboard', phase: 'Output' }
  ),
  () => agent(
    `Si hay SKUs criticos (>=3), envía alerta WhatsApp via mp_meta_whatsapp al seller ${seller_id}: "Detectadas N discrepancias críticas en sync multicanal. Revisar ${ruta}-report.md".`,
    { label: 'alerta-wa', phase: 'Output' }
  ),
])

return {
  status: 'completado',
  seller_id,
  canales_sincronizados: canales,
  skus_analizados: cruce?.total_skus || 0,
  skus_criticos: cruce?.skus_por_severidad?.critica || 0,
  acciones_aplicadas: correcciones ? correcciones.aplicadas_count : 0,
  artefactos: {
    reporte: `${ruta}-report.md`,
    csv: `${ruta}-dashboard.csv`,
  },
}

// ============================================================
// Schemas
// ============================================================
function listingsSchema() {
  return {
    type: 'object',
    properties: {
      canal: { type: 'string' },
      listings: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            sku: { type: 'string' },
            titulo: { type: 'string' },
            precio_mxn: { type: 'number' },
            stock: { type: 'number' },
            status: { type: 'string' },
            comision_pct: { type: 'number' },
            link: { type: 'string' },
          },
        },
      },
    },
  }
}

function cruceSchema() {
  return {
    type: 'object',
    properties: {
      total_skus: { type: 'number' },
      skus_por_severidad: { type: 'object' },
      skus: { type: 'array' },
      resumen: { type: 'object' },
    },
  }
}

function impactoSchema() {
  return {
    type: 'object',
    properties: {
      ordenes_en_riesgo: { type: 'number' },
      monto_riesgo_mxn: { type: 'number' },
      por_sku: { type: 'array' },
    },
  }
}

function pricingSchema() {
  return {
    type: 'object',
    properties: {
      sobre_precio: { type: 'array' },
      bajo_precio: { type: 'array' },
      recomendaciones_ajuste: { type: 'array' },
    },
  }
}

function canibalizacionSchema() {
  return {
    type: 'object',
    properties: {
      skus_multicanal: { type: 'array' },
      recomendacion_canal_optimo: { type: 'array' },
    },
  }
}

function correccionesSchema() {
  return {
    type: 'object',
    properties: {
      aplicadas_count: { type: 'number' },
      fallidas_count: { type: 'number' },
      detalle: { type: 'array' },
    },
  }
}
