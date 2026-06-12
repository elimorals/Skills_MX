// Workflow ejecutable: monitoreo-diario-vehicular
//
// Cron diario 08:00: para cada auto del usuario, revisa multas nuevas + tenencia
// + refrendo + verificación próxima + hoy-no-circula.
//
// args: { autos: [{placas, estado, no_circula_dia?}] }

export const meta = {
  name: 'monitoreo-diario-vehicular',
  description: 'Monitoreo diario de multas/tenencia/refrendo/verificación/hoy-no-circula por cada auto del usuario. Cron-driven.',
  whenToUse: 'Cron 0 8 * * * (diario 08:00).',
  phases: [
    { title: 'Por auto', detail: 'pipeline: cada auto pasa por checks paralelos' },
    { title: 'Consolidación', detail: 'agrupar alertas por urgencia' },
    { title: 'Notificación', detail: 'WhatsApp con alertas accionables' },
  ],
}

const { autos } = args || {}
if (!autos || !autos.length) throw new Error('args.autos requerido (array)')

log(`Monitoreo vehicular: ${autos.length} auto(s)`)

phase('Por auto')

const resultados = await pipeline(
  autos,
  (auto) =>
    parallel([
      () => agent(
        `Consulta multas nuevas del auto ${auto.placas} en ${auto.estado} via mp_${auto.estado.toLowerCase()}_municipal o equivalente. Devuelve { multas_nuevas: [...], monto_total }.`,
        { label: `multas-${auto.placas}`, phase: 'Por auto', schema: { type: 'object', properties: { multas_nuevas: { type: 'array' }, monto_total: { type: 'number' } } } }
      ),
      () => agent(
        `Consulta status de tenencia/refrendo del auto ${auto.placas} en ${auto.estado}. Devuelve { tenencia_pendiente: bool, vence: string, refrendo_pendiente: bool }.`,
        { label: `tenencia-${auto.placas}`, phase: 'Por auto', schema: { type: 'object', properties: { tenencia_pendiente: { type: 'boolean' }, vence: { type: 'string' }, refrendo_pendiente: { type: 'boolean' } } } }
      ),
      () => agent(
        `Consulta calendario de verificación vehicular del auto ${auto.placas} según engomado. Devuelve { proxima_verificacion: string, dias_restantes: number }.`,
        { label: `verifica-${auto.placas}`, phase: 'Por auto', schema: { type: 'object', properties: { proxima_verificacion: { type: 'string' }, dias_restantes: { type: 'number' } } } }
      ),
      () => agent(
        `Calcula si el auto ${auto.placas} no_circula HOY según día semana + último dígito placa. Devuelve { no_circula_hoy: bool, razon: string }.`,
        { label: `hnc-${auto.placas}`, phase: 'Por auto', schema: { type: 'object', properties: { no_circula_hoy: { type: 'boolean' }, razon: { type: 'string' } } } }
      ),
    ]).then(([multas, tenencia, verifica, hnc]) => ({ auto, multas, tenencia, verifica, hnc }))
)

phase('Consolidación')

const alertas = {
  criticas: [],
  altas: [],
  medias: [],
  informativas: [],
}

for (const r of resultados.filter(Boolean)) {
  if (r.multas?.monto_total > 0) {
    alertas.altas.push(`${r.auto.placas}: ${r.multas.multas_nuevas?.length || 0} multas nuevas, total $${r.multas.monto_total}`)
  }
  if (r.tenencia?.tenencia_pendiente) {
    const dias = Math.ceil((new Date(r.tenencia.vence) - new Date()) / (1000 * 60 * 60 * 24))
    if (dias < 7) alertas.criticas.push(`${r.auto.placas}: tenencia vence en ${dias} días`)
    else if (dias < 30) alertas.altas.push(`${r.auto.placas}: tenencia vence en ${dias} días`)
  }
  if (r.verifica?.dias_restantes < 14) {
    alertas.altas.push(`${r.auto.placas}: verificación próxima en ${r.verifica.dias_restantes} días`)
  }
  if (r.hnc?.no_circula_hoy) {
    alertas.informativas.push(`${r.auto.placas}: HOY NO CIRCULA — ${r.hnc.razon}`)
  }
}

phase('Notificación')

if (alertas.criticas.length || alertas.altas.length) {
  await agent(
    `Envía resumen via WhatsApp al usuario con alertas vehiculares:
     - CRÍTICAS: ${alertas.criticas.join(' | ')}
     - ALTAS: ${alertas.altas.join(' | ')}
     - INFO: ${alertas.informativas.join(' | ')}
     Template "utility_alertas_vehiculares".`,
    { label: 'notificar-wa', phase: 'Notificación' }
  )
}

return {
  fecha: new Date().toISOString().slice(0, 10),
  total_autos: autos.length,
  alertas,
  detalle: resultados,
}
