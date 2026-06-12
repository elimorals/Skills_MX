// Workflow ejecutable: auditoria-fiscal-mensual
//
// Distinto a cierre-fiscal-mensual (que es PROSPECTIVO — calcula pago provisional para emitir).
// Este es RETROSPECTIVO: revisa un mes ya cerrado para detectar errores subsanables antes de
// que SAT los observe. Útil para despachos contables que dan servicio mensual de revisión.
//
// args: { rfc_cliente, ejercicio, mes, regimen, profundidad?: "basica"|"completa" (default basica) }

export const meta = {
  name: 'auditoria-fiscal-mensual',
  description: 'Auditoría fiscal mensual retrospectiva: descarga CFDIs SAT del mes + consolida + detecta errores subsanables (CFDIs PPD sin REP, proveedores 69-B post-timbrado, retenciones mal aplicadas, depósitos sin facturar). Genera reporte ejecutivo con riesgo + impacto fiscal estimado. Distinto a cierre-fiscal-mensual (prospectivo).',
  whenToUse: '/freelancers:auditoria-mensual o cron día 25 del mes siguiente al revisado. Servicio típico de despachos contables.',
  phases: [
    { title: 'Descarga', detail: 'CFDIs SAT del mes completo (ya cerrado)' },
    { title: 'Consolidación', detail: 'totalizar por concepto + cruzar emitidos/recibidos' },
    { title: 'Detección', detail: 'parallel: REP faltantes, 69-B post, retenciones, depósitos efectivo' },
    { title: 'Cuantificación', detail: 'impacto fiscal estimado por hallazgo' },
    { title: 'Reporte', detail: 'ejecutivo con acciones priorizadas' },
  ],
}

const { rfc_cliente, ejercicio, mes, regimen, profundidad = 'basica' } = args || {}
if (!rfc_cliente || !ejercicio || !mes || !regimen) {
  throw new Error('args requeridos: { rfc_cliente, ejercicio, mes, regimen }')
}

log(`Auditoría retrospectiva ${rfc_cliente} | ${ejercicio}-${String(mes).padStart(2, '0')} | ${regimen}`)

phase('Descarga')

const datos = await agent(
  `Descarga todos los CFDIs del periodo ${ejercicio}-${mes} vía mp_sat_portal.descargar_cfdi_masivo (emitidos + recibidos). El mes YA está cerrado, debería estar completo.
   Devuelve { total_emitidos, total_recibidos, cfdis_emitidos: [...], cfdis_recibidos: [...] }.`,
  { label: 'descarga-sat', phase: 'Descarga', schema: { type: 'object', properties: { total_emitidos: { type: 'number' }, total_recibidos: { type: 'number' } } } }
)

if (!datos.cfdis_emitidos && !datos.cfdis_recibidos) {
  return { status: 'sin_datos', razon: 'No hay CFDIs en el periodo' }
}

phase('Consolidación')

const consolidado = await agent(
  `Consolida los CFDIs:
   - Total ingresos cobrados (CFDIs I + REPs)
   - Total gastos pagados (CFDIs recibidos pagados)
   - Cancelaciones del periodo
   - CFDIs PPD emitidos sin su REP correspondiente
   - Proveedores únicos (RFCs)
   Devuelve estructura totalizada.`,
  { label: 'consolidar', phase: 'Consolidación', schema: { type: 'object' } }
)

phase('Detección')

const tasks = [
  () => agent(
    `Para cada CFDI emitido tipo I con metodoPago=PPD, verifica que tiene REP correspondiente emitido en plazo (≤ 5 días tras pago). Lista los que faltan o están vencidos.`,
    { label: 'reps-faltantes', phase: 'Detección', schema: { type: 'object', properties: { faltantes: { type: 'array' }, vencidos: { type: 'array' } } } }
  ),
  () => agent(
    `Para cada RFC emisor de los CFDIs recibidos del periodo, verifica si entró a lista 69-B DEFINITIVO después de la fecha de timbrado del CFDI. Si sí: el CFDI fue válido al momento pero gasto debe excluirse de deducibles. Devuelve { rfcs_69b_post: [...], monto_a_excluir }.`,
    { label: 'detector-69b-post', phase: 'Detección', schema: { type: 'object', properties: { rfcs_69b_post: { type: 'array' }, monto_a_excluir: { type: 'number' } } } }
  ),
  () => agent(
    `Verifica que las retenciones aplicadas en los CFDIs del periodo sean correctas según el régimen:
     - PFAE 612 receptor PM: 10% ISR + 10.67% IVA
     - RESICO PF 626 receptor PM: 1.25% ISR
     - Arrendamiento 614: 10% ISR
     - REPSE: 6% IVA por servicio especializado
     Detecta retenciones omitidas o mal calculadas.`,
    { label: 'retenciones-mal', phase: 'Detección', schema: { type: 'object', properties: { errores: { type: 'array' }, impacto_mxn: { type: 'number' } } } }
  ),
  () => agent(
    `Cruza depósitos bancarios del mes (si están disponibles) vs ingresos facturados. Identifica depósitos > $15,000 MXN sin CFDI correspondiente (Art. 91 LISR discrepancia). Devuelve { depositos_sin_factura: [...], total }.`,
    { label: 'depositos-sin-factura', phase: 'Detección', schema: { type: 'object', properties: { depositos_sin_factura: { type: 'array' }, total: { type: 'number' } } } }
  ),
  ...(profundidad === 'completa' ? [
    () => agent(
      `Detecta duplicación de CFDIs (mismo UUID, mismo monto, mismo receptor) que pudieron haberse capturado o timbrado dos veces por error. Cubre los emitidos y recibidos. Devuelve { duplicados: [...] }.`,
      { label: 'duplicados', phase: 'Detección', schema: { type: 'object', properties: { duplicados: { type: 'array' } } } }
    ),
    () => agent(
      `Para CFDIs en moneda extranjera, valida que el TC usado esté dentro de ±2% del TC DOF correspondiente. Reporta los que se salgan (posible captura errónea).`,
      { label: 'tc-anomalos', phase: 'Detección', schema: { type: 'object', properties: { anomalos: { type: 'array' } } } }
    ),
  ] : []),
]

const detecciones = await parallel(tasks)

phase('Cuantificación')

const cuantificacion = await agent(
  `Cuantifica el impacto fiscal estimado de cada hallazgo en términos de:
   - ISR adicional que SAT podría determinar
   - Multas potenciales (Art. 81-83 CFF)
   - Recargos (1.47% mensual)
   - Riesgo de auditoría (bajo/medio/alto)

   Hallazgos: ${JSON.stringify(detecciones).slice(0, 2000)}

   Devuelve estimación total + ranking por impacto.`,
  { label: 'cuantificar', phase: 'Cuantificación', schema: { type: 'object', properties: { impacto_isr_estimado: { type: 'number' }, ranking: { type: 'array' }, riesgo_global: { type: 'string' } } } }
)

phase('Reporte')

const ruta = `auditorias/${rfc_cliente}/${ejercicio}-${String(mes).padStart(2, '0')}`
await agent(
  `Genera reporte ejecutivo en ${ruta}/auditoria-ejecutiva.md con:
   - Resumen del periodo (totales ingresos/gastos)
   - Hallazgos priorizados por riesgo
   - Acciones recomendadas con plazo (¿qué refacturar? ¿qué REP emitir?)
   - Impacto fiscal estimado total
   - Disclaimer "consultar al contador antes de aplicar"`,
  { label: 'reporte', phase: 'Reporte' }
)

return {
  rfc_cliente,
  ejercicio,
  mes,
  regimen,
  profundidad,
  cfdis_revisados: {
    emitidos: datos.total_emitidos,
    recibidos: datos.total_recibidos,
  },
  hallazgos: detecciones,
  cuantificacion,
  reporte: `${ruta}/auditoria-ejecutiva.md`,
}
