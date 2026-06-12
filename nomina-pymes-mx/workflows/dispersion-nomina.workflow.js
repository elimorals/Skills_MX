// Workflow ejecutable: dispersion-nomina
//
// Quincenal/semanal: para cada empleado activo, calcula percepciones y deducciones,
// timbra CFDI Nómina 4.0, genera lote SPEI Banxico para dispersar al banco del trabajador.
//
// args: { periodo: "2026-Q12", tipo: "ordinaria"|"extraordinaria"|"finiquito",
//         empresa_rfc, dry_run?: bool=true (default no toca banco) }

export const meta = {
  name: 'dispersion-nomina',
  description: 'Dispersión nómina quincenal/semanal: cálculo neto por empleado + IMSS/INFONAVIT/ISR + CFDI Nómina 4.0 + lote SPEI Banxico. Defaults dry_run=true porque toca dinero real.',
  whenToUse: 'Días 15 y 30 del mes (quincenal) o viernes (semanal en construcción). /nomina:dispersar.',
  phases: [
    { title: 'Validación empresa', detail: 'CSD vigente + e.firma + cuenta bancaria configurada' },
    { title: 'Cálculo empleados', detail: 'pipeline: cada empleado calcula percepciones + retenciones' },
    { title: 'Timbrado CFDIs', detail: 'parallel: 1 CFDI Nómina por empleado vía Facturama' },
    { title: 'Lote SPEI', detail: 'construir layout Banxico + checksum' },
    { title: 'Dispersión', detail: 'enviar lote a banco (REAL solo si dry_run=false)' },
    { title: 'Bitácora', detail: 'comprobantes por persona + reporte ejecutivo' },
  ],
}

const { periodo, tipo = 'ordinaria', empresa_rfc, dry_run = true } = args || {}
if (!periodo || !empresa_rfc) throw new Error('args requeridos: { periodo, empresa_rfc }')

log(`Dispersión nómina | ${empresa_rfc} | ${periodo} | tipo=${tipo} | dry_run=${dry_run}`)

phase('Validación empresa')

const validacion = await agent(
  `Valida pre-requisitos del patrón ${empresa_rfc} para dispersar nómina:
   1. CSD (Certificado Sello Digital) vigente
   2. e.firma vigente
   3. Cuenta bancaria origen configurada y con saldo suficiente
   4. CFDI Nómina anterior timbrado correctamente (continuidad)
   5. SUA / IDSE actualizados con últimas altas/bajas

   Devuelve { ok: bool, errores: [...], advertencias: [...] }`,
  { label: 'validar-empresa', phase: 'Validación empresa', schema: { type: 'object', properties: { ok: { type: 'boolean' }, errores: { type: 'array' }, advertencias: { type: 'array' } } } }
)

if (!validacion.ok) {
  return { status: 'pre_requisitos_faltantes', errores: validacion.errores }
}

phase('Cálculo empleados')

const empleados = await agent(
  `Lee empleados activos del patrón ${empresa_rfc} desde data/empleados.json.
   Para cada uno calcula percepciones + deducciones del periodo ${periodo} tipo ${tipo}:

   Percepciones:
   - Sueldo proporcional al periodo (quincenal = sueldo_mensual / 2)
   - Horas extras si hubo (cálculo Art. 67-68 LFT)
   - Bonos / comisiones / prima vacacional / aguinaldo proporcional
   - Subsidio al empleo (Art. 96 LISR para ingresos bajos)

   Deducciones:
   - ISR (tarifa Art. 96 mensualizada)
   - IMSS obrero (~2.375% del SBC)
   - INFONAVIT descuento (si tiene crédito activo, consultar EMIS)
   - Préstamos / otros descuentos

   Neto a pagar = Percepciones − Deducciones

   Devuelve array de empleados con desglose completo.`,
  { label: 'calcular-empleados', phase: 'Cálculo empleados', schema: { type: 'object', properties: { empleados: { type: 'array' }, total_neto: { type: 'number' }, total_isr: { type: 'number' }, total_imss: { type: 'number' } } } }
)

if (!empleados.empleados || empleados.empleados.length === 0) {
  return { status: 'sin_empleados', razon: 'No hay empleados activos' }
}

log(`${empleados.empleados.length} empleados | Total neto $${empleados.total_neto} | ISR $${empleados.total_isr}`)

phase('Timbrado CFDIs')

const cfdis = await parallel(
  empleados.empleados.map(emp => () => agent(
    `Timbra CFDI Nómina 4.0 vía mp_facturama_extendido.timbrar_con_nomina12 para ${emp.rfc}:
     - TipoComprobante: N
     - TipoNomina: O (ordinaria), E (extraordinaria), F (finiquito)
     - Receptor: ${emp.rfc} / ${emp.nombre}
     - Periodicidad pago: 02 (semanal), 04 (quincenal), 05 (mensual)
     - Percepciones detalladas + Deducciones detalladas
     - Subsidio al empleo si aplica
     - Total

     Devuelve { uuid, xml_b64, pdf_b64, rfc_empleado }`,
    { label: `cfdi-${emp.rfc?.slice(0, 8)}`, phase: 'Timbrado CFDIs', schema: { type: 'object', properties: { uuid: { type: 'string' }, rfc_empleado: { type: 'string' } } } }
  ))
)

const cfdisExitosos = cfdis.filter(c => c && c.uuid).length
log(`CFDIs timbrados: ${cfdisExitosos}/${empleados.empleados.length}`)

if (cfdisExitosos < empleados.empleados.length) {
  log(`⚠ ${empleados.empleados.length - cfdisExitosos} fallaron al timbrar — revisar antes de continuar`)
}

phase('Lote SPEI')

const lote = await agent(
  `Construye layout SPEI estándar Banxico H2H (Host-to-Host) o equivalente API del banco:
   - Cabecera: empresa_rfc, fecha_aplicacion, total registros, monto total
   - 1 línea por empleado: { CLABE_destino, monto_neto, concepto: "Nómina ${periodo}", referencia_numerica }
   - Pie con checksum

   Validar cada CLABE con mp_clabe_validador_oficial antes de incluirla en lote.
   Lista de empleados con monto: ${JSON.stringify(empleados.empleados.map(e => ({ rfc: e.rfc, clabe: e.clabe, neto: e.neto_a_pagar }))).slice(0, 1500)}

   Devuelve { lote_archivo: string, total_registros: number, total_monto: number, errores_clabe: [...] }`,
  { label: 'construir-lote', phase: 'Lote SPEI', schema: { type: 'object', properties: { lote_archivo: { type: 'string' }, total_registros: { type: 'number' }, total_monto: { type: 'number' }, errores_clabe: { type: 'array' } } } }
)

if (lote.errores_clabe?.length > 0) {
  log(`⚠ ${lote.errores_clabe.length} CLABEs inválidas — corregir antes de dispersar`)
  return {
    status: 'clabes_invalidas',
    errores: lote.errores_clabe,
    accion: 'Corregir CLABEs en data/empleados.json y reintentar',
  }
}

phase('Dispersión')

let dispersion = null
if (dry_run) {
  log(`🔵 DRY-RUN: lote construido pero NO enviado al banco. Archivo: ${lote.lote_archivo}`)
  dispersion = { ejecutada: false, modo: 'dry_run', archivo_listo: lote.lote_archivo }
} else {
  dispersion = await agent(
    `🚨 EJECUTAR dispersión real:
     1. Subir lote ${lote.lote_archivo} al portal/API del banco
     2. Confirmar autorización por usuario (segundo factor)
     3. Esperar confirmación SPEI emitido por cada empleado
     4. Capturar IDs de transacción Banxico de cada movimiento

     Devuelve { ejecutada: true, modo: "real", transacciones: [...] }`,
    { label: 'dispersar-real', phase: 'Dispersión', schema: { type: 'object', properties: { ejecutada: { type: 'boolean' }, transacciones: { type: 'array' } } } }
  )
}

phase('Bitácora')

const ruta = `nominas/${empresa_rfc}/${periodo}`
await agent(
  `Persiste bitácora completa en ${ruta}/:
   - dispersion.json: resumen + dry_run/real
   - lote-spei.txt: archivo H2H
   - cfdis/<rfc>.xml y .pdf por empleado
   - comprobantes-spei.json (si !dry_run)
   - reporte-ejecutivo.md con total + alertas`,
  { label: 'bitacora', phase: 'Bitácora' }
)

return {
  empresa_rfc,
  periodo,
  tipo,
  empleados_procesados: empleados.empleados.length,
  cfdis_timbrados: cfdisExitosos,
  total_neto_dispersado: lote.total_monto,
  total_isr_retenido: empleados.total_isr,
  total_imss_obrero: empleados.total_imss,
  dry_run,
  dispersion,
  ruta_bitacora: ruta,
}
