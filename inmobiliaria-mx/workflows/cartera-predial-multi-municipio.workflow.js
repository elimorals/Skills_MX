// Workflow ejecutable: cartera-predial-multi-municipio
//
// Consulta predial en PARALELO para N propiedades en distintos municipios.
// Cierra el loop con cobranza-renta-mensual.workflow.js cuando el adeudo afecta
// la operación del arrendador (no puede facturar si está moroso, etc.).
//
// Casos de uso:
// 1. Arrendador con 5 propiedades en distintos municipios → status consolidado.
// 2. Despacho contable manejando 50+ clientes con propiedades → cartera completa.
// 3. Due diligence pre-compra inmueble → verificar adeudo antes de cerrar.
// 4. Inmobiliaria con cartera de 100 inmuebles → vista global de adeudos.
//
// Invocar con: Workflow({scriptPath: "inmobiliaria-mx/workflows/cartera-predial-multi-municipio.workflow.js", args: {...}})
//
// Inputs en `args`:
//   {
//     cliente_rfc: string,                  // dueño de la cartera (opcional)
//     propiedades: [
//       {
//         id: string,                       // id interno (contrato, etiqueta)
//         estado: string,                   // "cdmx", "jal", "mich", etc.
//         municipio: string,                // "ciudad_de_mexico", "guadalajara"
//         cuenta_predial: string,           // clave catastral
//         tipo?: "urbano" | "rustico",      // solo para SACPI Michoacán
//         direccion?: string,               // para Mérida que busca por dirección
//         alias?: string,                   // nombre amigable de la propiedad
//         monto_renta_mensual?: number,     // contexto: cuánto renta este inmueble
//       }
//     ],
//     incluir_recomendaciones?: boolean,    // default true
//     enviar_alerta_whatsapp?: boolean,     // default false
//     tel_cliente?: string,                 // requerido si enviar_alerta_whatsapp=true
//   }

export const meta = {
  name: 'cartera-predial-multi-municipio',
  description: 'Consulta predial en paralelo para múltiples propiedades en distintos municipios. Consolida vencimientos, montos y recomienda priorización de pagos. Usa el catálogo central de municipios + plataformas SaaS (SACPI MICH).',
  whenToUse: 'Arrendador/despacho/inmobiliaria con propiedades distribuidas. Cron mensual o on-demand.',
  phases: [
    { title: 'Validación', detail: 'verificar cada propiedad contra catálogo + clasificar por tipo de consulta' },
    { title: 'Consulta', detail: 'parallel: una consulta por propiedad (directa, SACPI, no-soportada)' },
    { title: 'Consolidación', detail: 'sumar adeudos, identificar vencimientos críticos, calcular descuentos por pronto pago' },
    { title: 'Análisis', detail: 'priorizar pagos + detectar oportunidades (descuentos enero/febrero, planes de pago)' },
    { title: 'Output', detail: 'reporte ejecutivo + CSV cartera + alerta WhatsApp opcional' },
  ],
}

const {
  cliente_rfc,
  propiedades = [],
  incluir_recomendaciones = true,
  enviar_alerta_whatsapp = false,
  tel_cliente,
} = args || {}

if (!Array.isArray(propiedades) || propiedades.length === 0) {
  throw new Error('args.propiedades requerido: array con al menos 1 propiedad {estado, municipio, cuenta_predial}')
}

if (enviar_alerta_whatsapp && !tel_cliente) {
  throw new Error('args.tel_cliente requerido cuando enviar_alerta_whatsapp=true')
}

log(`Cartera predial — ${propiedades.length} propiedades${cliente_rfc ? ` — cliente ${cliente_rfc.slice(0, 4)}***` : ''}`)

// ============================================================
// FASE 1: Validación + clasificación por tipo de consulta
// ============================================================
phase('Validación')

const clasificacion = await agent(
  `Clasifica las ${propiedades.length} propiedades por tipo de consulta predial.
   Inputs: ${JSON.stringify(propiedades).slice(0, 4000)}

   Para cada propiedad determina:
   1. Categoría:
      - "catalogo_directo": municipio con portal_predial_url verificado en catálogo (validado=True)
      - "saas_sacpi": municipio MICH cubierto por SACPI (consultar via shared.plataformas_saas_mx.consulta_sacpi)
      - "merida_por_direccion": yuc/merida busca por calle+numero, no por cuenta
      - "captcha_humano": pue/puebla (form con campo 'answer')
      - "no_soportado": municipio sin URL en catálogo (incluir en reporte como pendiente)

   2. Valida que cuenta_predial tenga formato razonable (8-20 caracteres alfanuméricos).

   3. Para SACPI, mapear nombre del municipio al código INEGI 3 dígitos
      (usar shared.plataformas_saas_mx.codigo_municipio_sacpi).

   Devuelve estructura:
   {
     por_categoria: {catalogo_directo: [...], saas_sacpi: [...], ...},
     total_consultables: N,
     total_no_soportados: M,
     advertencias: [...]
   }`,
  { label: 'clasificar', phase: 'Validación', schema: clasificacionSchema() }
)

log(`Consultables: ${clasificacion.total_consultables}/${propiedades.length}`)
if (clasificacion.total_no_soportados > 0) {
  log(`⚠ ${clasificacion.total_no_soportados} propiedades sin soporte en catálogo`)
}

// ============================================================
// FASE 2: Consultas en PARALELO
// ============================================================
phase('Consulta')

// Construir tareas por categoría
const tareas = []

// 2.1 Catálogo directo: usa el MCP municipal correspondiente
for (const prop of (clasificacion.por_categoria?.catalogo_directo || [])) {
  tareas.push({ propiedad: prop, fn: () => agent(
    `Consulta predial de la propiedad ${prop.id || prop.alias || prop.cuenta_predial}:
     - Estado: ${prop.estado}
     - Municipio: ${prop.municipio}
     - Cuenta: ${prop.cuenta_predial}

     Usa el MCP municipal correspondiente (mp_${prop.estado}_municipal si existe,
     o llama a shared.catalogo_municipios_mx.buscar_portal_predial + shared.playwright_municipal_generic.consulta_portal).

     Devuelve: { propiedad_id, estatus, adeudo_total_mxn, bimestres_pendientes, conceptos: [...], url_consultada }`,
    { label: `consulta-${prop.id || prop.cuenta_predial.slice(-4)}`, phase: 'Consulta', schema: consultaSchema() }
  )})
}

// 2.2 SACPI Michoacán
for (const prop of (clasificacion.por_categoria?.saas_sacpi || [])) {
  tareas.push({ propiedad: prop, fn: () => agent(
    `Consulta predial Michoacán via SACPI:
     - Código municipio: ${prop.codigo_sacpi || 'pendiente lookup'}
     - Cuenta: ${prop.cuenta_predial}
     - Tipo: ${prop.tipo || 'urbano'}

     Usar shared.plataformas_saas_mx.consulta_sacpi(municipio_codigo, cuenta, tipo).`,
    { label: `sacpi-${prop.id || prop.cuenta_predial.slice(-4)}`, phase: 'Consulta', schema: consultaSchema() }
  )})
}

// 2.3 Mérida por dirección
for (const prop of (clasificacion.por_categoria?.merida_por_direccion || [])) {
  tareas.push({ propiedad: prop, fn: () => agent(
    `Consulta predial Mérida por dirección:
     - Calle: ${prop.direccion}
     - Usar mp_merida_municipal.predial_real() — busca por calle/número, no por cuenta.`,
    { label: `merida-${prop.id || (prop.direccion || '').slice(0, 20)}`, phase: 'Consulta', schema: consultaSchema() }
  )})
}

// 2.4 Puebla con CAPTCHA — generar instrucción para humano-en-loop
for (const prop of (clasificacion.por_categoria?.captcha_humano || [])) {
  tareas.push({ propiedad: prop, fn: () => agent(
    `Puebla requiere CAPTCHA en form predial. NO consultar automáticamente.
     Generar URL pre-llenada para que humano complete: https://srvappayt.pueblacapital.gob.mx:7016/pabel/iniciopredial
     Cuenta: ${prop.cuenta_predial}. Devolver { status: "pendiente_humano", url, instrucciones }.`,
    { label: `puebla-pending-${prop.id || prop.cuenta_predial.slice(-4)}`, phase: 'Consulta' }
  )})
}

// Ejecutar todas en paralelo
const resultadosBrutos = await parallel(tareas.map(t => t.fn))

// Pegar de vuelta el contexto de la propiedad (para no perder qué es qué)
const resultados = tareas.map((t, i) => ({
  propiedad: t.propiedad,
  resultado: resultadosBrutos[i],
}))

// No soportados: agregarlos al output con status correcto
for (const prop of (clasificacion.por_categoria?.no_soportado || [])) {
  resultados.push({
    propiedad: prop,
    resultado: { status: 'no_soportado_en_catalogo', adeudo_total_mxn: null },
  })
}

log(`Consultas completas: ${resultados.filter(r => r.resultado?.adeudo_total_mxn != null).length}/${propiedades.length}`)

// ============================================================
// FASE 3: Consolidación
// ============================================================
phase('Consolidación')

const consolidado = await agent(
  `Consolida los resultados de ${resultados.length} consultas:

   Inputs: ${JSON.stringify(resultados).slice(0, 6000)}

   Calcula:
   - adeudo_total_cartera_mxn: suma de adeudos
   - propiedades_al_corriente: count
   - propiedades_con_adeudo: count
   - propiedades_pendientes_humano: count (Puebla CAPTCHA)
   - propiedades_no_soportadas: count
   - bimestres_vencidos_total: sum de bimestres pendientes
   - top5_mayores_adeudos: lista propiedades ordenadas por monto desc

   Por propiedad calcula:
   - dias_vencido: si bimestre venció (días)
   - recargo_estimado_mxn: típicamente 10% mes vencido (varía por municipio)
   - descuento_pronto_pago_disponible_mxn: enero ~15%, febrero ~10%, marzo ~5%
   - oportunidad_neta_mxn: si pagas en enero, ahorras X

   Marca alertas:
   - "critico": adeudo > 3 bimestres O monto > monto_renta × 3
   - "advertencia": vence en < 30 días
   - "ok": al corriente`,
  { label: 'consolidar', phase: 'Consolidación', schema: consolidadoSchema() }
)

log(`Adeudo total cartera: $${(consolidado.adeudo_total_cartera_mxn || 0).toLocaleString('es-MX')} MXN`)
log(`Propiedades con adeudo: ${consolidado.propiedades_con_adeudo || 0}/${propiedades.length}`)

// ============================================================
// FASE 4: Análisis + recomendaciones
// ============================================================
phase('Análisis')

let recomendaciones = null
if (incluir_recomendaciones) {
  recomendaciones = await agent(
    `Genera plan de acción priorizado para la cartera:

     Cartera consolidada: ${JSON.stringify(consolidado).slice(0, 3000)}

     Recomienda en orden:
     1. URGENTE: pagos que generan más recargo si se demoran 30 días más
     2. OPORTUNIDAD: pagos donde aplica descuento pronto pago (enero/febrero/marzo)
     3. PLANES DE PAGO: propiedades con > 6 bimestres vencidos donde conviene plan municipal
     4. NO-AUTOMATIZABLES: Puebla CAPTCHA, anti-bot Mérida — proceso manual

     Para cada recomendación da:
     - "accion": qué hacer
     - "fecha_limite": cuándo
     - "ahorro_potencial_mxn": cuánto se ahorra si se hace ahora vs después
     - "url_pago_directo": link al portal del municipio para el cliente`,
    { label: 'plan-accion', phase: 'Análisis', schema: recomendacionesSchema() }
  )
}

// ============================================================
// FASE 5: Output
// ============================================================
phase('Output')

const ruta = `cartera-predial/${cliente_rfc ? cliente_rfc.slice(0, 4) : 'cliente'}/${new Date().toISOString().slice(0, 10)}`

await parallel([
  () => agent(
    `Genera reporte ejecutivo \`${ruta}-cartera.md\` con:
     - Resumen ejecutivo: $${consolidado.adeudo_total_cartera_mxn || 0} adeudo total, N propiedades, M en riesgo
     - Tabla por propiedad: alias/id, ubicación, adeudo, estatus, alerta
     - Top 5 mayores adeudos con plan de acción
     - Calendario de vencimientos próximos (30/60/90 días)
     - Propiedades pendientes humano (Puebla CAPTCHA) con URLs pre-llenadas
     - Propiedades sin soporte automatizado + cómo consultar manual
     ${incluir_recomendaciones ? '- Plan accionable con ahorro potencial' : ''}`,
    { label: 'reporte-md', phase: 'Output' }
  ),
  () => agent(
    `Genera CSV \`${ruta}-cartera.csv\` con columnas:
     id, alias, estado, municipio, cuenta_predial, adeudo_total_mxn, bimestres_pendientes,
     dias_vencido, recargo_estimado_mxn, descuento_pronto_pago_mxn, alerta, url_pago.

     Listo para abrir en Excel/Sheets.`,
    { label: 'csv-cartera', phase: 'Output' }
  ),
  ...(enviar_alerta_whatsapp && tel_cliente && (consolidado.propiedades_con_adeudo || 0) > 0
    ? [() => agent(
        `Envía alerta WhatsApp al ${tel_cliente.slice(-4)} via mp_meta_whatsapp template "alerta_cartera_predial":
         "Tu cartera tiene $${consolidado.adeudo_total_cartera_mxn} MXN en adeudo predial repartido en ${consolidado.propiedades_con_adeudo} propiedades. Ver reporte completo: <link>"`,
        { label: 'wa-alerta', phase: 'Output' }
      )]
    : []),
])

return {
  status: 'completado',
  cliente_rfc: cliente_rfc ? cliente_rfc.slice(0, 4) + '***' : null,
  propiedades_total: propiedades.length,
  propiedades_consultadas_ok: resultados.filter(r => r.resultado?.adeudo_total_mxn != null).length,
  propiedades_pendientes_humano: consolidado.propiedades_pendientes_humano || 0,
  propiedades_no_soportadas: consolidado.propiedades_no_soportadas || 0,
  adeudo_total_cartera_mxn: consolidado.adeudo_total_cartera_mxn || 0,
  ahorro_potencial_pronto_pago_mxn: recomendaciones?.ahorro_total_disponible_mxn || 0,
  artefactos: {
    reporte: `${ruta}-cartera.md`,
    csv: `${ruta}-cartera.csv`,
  },
}

// ============================================================
// Schemas
// ============================================================
function clasificacionSchema() {
  return {
    type: 'object',
    properties: {
      por_categoria: {
        type: 'object',
        properties: {
          catalogo_directo: { type: 'array' },
          saas_sacpi: { type: 'array' },
          merida_por_direccion: { type: 'array' },
          captcha_humano: { type: 'array' },
          no_soportado: { type: 'array' },
        },
      },
      total_consultables: { type: 'number' },
      total_no_soportados: { type: 'number' },
      advertencias: { type: 'array', items: { type: 'string' } },
    },
  }
}

function consultaSchema() {
  return {
    type: 'object',
    properties: {
      propiedad_id: { type: 'string' },
      estatus: { type: 'string' },
      adeudo_total_mxn: { type: ['number', 'null'] },
      bimestres_pendientes: { type: 'number' },
      conceptos: { type: 'array' },
      url_consultada: { type: 'string' },
      status: { type: 'string' },
    },
  }
}

function consolidadoSchema() {
  return {
    type: 'object',
    required: ['adeudo_total_cartera_mxn'],
    properties: {
      adeudo_total_cartera_mxn: { type: 'number' },
      propiedades_al_corriente: { type: 'number' },
      propiedades_con_adeudo: { type: 'number' },
      propiedades_pendientes_humano: { type: 'number' },
      propiedades_no_soportadas: { type: 'number' },
      bimestres_vencidos_total: { type: 'number' },
      top5_mayores_adeudos: { type: 'array' },
      por_propiedad: { type: 'array' },
    },
  }
}

function recomendacionesSchema() {
  return {
    type: 'object',
    properties: {
      acciones_urgentes: { type: 'array' },
      oportunidades_pronto_pago: { type: 'array' },
      planes_pago_recomendados: { type: 'array' },
      no_automatizables: { type: 'array' },
      ahorro_total_disponible_mxn: { type: 'number' },
    },
  }
}
