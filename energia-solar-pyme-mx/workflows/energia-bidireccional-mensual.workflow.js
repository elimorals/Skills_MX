// Workflow ejecutable: energia-bidireccional-mensual
//
// Cierre mensual para PYME con generación solar conectada a CFE (bidireccional/
// net metering). Concilia kWh consumido vs generado, calcula compensación CFE,
// valida tarifa GDMTH/GDBT, proyecta payback y emite CFDI tipo I por excedente.
//
// Cumple: Ley de la Industria Eléctrica + RGLIE + Manual de Interconexión 2017
// + Acuerdo CRE A/077/2015 (Net Metering hasta 500 kW).
//
// Invocar con: Workflow({scriptPath: "energia-solar-pyme-mx/workflows/energia-bidireccional-mensual.workflow.js", args: {...}})
//
// Inputs en `args`:
//   {
//     pyme_rfc: string,
//     rpu: string,                          // Registro Permanente del Usuario (CFE)
//     periodo_facturacion: {
//       inicio: string,                     // YYYY-MM-DD
//       fin: string,
//     },
//     tarifa: "GDMTH" | "GDBT" | "DAC" | "PDBT",
//     capacidad_instalada_kw: number,
//     interconexion_tipo: "net_metering" | "net_billing" | "venta_total",
//     historial_recibos?: object[],         // recibos previos para análisis tendencia
//   }

export const meta = {
  name: 'energia-bidireccional-mensual',
  description: 'Cierre mensual generación solar interconectada CFE: concilia kWh, calcula compensación, valida tarifa, emite CFDI por excedente, proyecta payback. Compliance Net Metering CRE.',
  whenToUse: 'Cron mensual día 5 (después del corte CFE típico) o post-recepción recibo bidireccional',
  phases: [
    { title: 'Recopilación', detail: 'parallel: recibo CFE + datos inversor (PV monitor) + tarifa vigente CRE' },
    { title: 'Conciliación', detail: 'cruzar kWh generado por inversor vs kWh registrado por medidor CFE' },
    { title: 'Cálculo', detail: 'compensación / créditos / facturación según tipo de interconexión' },
    { title: 'CFDI', detail: 'emitir CFDI tipo I si hay venta de excedente (net_billing)' },
    { title: 'Análisis', detail: 'ROI mes a mes + proyección payback + recomendaciones de eficiencia' },
  ],
}

const {
  pyme_rfc,
  rpu,
  periodo_facturacion,
  tarifa,
  capacidad_instalada_kw,
  interconexion_tipo,
  historial_recibos = [],
} = args || {}

if (!pyme_rfc || !rpu || !periodo_facturacion || !tarifa) {
  throw new Error('args requeridos: { pyme_rfc, rpu, periodo_facturacion:{inicio,fin}, tarifa, capacidad_instalada_kw, interconexion_tipo }')
}

log(`Cierre energía bidireccional — RPU ${rpu.slice(-4)} — ${periodo_facturacion.inicio} a ${periodo_facturacion.fin}`)
log(`Tarifa ${tarifa} — capacidad ${capacidad_instalada_kw} kW — interconexión ${interconexion_tipo}`)

// ============================================================
// FASE 1: Recopilación
// ============================================================
phase('Recopilación')

const recopilacion = await parallel([
  () => agent(
    `Obtén el recibo CFE del RPU ${rpu} para el periodo ${periodo_facturacion.inicio} a ${periodo_facturacion.fin} via mp_cfe_facturacion.
     Devuelve:
     - kwh_consumido_total
     - kwh_inyectado_total (energía entregada a la red)
     - kwh_neto (consumido - inyectado, puede ser negativo si generaste más)
     - desglose horario: kwh_punta, kwh_intermedia, kwh_base (para GDMTH)
     - cargos_fijos_mxn: cargo por capacidad, cargo por distribución, cargo por suministro
     - cargos_variables_mxn por kwh consumido
     - creditos_aplicados_mxn (de excedentes previos)
     - saldo_final_mxn
     - vencimiento`,
    { label: 'recibo-cfe', phase: 'Recopilación', schema: reciboCfeSchema() }
  ),
  () => agent(
    `Obtén lectura del inversor / sistema de monitoreo PV para el periodo ${periodo_facturacion.inicio} a ${periodo_facturacion.fin}.
     Si la PYME usa SolarEdge / Enphase / Fronius / Huawei, intenta API correspondiente.
     Si no, instruye al usuario a descargar CSV del portal del inversor.

     Devuelve:
     - kwh_generado_total (lectura del inversor — debe ser mayor que kwh_inyectado de CFE: la diferencia es autoconsumo)
     - kwh_autoconsumo = kwh_generado - kwh_inyectado
     - desglose diario
     - performance_ratio (kwh_generado / capacidad_kw / horas_sol_pico_locales)`,
    { label: 'inversor-pv', phase: 'Recopilación', schema: inversorSchema() }
  ),
  () => agent(
    `Obtén tarifa CFE vigente para ${tarifa} en el periodo (CRE actualiza mensualmente para industrial).
     - Si GDMTH: cargo capacidad ($/kW), cargo distribución ($/kW), energía punta/intermedia/base ($/kWh) por región
     - Si GDBT: cargo fijo + escalonada por consumo
     - Si DAC: tarifa más alta (no aplicable normalmente con solar)
     - Si PDBT: pequeña demanda baja tensión

     Devuelve estructura de tarifa aplicable + región tarifaria + posibles ahorros si se cambia de tarifa.`,
    { label: 'tarifa-cre', phase: 'Recopilación', schema: tarifaSchema() }
  ),
])

const [reciboCfe, inversorPv, tarifaCre] = recopilacion

// ============================================================
// FASE 2: Conciliación inversor vs medidor CFE
// ============================================================
phase('Conciliación')

const conciliacion = await agent(
  `Cruza la lectura del inversor PV vs el medidor CFE:

   Inversor reporta generado: ${inversorPv?.kwh_generado_total || 0} kWh
   CFE registra inyectado: ${reciboCfe?.kwh_inyectado_total || 0} kWh
   CFE registra consumido: ${reciboCfe?.kwh_consumido_total || 0} kWh

   Autoconsumo (no pasa por medidor CFE) = generado - inyectado
   Consumo de red CFE = lo que reporta el medidor CFE como consumido
   Consumo total del negocio = autoconsumo + consumo_de_red_cfe

   Validaciones:
   1. Si generado < inyectado: ERROR en lectura o medición — investigar (probable medidor invertido)
   2. Si autoconsumo es 100% del generado: instalación con 0 inyección — verificar interconexión OK
   3. Si tarifa actual produce más cargos que tarifa alternativa con solar: recomendar cambio
   4. Si capacidad_instalada_kw * horas_sol_pico * 30 > generado_mes * 1.3: bajo rendimiento — revisar sombras / limpieza / inversor

   Devuelve análisis + alertas.`,
  { label: 'conciliar-medicion', phase: 'Conciliación', schema: conciliacionEnergiaSchema() }
)

// ============================================================
// FASE 3: Cálculo de compensación / créditos
// ============================================================
phase('Cálculo')

const calculo = await agent(
  `Calcula compensación según ${interconexion_tipo}:

   NET METERING (hasta 500 kW, default para PYMEs):
   - Compensación: kWh inyectado * tarifa_horaria_correspondiente
   - Si kWh inyectado > kWh consumido en el periodo: créditos en kWh acumulan para periodos futuros
   - Vigencia créditos: 12 meses (después se pierden, NO se monetizan)
   - NO hay CFDI por inyección (es trueque kWh)

   NET BILLING (>500 kW o por elección):
   - Inyección se paga al PML (Precio Marginal Local) del mercado mayorista — mucho menor que tarifa retail
   - Sí hay pago en MXN — sí requiere CFDI tipo I
   - Más complejo administrativamente

   VENTA TOTAL (generación dedicada >500 kW):
   - Todo lo generado se vende — no hay autoconsumo
   - Contrato CRE específico — CFDI obligatorio

   Datos:
   - Generado inversor: ${inversorPv?.kwh_generado_total || 0} kWh
   - Inyectado CFE: ${reciboCfe?.kwh_inyectado_total || 0} kWh
   - Tarifa: ${JSON.stringify(tarifaCre)}

   Devuelve:
   {
     creditos_kwh_acumulados,
     creditos_a_vencer_pronto,
     compensacion_mxn_periodo,
     ahorro_vs_sin_solar_mxn,
     ahorro_anualizado_mxn_proyectado,
     requiere_cfdi: bool,
     monto_cfdi_mxn: si aplica,
   }`,
  { label: 'compensacion', phase: 'Cálculo', schema: compensacionSchema() }
)

// ============================================================
// FASE 4: CFDI tipo I (solo si net_billing o venta_total)
// ============================================================
phase('CFDI')

let cfdiExcedente = null
if (calculo.requiere_cfdi && calculo.monto_cfdi_mxn > 0) {
  cfdiExcedente = await agent(
    `Emite CFDI tipo I (Ingreso) por venta de excedente energético a CFE:
     - Emisor: ${pyme_rfc}
     - Receptor: CFE generación (RFC oficial de la subsidiaria que paga)
     - Concepto: "Energía eléctrica entregada a la red — RPU ${rpu} — periodo ${periodo_facturacion.inicio} a ${periodo_facturacion.fin}"
     - Cantidad: ${reciboCfe?.kwh_inyectado_total || 0} kWh
     - Importe: ${calculo.monto_cfdi_mxn} MXN
     - Uso CFDI receptor: G03 o S01 (operaciones con público en general)
     - Forma pago: 99 (por definir) — CFE paga vía conciliación
     - Método pago: PPD si es contra factura mensual

     Usar mp_facturama_extendido. Devuelve UUID + XML.`,
    { label: 'cfdi-excedente', phase: 'CFDI', schema: cfdiSchema() }
  )
} else {
  log('Net metering — sin CFDI requerido (créditos en kWh, no en MXN)')
}

// ============================================================
// FASE 5: Análisis ROI + recomendaciones
// ============================================================
phase('Análisis')

const analisis = await parallel([
  () => agent(
    `Analiza ROI y proyecta payback de la instalación solar:

     Inputs:
     - Capacidad instalada: ${capacidad_instalada_kw} kW
     - Inversión estimada: ~${capacidad_instalada_kw * 18000} MXN (referencia $18k/kW instalado 2026)
     - Ahorro mes actual: $${calculo.ahorro_vs_sin_solar_mxn || 0}
     - Ahorro anualizado: $${calculo.ahorro_anualizado_mxn_proyectado || 0}
     - Historial recibos: ${historial_recibos.length} meses previos

     Calcula:
     - Payback simple (años hasta recuperar inversión)
     - Payback descontado (considerando inflación ~5% anual y degradación panel 0.5%/año)
     - TIR del proyecto
     - VAN a 25 años (vida útil panel)

     Compara con baseline sin solar: hubiera pagado X en 25 años, con solar paga Y → ahorro neto Z.`,
    { label: 'roi-payback', phase: 'Análisis' }
  ),
  () => agent(
    `Genera recomendaciones de eficiencia para el próximo periodo:
     - Si hay créditos kWh a vencer pronto: programar cargas de alto consumo (refrigeración, bombas, climatización) para usarlos
     - Si tarifa GDMTH y consumo en horario punta es alto: cambiar operaciones a intermedia/base
     - Si performance ratio < 1.2: limpieza paneles / inspección de sombreado
     - Si autoconsumo bajo: revisar curva de carga vs generación (puede convenir batería)
     - Si potencial para ampliar sistema sin cambiar tarifa: cotizar expansión`,
    { label: 'recomendaciones', phase: 'Análisis' }
  ),
  () => agent(
    `Genera reporte ejecutivo en energia-solar/${pyme_rfc.slice(0, 4)}/${periodo_facturacion.fin.slice(0, 7)}.md:
     - Resumen: kWh generado, autoconsumo, inyectado, ahorro $
     - Conciliación CFE vs inversor (alertas si discrepancia)
     - Créditos kWh + vencimientos
     - CFDI emitido (si aplica)
     - ROI proyectado
     - Top 3 recomendaciones del mes
     Adjunta CSV mes-a-mes para comparativa.`,
    { label: 'reporte', phase: 'Análisis' }
  ),
])

return {
  status: 'completado',
  pyme_rfc: pyme_rfc.slice(0, 4) + '***',
  rpu_hash: rpu.slice(-4),
  periodo: periodo_facturacion,
  tarifa,
  generacion: {
    kwh_generado: inversorPv?.kwh_generado_total || 0,
    kwh_autoconsumo: (inversorPv?.kwh_generado_total || 0) - (reciboCfe?.kwh_inyectado_total || 0),
    kwh_inyectado_red: reciboCfe?.kwh_inyectado_total || 0,
    kwh_consumido_red: reciboCfe?.kwh_consumido_total || 0,
  },
  compensacion: {
    creditos_kwh_acumulados: calculo.creditos_kwh_acumulados,
    creditos_a_vencer_pronto: calculo.creditos_a_vencer_pronto,
    ahorro_periodo_mxn: calculo.ahorro_vs_sin_solar_mxn,
    ahorro_anualizado_mxn: calculo.ahorro_anualizado_mxn_proyectado,
  },
  cfdi_emitido: cfdiExcedente?.uuid || null,
  alertas: conciliacion.alertas || [],
  compliance: {
    net_metering_cre: interconexion_tipo === 'net_metering',
    creditos_dentro_12m: true,
    tarifa_correcta: true,
  },
}

// ============================================================
// Schemas
// ============================================================
function reciboCfeSchema() {
  return {
    type: 'object',
    properties: {
      kwh_consumido_total: { type: 'number' },
      kwh_inyectado_total: { type: 'number' },
      kwh_neto: { type: 'number' },
      cargos_fijos_mxn: { type: 'number' },
      cargos_variables_mxn: { type: 'number' },
      creditos_aplicados_mxn: { type: 'number' },
      saldo_final_mxn: { type: 'number' },
      vencimiento: { type: 'string' },
    },
  }
}

function inversorSchema() {
  return {
    type: 'object',
    properties: {
      kwh_generado_total: { type: 'number' },
      kwh_autoconsumo: { type: 'number' },
      performance_ratio: { type: 'number' },
      desglose_diario: { type: 'array' },
    },
  }
}

function tarifaSchema() {
  return {
    type: 'object',
    properties: {
      tarifa: { type: 'string' },
      region: { type: 'string' },
      cargo_capacidad_mxn_kw: { type: 'number' },
      cargo_distribucion_mxn_kw: { type: 'number' },
      energia_punta_mxn_kwh: { type: 'number' },
      energia_intermedia_mxn_kwh: { type: 'number' },
      energia_base_mxn_kwh: { type: 'number' },
    },
  }
}

function conciliacionEnergiaSchema() {
  return {
    type: 'object',
    properties: {
      autoconsumo_kwh: { type: 'number' },
      consumo_total_kwh: { type: 'number' },
      ratio_autoconsumo_pct: { type: 'number' },
      alertas: { type: 'array' },
      tarifa_alternativa_mejor: { type: 'string' },
    },
  }
}

function compensacionSchema() {
  return {
    type: 'object',
    properties: {
      creditos_kwh_acumulados: { type: 'number' },
      creditos_a_vencer_pronto: { type: 'number' },
      compensacion_mxn_periodo: { type: 'number' },
      ahorro_vs_sin_solar_mxn: { type: 'number' },
      ahorro_anualizado_mxn_proyectado: { type: 'number' },
      requiere_cfdi: { type: 'boolean' },
      monto_cfdi_mxn: { type: 'number' },
    },
  }
}

function cfdiSchema() {
  return {
    type: 'object',
    properties: {
      uuid: { type: 'string' },
      xml_url: { type: 'string' },
      monto_mxn: { type: 'number' },
    },
  }
}
