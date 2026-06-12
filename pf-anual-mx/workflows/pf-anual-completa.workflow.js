// Workflow ejecutable: pf-anual-completa
//
// Convierte el markdown declarativo `pf-anual-mx/agents/workflow-pf-anual-completa.md`
// a un script ejecutable del skill `Workflow`.
//
// Invocar con: Workflow({scriptPath: "pf-anual-mx/workflows/pf-anual-completa.workflow.js", args: {...}})
//
// Inputs en `args`:
//   { rfc: string, ejercicio: number, regimen: "PFAE_612"|"RESICO_PF_626"|"ASALARIADO_HONORARIOS_605",
//     incluir_bancos?: boolean }
//
// Flujo secuencial (8 fases) — cada fase depende de la previa.

export const meta = {
  name: 'pf-anual-completa',
  description: 'Declaración anual PF end-to-end: e.firma + CFDIs + deducciones + cruce bancos + ISR + borrador + tracker. Genera PDF presentable y advertencias críticas (depósitos sin facturar >$15k, RFCs 69-B, saldo a favor anómalo). Marca vigencia_validada=false hasta validación de contador.',
  whenToUse: 'Marzo-abril (temporada anual) o auditoría retroactiva. Tu propia declaración personal antes de marzo 2027.',
  phases: [
    { title: 'Validación', detail: 'régimen + e.firma vigente' },
    { title: 'CFDIs', detail: 'descarga anual emitidos + recibidos del SAT' },
    { title: 'Deducciones', detail: 'clasificar CFDIs deducibles personales Art. 151' },
    { title: 'Bancos', detail: 'cruzar depósitos vs CFDIs emitidos (opcional)' },
    { title: 'ISR', detail: 'calculadora ISR anual + comparar pagos provisionales' },
    { title: 'Riesgo', detail: 'alertas críticas (auditoría, 69-B, discrepancias)' },
    { title: 'Borrador', detail: 'generar PDF presentable + path' },
    { title: 'Tracker', detail: 'persistir resultado + recomendaciones finales' },
  ],
}

const { rfc, ejercicio, regimen, incluir_bancos = true } = args || {}

if (!rfc || !ejercicio || !regimen) {
  throw new Error('args requeridos: { rfc, ejercicio, regimen }')
}

if (!['PFAE_612', 'RESICO_PF_626', 'ASALARIADO_HONORARIOS_605'].includes(regimen)) {
  throw new Error(`régimen inválido: ${regimen}`)
}

log(`Anual PF — RFC ${rfc} — ejercicio ${ejercicio} — régimen ${regimen}`)

// ============================================================
// FASE 0: Validación inicial (e.firma vigente)
// ============================================================
phase('Validación')

const validacion = await agent(
  `Verifica que la e.firma del RFC ${rfc} esté vigente usando mp_sat_portal.verificar_efirma_vigente.
   Devuelve { vigente: bool, dias_para_vencer: number, vigencia_hasta: string }.
   Si dias_para_vencer < 30: incluir warning pero continuar.
   Si !vigente: NO continuar.`,
  { label: 'efirma-check', phase: 'Validación', schema: efirmaSchema() }
)

if (!validacion.vigente) {
  return {
    status: 'abortado',
    razon: 'e.firma vencida',
    detalle: validacion,
    accion_humana: 'Renovar e.firma en oficina SAT con cita previa antes de continuar.',
  }
}

const efirmaWarning = validacion.dias_para_vencer < 30
  ? `⚠ e.firma vence en ${validacion.dias_para_vencer} días — renovar pronto.`
  : null

// ============================================================
// FASE 1: Recopilación de CFDIs anuales
// ============================================================
phase('CFDIs')

const cfdis = await agent(
  `Recopila TODOS los CFDIs emitidos y recibidos del RFC ${rfc} para el ejercicio ${ejercicio}.
   Usa el skill recopilar-cfdis-anuales (pf-anual-mx/skills/recopilar-cfdis-anuales).
   Internamente invoca mp_sat_portal.descargar_cfdi_masivo 2 veces (emitidos + recibidos).

   Devuelve:
   {
     total_cfdis_emitidos, total_cfdis_recibidos,
     ingresos_totales_mxn, ingresos_cobrados_mxn (base flujo),
     gastos_totales_mxn, gastos_pagados_mxn,
     monedas_extranjeras: [{moneda, cantidad}],
     cfdis_cancelados: number,
     cfdis_con_pago_pendiente_rep: number
   }

   Si SAT regresa pending (async): retornar {pending: true} y workflow se aborta para retry.`,
  { label: 'recopilacion-cfdis', phase: 'CFDIs', schema: cfdisAnualesSchema() }
)

if (cfdis.pending) {
  return {
    status: 'pendiente_sat',
    razon: 'descarga masiva CFDIs aún procesando (1-4 hrs típico)',
    siguiente_intento: 'cron retry en 2 hrs',
  }
}

if (cfdis.total_cfdis_emitidos === 0 && cfdis.total_cfdis_recibidos === 0) {
  log(`⚠ Ejercicio ${ejercicio} sin CFDIs — declaración en ceros pero presentar de todos modos.`)
}

// ============================================================
// FASE 2: Identificación de deducciones personales
// ============================================================
phase('Deducciones')

const deducciones = await agent(
  `Clasifica los CFDIs recibidos (${cfdis.total_cfdis_recibidos} comprobantes) en categorías deducibles personales del Art. 151 LISR:
   - D01 honorarios médicos/dentales/hospitalarios
   - D02 gastos funerarios
   - D03 donativos
   - D04 intereses hipotecarios reales casa-habitación
   - D05 aportaciones voluntarias SAR/AFORE
   - D06 primas seguros gastos médicos
   - D07 transporte escolar obligatorio
   - D08 decreto colegiaturas (por nivel educativo)
   - D09 depósitos cuentas especiales ahorro

   Aplica topes vigentes (validar contra brief-contador-2026):
   - Tope global: 5 UMA anual O 15% ingresos acumulables (lo menor)
   - Donativos: 7% ingresos previos
   - SAR/AFORE: 10% ingresos, máx 5 UMA anual
   - Colegiaturas por nivel: preescolar $14,200 / primaria $12,900 / secundaria $19,900 / etc.

   Devuelve:
   {
     deducciones_personales_totales_mxn,
     por_categoria: {D01: monto, D02: monto, ...},
     tope_global_aplicado_mxn,
     monto_que_excedio_tope_mxn,
     advertencias_topes: [string]
   }`,
  { label: 'deducciones-personales', phase: 'Deducciones', schema: deduccionesSchema() }
)

// ============================================================
// FASE 3: Cruce bancos vs CFDIs (opcional)
// ============================================================
phase('Bancos')

let cruceBancos = null
if (incluir_bancos) {
  cruceBancos = await agent(
    `Cruza depósitos bancarios del ejercicio ${ejercicio} vs CFDIs emitidos.
     Identifica:
     - depositos_sin_factura_mxn (potencial ingreso no facturado)
     - depositos_efectivo_mayores_15k (Art. 91 LISR — discrepancia)
     - cfdis_sin_cobro (cartera del ejercicio)
     - riesgo_discrepancia: "bajo"|"medio"|"alto"|"no_evaluado"

     Si no hay extractos bancarios cargados: devuelve { riesgo_discrepancia: "no_evaluado" }.`,
    { label: 'cruce-bancos', phase: 'Bancos', schema: cruceBancosSchema() }
  )
} else {
  cruceBancos = { riesgo_discrepancia: 'no_evaluado', razon: 'incluir_bancos=false' }
}

// ============================================================
// FASE 4: Cálculo ISR anual + comparativa con pagos provisionales
// ============================================================
phase('ISR')

const isr = await agent(
  `Usando el skill calculadora-isr-anual (pf-anual-mx/skills/calculadora-isr-anual), calcula:

   Inputs:
   - Régimen: ${regimen}
   - Ingresos acumulables: $${cfdis.ingresos_cobrados_mxn || cfdis.ingresos_totales_mxn}
   - Gastos deducibles ejercicio: $${cfdis.gastos_pagados_mxn}
   - Deducciones personales: $${deducciones.deducciones_personales_totales_mxn}
   - Pagos provisionales del ejercicio: obtener del tracker fiscal/<rfc_hash>/<ejercicio>/ (suma de cierre-fiscal-mensual)
   - Retenciones del ejercicio: obtener del tracker

   Aplica tarifa anual Art. 152 LISR para PFAE / tasa única para RESICO.

   Devuelve:
   {
     isr_anual_causado_mxn,
     pagos_provisionales_acumulados_mxn,
     retenciones_acumuladas_mxn,
     diferencia_mxn,
     resultado: "SALDO_A_PAGAR"|"SALDO_A_FAVOR"|"EXACTO",
     tarifa_aplicada: { rango_li, rango_ls, cuota_fija, porcentaje },
     vigencia_validada: bool
   }`,
  { label: 'calculo-isr-anual', phase: 'ISR', schema: isrAnualSchema() }
)

// ============================================================
// FASE 5: Análisis de riesgo
// ============================================================
phase('Riesgo')

const alertas_criticas = []

if (isr.resultado === 'SALDO_A_FAVOR') {
  if (isr.diferencia_mxn > 100000) {
    alertas_criticas.push({
      tipo: 'saldo_a_favor_muy_alto',
      severidad: 'critica',
      detalle: `Saldo a favor de $${isr.diferencia_mxn} — alta probabilidad de auditoría SAT antes de devolución.`,
    })
  } else if (isr.diferencia_mxn > 50000) {
    alertas_criticas.push({
      tipo: 'saldo_a_favor_alto',
      severidad: 'alta',
      detalle: `Saldo a favor de $${isr.diferencia_mxn} — preparar documentación soporte para validación SAT.`,
    })
  }
}

if (cruceBancos?.depositos_efectivo_mayores_15k > 0) {
  alertas_criticas.push({
    tipo: 'discrepancia_efectivo',
    severidad: 'alta',
    detalle: `$${cruceBancos.depositos_efectivo_mayores_15k} en depósitos efectivo > $15k/mes (Art. 91 LISR).`,
  })
}

const verificacion69b = await agent(
  `Para los CFDIs recibidos del ejercicio, identifica cuáles tienen RFC emisor en la lista 69-B DEFINITIVO del SAT.
   Sus gastos NO son deducibles. Reporta monto total a EXCLUIR de gastos deducibles.`,
  { label: 'verificacion-69b', phase: 'Riesgo', schema: alerta69bSchema() }
)

if (verificacion69b.monto_a_excluir > 0) {
  alertas_criticas.push({
    tipo: 'cfdis_69b_definitivo',
    severidad: 'critica',
    detalle: `$${verificacion69b.monto_a_excluir} en CFDIs de RFCs en lista 69-B definitiva — EXCLUIR de gastos deducibles.`,
  })
}

// ============================================================
// FASE 6: Generación del borrador
// ============================================================
phase('Borrador')

const borrador = await agent(
  `Usando el skill generar-borrador-declaracion (pf-anual-mx/skills/generar-borrador-declaracion), genera un PDF presentable con:
   - Encabezado: RFC, ejercicio, régimen, fecha generación
   - Sección 1: Ingresos del ejercicio (con desglose por mes)
   - Sección 2: Gastos deducibles (Art. 25 LISR para PFAE)
   - Sección 3: Deducciones personales (Art. 151 LISR) con topes aplicados
   - Sección 4: Cálculo ISR (tarifa aplicada + cuotas)
   - Sección 5: Comparativa pagos provisionales acumulados
   - Sección 6: Resultado (saldo a favor o pagar)
   - Sección 7: Alertas + recomendaciones
   - Footer: vigencia_validada + disclaimer "presentar tras validar con contador certificado"

   Devuelve { pdf_path: string, paginas: number }.`,
  { label: 'borrador-pdf', phase: 'Borrador', schema: borradorSchema() }
)

// ============================================================
// FASE 7: Tracker + recomendaciones finales
// ============================================================
phase('Tracker')

const recomendaciones = [
  `📋 Llevar PDF a contador certificado antes del 25 de abril ${ejercicio + 1}.`,
  isr.resultado === 'SALDO_A_FAVOR'
    ? `💰 Configurar CLABE de cobro en DeclaraSAT para solicitar devolución de $${isr.diferencia_mxn}.`
    : `💳 Saldo a pagar: $${isr.diferencia_mxn}. Si > $50k, evaluar pago en parcialidades (RMF Art. 66).`,
  alertas_criticas.length > 0
    ? `⚠ Resolver ${alertas_criticas.length} alertas críticas ANTES de presentar.`
    : `✅ Sin alertas críticas detectadas.`,
  `📅 Próxima sesión sugerida: /pf-anual:status-devolucion en mayo ${ejercicio + 1}.`,
]

if (efirmaWarning) recomendaciones.unshift(efirmaWarning)

await agent(
  `Persiste el resultado en ~/.local/share/plugins-mx/pf-anual/<rfc_hash>/${ejercicio}/resultado.json con timestamp + workflow_run_id + hash de PDF.`,
  { label: 'tracker-persist', phase: 'Tracker' }
)

return {
  workflow: 'pf-anual-completa',
  rfc_hash: '<hash>', // computado por skill
  ejercicio,
  regimen,
  fases_completadas: ['Validación', 'CFDIs', 'Deducciones', 'Bancos', 'ISR', 'Riesgo', 'Borrador', 'Tracker'],
  isr_causado_mxn: isr.isr_anual_causado_mxn,
  pagos_provisionales_mxn: isr.pagos_provisionales_acumulados_mxn,
  diferencia_mxn: isr.diferencia_mxn,
  resultado: isr.resultado,
  pdf_borrador_path: borrador.pdf_path,
  alertas_criticas,
  recomendaciones,
  vigencia_validada: isr.vigencia_validada === true,
  efirma_warning: efirmaWarning,
}

// ============================================================
// Schemas
// ============================================================
function efirmaSchema() {
  return {
    type: 'object',
    required: ['vigente'],
    properties: {
      vigente: { type: 'boolean' },
      dias_para_vencer: { type: 'number' },
      vigencia_hasta: { type: 'string' },
      rfc: { type: 'string' },
    },
  }
}

function cfdisAnualesSchema() {
  return {
    type: 'object',
    properties: {
      total_cfdis_emitidos: { type: 'number' },
      total_cfdis_recibidos: { type: 'number' },
      ingresos_totales_mxn: { type: 'number' },
      ingresos_cobrados_mxn: { type: 'number' },
      gastos_totales_mxn: { type: 'number' },
      gastos_pagados_mxn: { type: 'number' },
      cfdis_cancelados: { type: 'number' },
      cfdis_con_pago_pendiente_rep: { type: 'number' },
      pending: { type: 'boolean' },
    },
  }
}

function deduccionesSchema() {
  return {
    type: 'object',
    required: ['deducciones_personales_totales_mxn', 'por_categoria'],
    properties: {
      deducciones_personales_totales_mxn: { type: 'number' },
      por_categoria: { type: 'object' },
      tope_global_aplicado_mxn: { type: 'number' },
      monto_que_excedio_tope_mxn: { type: 'number' },
      advertencias_topes: { type: 'array', items: { type: 'string' } },
    },
  }
}

function cruceBancosSchema() {
  return {
    type: 'object',
    properties: {
      depositos_sin_factura_mxn: { type: 'number' },
      depositos_efectivo_mayores_15k: { type: 'number' },
      cfdis_sin_cobro_mxn: { type: 'number' },
      riesgo_discrepancia: { enum: ['bajo', 'medio', 'alto', 'no_evaluado'] },
      razon: { type: 'string' },
    },
  }
}

function isrAnualSchema() {
  return {
    type: 'object',
    required: ['isr_anual_causado_mxn', 'diferencia_mxn', 'resultado'],
    properties: {
      isr_anual_causado_mxn: { type: 'number' },
      pagos_provisionales_acumulados_mxn: { type: 'number' },
      retenciones_acumuladas_mxn: { type: 'number' },
      diferencia_mxn: { type: 'number' },
      resultado: { enum: ['SALDO_A_PAGAR', 'SALDO_A_FAVOR', 'EXACTO'] },
      tarifa_aplicada: { type: 'object' },
      vigencia_validada: { type: 'boolean' },
    },
  }
}

function alerta69bSchema() {
  return {
    type: 'object',
    properties: {
      rfcs_en_69b_definitivo: { type: 'array', items: { type: 'string' } },
      cantidad_cfdis: { type: 'number' },
      monto_a_excluir: { type: 'number' },
    },
  }
}

function borradorSchema() {
  return {
    type: 'object',
    required: ['pdf_path'],
    properties: {
      pdf_path: { type: 'string' },
      paginas: { type: 'number' },
    },
  }
}
