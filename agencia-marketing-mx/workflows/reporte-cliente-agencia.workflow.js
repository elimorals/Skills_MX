// Workflow ejecutable: reporte-cliente-agencia
//
// Cron día 2 de mes: para cada cliente activo de la agencia, descarga datos de
// Meta Ads + Google Ads + GA4 + métricas orgánicas, consolida, genera reporte,
// envía al cliente.
//
// args: { cliente_id?, mes?, anio? (si no, mes anterior automático), enviar?: bool=false }

export const meta = {
  name: 'reporte-cliente-agencia',
  description: 'Reporte mensual de agencia para cliente: descarga Meta Ads + Google Ads + GA4 + orgánico, consolida KPIs, genera insights + recomendaciones, opcionalmente envía. Cron día 2 / manual /agencia:reporte.',
  whenToUse: 'Cron mensual día 2 09:00 / manual al cierre del mes.',
  phases: [
    { title: 'Lookup cliente', detail: 'datos + canales activos + cuentas conectadas' },
    { title: 'Descarga datos', detail: 'parallel: Meta + Google + GA4 + orgánico' },
    { title: 'Consolidación', detail: 'KPIs + comparativa vs mes anterior' },
    { title: 'Insights', detail: 'winners + losers + recomendaciones IA' },
    { title: 'Distribución', detail: 'PDF + envío email/WA si aprobado' },
  ],
}

const { cliente_id, mes, anio, enviar = false } = args || {}
const hoy = new Date()
// Default: mes anterior
const fechaRef = anio && mes
  ? new Date(Date.UTC(anio, mes - 1, 1))
  : new Date(Date.UTC(hoy.getUTCFullYear(), hoy.getUTCMonth() - 1, 1))
const mesReporte = fechaRef.getUTCMonth() + 1
const anioReporte = fechaRef.getUTCFullYear()

log(`Reporte agencia | cliente=${cliente_id || 'TODOS'} | ${anioReporte}-${String(mesReporte).padStart(2, '0')}`)

phase('Lookup cliente')

const cliente = await agent(
  `Lee datos del cliente ${cliente_id || '(todos los activos)'}:
   - Nombre + industria + objetivo principal
   - Canales activos (meta_ads, google_ads, tiktok_ads, linkedin_ads, etc.)
   - Cuentas conectadas (IDs de cada plataforma)
   - Plan inversión del mes
   - Preferencias de reporte (formato, idioma, profundidad)

   Si cliente_id no se especifica: devuelve array de TODOS los clientes activos.`,
  { label: 'lookup', phase: 'Lookup cliente', schema: { type: 'object', properties: { clientes: { type: 'array' }, count: { type: 'number' } } } }
)

if (!cliente.clientes || cliente.clientes.length === 0) {
  return { status: 'sin_clientes', razon: 'No hay clientes activos' }
}

// Si hay múltiples, procesar uno por uno (pipeline). Para demo simplificado, procesamos primero
const c = cliente.clientes[0]
log(`Procesando: ${c.nombre} (${c.industria})`)

phase('Descarga datos')

const canalesData = await parallel(
  c.canales.map(canal => () => agent(
    `Descarga métricas del canal ${canal.tipo} para cuenta ${canal.cuenta_id} periodo ${anioReporte}-${mesReporte}:
     - Inversión total
     - Impresiones
     - Clicks
     - Conversiones
     - Ingresos atribuidos
     - Top 5 campañas/anuncios por desempeño
     - Comparativa día a día

     Para meta_ads: usar Meta Marketing API
     Para google_ads: usar Google Ads API
     Para ga4: usar Google Analytics Data API
     Para orgánico: scrape o API correspondiente

     Devuelve datos crudos del canal.`,
    { label: `descarga-${canal.tipo}`, phase: 'Descarga datos', schema: { type: 'object', properties: { canal: { type: 'string' }, inversion: { type: 'number' }, conversiones: { type: 'number' } } } }
  ))
)

phase('Consolidación')

const consolidado = await agent(
  `Consolida los datos de ${canalesData.length} canales:

   Para cada canal: ${JSON.stringify(canalesData.filter(Boolean)).slice(0, 2000)}

   Calcula:
   - Inversión total cross-canal
   - Conversiones totales
   - CPA promedio (inversion / conversiones)
   - ROAS = ingresos / inversion
   - CTR ponderado
   - Comparativa vs mes anterior por canal (variación %)

   Devuelve estructura siguiendo schemas/reporte-mensual-cliente-output.schema.json.`,
  { label: 'consolidar', phase: 'Consolidación', schema: { type: 'object' } }
)

phase('Insights')

const insights = await agent(
  `Analiza el desempeño consolidado y genera insights estructurados:

   - WINNERS: campañas/anuncios con mejor ROAS, escalar
   - LOSERS: campañas a pausar o ajustar
   - RECOMENDACIONES próximo mes (3-5 acciones concretas con prioridad)
   - ALERTAS de atención (frequency cap alcanzado, audience fatigue, CPA en aumento)
   - OPORTUNIDADES no capitalizadas (segmentos sin explotar, formatos sin probar)

   Tono ejecutivo, sin jerga, con números específicos.`,
  { label: 'insights', phase: 'Insights', schema: { type: 'object', properties: { winners: { type: 'array' }, losers: { type: 'array' }, recomendaciones: { type: 'array' }, alertas_atencion: { type: 'array' } } } }
)

phase('Distribución')

const ruta = `reportes-agencia/${c.id || c.nombre}/${anioReporte}-${String(mesReporte).padStart(2, '0')}`

await agent(
  `Genera 2 archivos:
   - ${ruta}/reporte-completo.md (full markdown con todas las secciones)
   - ${ruta}/resumen-1pagina.md (resumen ejecutivo 1 página para WhatsApp/email)
   Y genera PDF presentable desde el markdown.`,
  { label: 'generar-pdf', phase: 'Distribución' }
)

if (enviar) {
  await agent(
    `Envía reporte al cliente ${c.nombre}:
     - Email: PDF adjunto + resumen 1-página inline
     - WhatsApp: link al PDF + 3 bullets clave
     - Agenda reunión 30 min para revisar (Calendly)`,
    { label: 'enviar-cliente', phase: 'Distribución' }
  )
}

return {
  cliente: c.nombre,
  periodo: `${anioReporte}-${String(mesReporte).padStart(2, '0')}`,
  canales_revisados: canalesData.filter(Boolean).length,
  kpis: consolidado.kpis_principales,
  insights,
  enviado_cliente: enviar,
  archivos: {
    completo: `${ruta}/reporte-completo.md`,
    resumen: `${ruta}/resumen-1pagina.md`,
  },
}
