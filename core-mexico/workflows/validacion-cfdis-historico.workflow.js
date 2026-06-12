// Workflow ejecutable: validacion-cfdis-historico
//
// Batch reactivo: valida histórico de CFDIs del usuario para detectar problemas
// (cancelaciones SAT no reflejadas localmente, sustituciones, RFCs en 69-B
// que entraron a lista después de timbrar).
//
// args: { rfc_emisor, año, mes? (opcional — si no, todo el año) }

export const meta = {
  name: 'validacion-cfdis-historico',
  description: 'Validación batch de CFDIs históricos: status actual en SAT (vigente/cancelado), proveedores en 69-B post-timbrado, errores de captura, cancelaciones unilaterales del receptor. Útil tras auditoría o cierre anual.',
  whenToUse: 'Manual antes de declaración anual, o tras descubrir error y necesitar limpieza histórica.',
  phases: [
    { title: 'Inventario', detail: 'leer todos los CFDIs locales del periodo' },
    { title: 'Validación SAT', detail: 'pipeline: status uuid + lista 69-B emisor' },
    { title: 'Discrepancias', detail: 'cruzar status local vs SAT' },
    { title: 'Reporte', detail: 'detalles + acciones recomendadas' },
  ],
}

const { rfc_emisor, año, mes } = args || {}
if (!rfc_emisor || !año) {
  throw new Error('args requeridos: { rfc_emisor, año, mes? }')
}

log(`Validación histórica CFDIs ${rfc_emisor} | ${año}${mes ? `-${mes}` : ' (todo el año)'}`)

phase('Inventario')

const inventario = await agent(
  `Lee todos los CFDIs del directorio cfdi/${año}${mes ? `-${String(mes).padStart(2, '0')}` : ''}/ y devuelve array de { uuid, tipo, fecha, total, rfc_receptor, status_local, es_emitido }.`,
  { label: 'inventario', phase: 'Inventario', schema: { type: 'object', properties: { cfdis: { type: 'array' }, total: { type: 'number' } } } }
)

if (!inventario.cfdis || inventario.cfdis.length === 0) {
  return { status: 'sin_cfdis', año, mes }
}

log(`Inventario: ${inventario.cfdis.length} CFDIs a validar`)

phase('Validación SAT')

// pipeline: cada CFDI pasa por: verificar status SAT + verificar 69-B emisor (si recibido)
const resultados = await pipeline(
  inventario.cfdis,
  (cfdi) => agent(
    `Verifica status del UUID ${cfdi.uuid} en SAT via mp_sat_portal.verificar_cfdi_uuid. Devuelve { status_sat: "vigente"|"cancelado"|"no_encontrado", fecha_cancelacion, motivo }.`,
    { label: `sat-${cfdi.uuid.slice(0, 8)}`, phase: 'Validación SAT', schema: { type: 'object', properties: { status_sat: { type: 'string' }, fecha_cancelacion: { type: 'string' }, motivo: { type: 'string' } } } }
  ),
  // Si es CFDI recibido, validar también el RFC emisor en 69-B
  (statusSat, cfdi) => {
    if (cfdi.es_emitido) {
      return { cfdi, status_sat: statusSat, lista_69b: null }
    }
    return agent(
      `Verifica si RFC emisor ${cfdi.rfc_emisor || cfdi.rfc_receptor} está en lista 69-B (presunto o definitivo) HOY. Devuelve { en_69b: bool, estado, fecha_entrada }.`,
      { label: `69b-${cfdi.uuid.slice(0, 8)}`, phase: 'Validación SAT', schema: { type: 'object', properties: { en_69b: { type: 'boolean' }, estado: { type: 'string' } } } }
    ).then(lista => ({ cfdi, status_sat: statusSat, lista_69b: lista }))
  }
)

phase('Discrepancias')

const discrepancias = {
  cancelados_no_marcados: [],
  vigentes_marcados_cancelados: [],
  no_encontrados: [],
  emisores_69b_post_timbrado: [],
}

for (const r of resultados.filter(Boolean)) {
  const local = r.cfdi.status_local
  const sat = r.status_sat?.status_sat
  if (sat === 'cancelado' && local !== 'cancelado') {
    discrepancias.cancelados_no_marcados.push({ uuid: r.cfdi.uuid, fecha_cancelacion: r.status_sat.fecha_cancelacion, motivo: r.status_sat.motivo })
  }
  if (sat === 'vigente' && local === 'cancelado') {
    discrepancias.vigentes_marcados_cancelados.push({ uuid: r.cfdi.uuid })
  }
  if (sat === 'no_encontrado') {
    discrepancias.no_encontrados.push({ uuid: r.cfdi.uuid })
  }
  if (r.lista_69b?.en_69b) {
    discrepancias.emisores_69b_post_timbrado.push({ uuid: r.cfdi.uuid, rfc: r.cfdi.rfc_receptor, estado: r.lista_69b.estado })
  }
}

phase('Reporte')

const ruta = `validacion-historica/${año}${mes ? `-${String(mes).padStart(2, '0')}` : ''}`
await agent(
  `Genera reporte en ${ruta}/discrepancias.md con:
   - CFDIs cancelados en SAT pero NO marcados localmente: ${discrepancias.cancelados_no_marcados.length} — Actualizar status local
   - CFDIs vigentes en SAT pero marcados como cancelados localmente: ${discrepancias.vigentes_marcados_cancelados.length} — Revisar manualmente
   - UUIDs no encontrados en SAT: ${discrepancias.no_encontrados.length} — Posible UUID falso o portal en mantenimiento
   - Proveedores entraron a 69-B después de timbrar: ${discrepancias.emisores_69b_post_timbrado.length} — Si DEFINITIVO: excluir de deducibles
   Acciones recomendadas por cada caso.`,
  { label: 'reporte-md', phase: 'Reporte' }
)

return {
  rfc_emisor,
  año,
  mes,
  total_validados: inventario.cfdis.length,
  discrepancias_count: {
    cancelados_no_marcados: discrepancias.cancelados_no_marcados.length,
    vigentes_marcados_cancelados: discrepancias.vigentes_marcados_cancelados.length,
    no_encontrados: discrepancias.no_encontrados.length,
    emisores_69b_post_timbrado: discrepancias.emisores_69b_post_timbrado.length,
  },
  detalles: discrepancias,
  reporte: `${ruta}/discrepancias.md`,
}
