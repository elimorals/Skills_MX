// Workflow ejecutable: pedimento-importacion
//
// Importación end-to-end: clasificación TIGIE + cálculo impuestos + pedimento
// + IVA al importar (acreditable) + IMMEX (si aplica) + bitácora aduana.
//
// Cumple: LIGIE, Ley Aduanera, RGCE 2026, Ley del IVA Art. 24 (IVA importación),
// Decreto IMMEX (si certificación vigente).
//
// Invocar con: Workflow({scriptPath: "importadores-mx/workflows/pedimento-importacion.workflow.js", args: {...}})
//
// Inputs en `args`:
//   {
//     importador_rfc: string,
//     pedimento_borrador: {
//       proveedor_extranjero: string,
//       pais_origen: string,                // ISO 2 letras
//       incoterm: string,                   // EXW, FCA, CIF, DDP, etc.
//       moneda: string,                     // USD, EUR, CNY
//       valor_factura_origen: number,
//       fecha_factura: string,              // YYYY-MM-DD
//       transporte: "maritimo" | "aereo" | "terrestre",
//       puerto_entrada: string,             // MZLO, ALTM, NLD, etc.
//       mercancias: [
//         {
//           fraccion_arancelaria?: string,  // si la conoces; si no, se intenta clasificar
//           descripcion: string,
//           cantidad: number,
//           unidad_medida: string,
//           peso_kg: number,
//           valor_unitario: number,
//         }
//       ],
//     },
//     immex?: {
//       certificacion_vigente: boolean,
//       programa: string,
//     },
//     agente_aduanal_patente?: string,
//   }

export const meta = {
  name: 'pedimento-importacion',
  description: 'Importación end-to-end: clasificación TIGIE + cálculo IGI/IVA/DTA + pedimento + acreditamiento IVA + IMMEX. Compliance Ley Aduanera + RGCE 2026.',
  whenToUse: 'Cada operación de importación. Cron NO recomendado (cada importación es única).',
  phases: [
    { title: 'Clasificación', detail: 'parallel: clasificar cada mercancía en TIGIE + validar fracciones + permisos previos' },
    { title: 'Valoración', detail: 'tipo de cambio DOF + valor agregado por flete/seguro + ajustes' },
    { title: 'Impuestos', detail: 'IGI + IVA + DTA + IEPS (si aplica) + cuotas compensatorias' },
    { title: 'Pedimento', detail: 'borrador de pedimento listo para agente aduanal' },
    { title: 'Acreditamiento', detail: 'plan de acreditamiento IVA + bitácora aduana' },
  ],
}

const {
  importador_rfc,
  pedimento_borrador,
  immex,
  agente_aduanal_patente,
} = args || {}

if (!importador_rfc || !pedimento_borrador || !pedimento_borrador.mercancias) {
  throw new Error('args requeridos: { importador_rfc, pedimento_borrador:{...mercancias[]} }')
}

const folio = `pedimento-${importador_rfc.slice(0, 4)}-${Date.now().toString(36)}`
log(`Pedimento — folio ${folio} — ${pedimento_borrador.mercancias.length} mercancías`)
log(`Origen ${pedimento_borrador.pais_origen} → ${pedimento_borrador.puerto_entrada} vía ${pedimento_borrador.transporte}`)

// ============================================================
// FASE 1: Clasificación arancelaria (TIGIE)
// ============================================================
phase('Clasificación')

const clasificaciones = await pipeline(
  pedimento_borrador.mercancias,
  (merc, _, idx) => agent(
    merc.fraccion_arancelaria
      ? `Valida que la fracción arancelaria ${merc.fraccion_arancelaria} aplique a "${merc.descripcion}".
         Consulta la TIGIE vigente 2026. Devuelve si es correcta + tasa IGI + UMT + observaciones.`
      : `Clasifica la mercancía: "${merc.descripcion}" (cantidad ${merc.cantidad} ${merc.unidad_medida}, peso ${merc.peso_kg}kg, valor unitario ${pedimento_borrador.moneda} ${merc.valor_unitario}).
         Sugiere fracción arancelaria de 8 dígitos según TIGIE 2026.
         Identifica capítulo + partida + subpartida + fracción.
         Devuelve: { fraccion_8d, descripcion_oficial, tasa_igi_pct, umt, regulaciones_no_arancelarias, requiere_permiso_previo, base_legal }`,
    { label: `clasificar-${idx}`, phase: 'Clasificación', schema: clasificacionSchema() }
  ),
)

const fraccionesProblematicas = clasificaciones.filter(c => c?.requiere_permiso_previo || c?.observaciones?.length > 0)
if (fraccionesProblematicas.length > 0) {
  log(`⚠ ${fraccionesProblematicas.length} mercancías con permisos previos requeridos`)
}

// ============================================================
// FASE 2: Valoración aduanera
// ============================================================
phase('Valoración')

const valoracion = await agent(
  `Calcula el valor en aduana según Art. 64-78 Ley Aduanera (método transacción):

   Valor factura: ${pedimento_borrador.moneda} ${pedimento_borrador.valor_factura_origen}
   Incoterm: ${pedimento_borrador.incoterm}
   Transporte: ${pedimento_borrador.transporte}

   Ajustes obligatorios al valor de transacción:
   - Si incoterm NO incluye flete (EXW, FCA): SUMAR flete real
   - Si incoterm NO incluye seguro (EXW, FCA, CIF Costo+Seguro+Flete sí lo incluye): SUMAR seguro
   - Comisiones, royalties, asistencias técnicas del comprador: SUMAR

   Convierte a MXN usando TC DOF de la fecha de pago del pedimento (mp_banxico.get_tc).

   Devuelve:
   {
     valor_factura_mxn,
     ajuste_flete_mxn,
     ajuste_seguro_mxn,
     valor_en_aduana_mxn,
     tc_dof_aplicado,
     fecha_tc_dof,
   }`,
  { label: 'valor-aduana', phase: 'Valoración', schema: valoracionSchema() }
)

// ============================================================
// FASE 3: Cálculo de impuestos
// ============================================================
phase('Impuestos')

const impuestos = await agent(
  `Calcula impuestos al comercio exterior:

   Mercancías clasificadas: ${JSON.stringify(clasificaciones).slice(0, 3000)}
   Valor en aduana: ${valoracion.valor_en_aduana_mxn} MXN

   IGI (Impuesto General de Importación):
     Para cada mercancía: valor_en_aduana_mxn_de_la_mercancia × tasa_igi_pct
     ⚠ Verificar tratados: T-MEC (EUA/CAN), TLCUEM (UE), Alianza Pacífico — pueden reducir IGI a 0%
     pais_origen: ${pedimento_borrador.pais_origen}

   DTA (Derecho de Trámite Aduanero):
     Si IMMEX vigente: tasa preferencial (verificar tabla anual)
     Si no: 8 al millar sobre valor_en_aduana (con tope mínimo y máximo)
     immex: ${JSON.stringify(immex || {})}

   IVA importación (Art. 24-27 LIVA):
     Base = valor_en_aduana + IGI + DTA + otros impuestos al comercio
     Tasa = 16% (8% si zona fronteriza norte y aplica decreto)

   IEPS (si aplica): solo tabacos, bebidas alcohólicas, gasolinas, plaguicidas, alimentos no básicos densidad calórica.

   Devuelve desglose completo + total a pagar al banco.

   ⚠ Si immex.certificacion_vigente=true y mercancías son materias primas para transformación, puede aplicar
   esquema "0% IVA" con virtual A1 (devolución vs A1 normal con pago). Reportar las dos opciones.`,
  { label: 'calculo-impuestos', phase: 'Impuestos', schema: impuestosSchema() }
)

// ============================================================
// FASE 4: Borrador de pedimento
// ============================================================
phase('Pedimento')

const pedimento = await agent(
  `Genera el borrador de pedimento listo para agente aduanal:

   Clave pedimento: ${immex?.certificacion_vigente ? 'A4 (IMMEX) o V1' : 'A1 (definitiva)'}
   Importador: ${importador_rfc}
   Agente aduanal patente: ${agente_aduanal_patente || 'pendiente'}
   Aduana: ${pedimento_borrador.puerto_entrada}
   Fecha pago: ${new Date().toISOString().slice(0, 10)}

   Datos a incluir en cada sección oficial:
   - Datos generales
   - Proveedor extranjero
   - Mercancías con fracciones y cantidades
   - Pesos brutos/netos
   - Valor en aduana
   - Tasas y montos IGI/IVA/DTA/IEPS
   - Forma de pago (efectivo, depósito o garantía)

   Formato: JSON estructurado + markdown legible. NO emitir al SAT desde aquí —
   solo preparar para que el agente aduanal lo valide y transmita vía SAAI/VOCE.

   Datos: clasificaciones=${JSON.stringify(clasificaciones).slice(0, 2000)}, valoracion=${JSON.stringify(valoracion)}, impuestos=${JSON.stringify(impuestos)}`,
  { label: 'borrador-pedimento', phase: 'Pedimento', schema: pedimentoSchema() }
)

// ============================================================
// FASE 5: Plan de acreditamiento IVA + bitácora
// ============================================================
phase('Acreditamiento')

const acreditamiento = await parallel([
  () => agent(
    `Genera plan de acreditamiento del IVA pagado en aduana ($${impuestos.iva_total_mxn}):

     - Periodo de acreditamiento: mes en que se PAGÓ el pedimento (no en que se ingresó la mercancía)
     - Documento soporte: pedimento con sello digital + comprobante de pago bancario
     - Asiento contable sugerido (DR IVA acreditable / CR Bancos)
     - Registro en DIOT del mes correspondiente
     - Si IMMEX virtual A1: NO se acredita aquí, va por mecanismo diferente

     Recordatorio próximo periodo provisional con fecha límite día 17 del mes siguiente.`,
    { label: 'plan-iva-acreditable', phase: 'Acreditamiento' }
  ),
  () => agent(
    `Registra bitácora aduana inmutable en importadores-mx/bitacora-aduana.jsonl:
     - folio_interno: ${folio}
     - importador: ${importador_rfc}
     - fecha_creacion: ${new Date().toISOString()}
     - aduana: ${pedimento_borrador.puerto_entrada}
     - clave_pedimento: ${pedimento.clave_pedimento || 'A1'}
     - mercancias_count: ${pedimento_borrador.mercancias.length}
     - valor_en_aduana_mxn: ${valoracion.valor_en_aduana_mxn}
     - impuestos_totales_mxn: ${impuestos.total_pagar_mxn}
     - immex_vigente: ${!!immex?.certificacion_vigente}
     - conservacion_anios: 5 (CFF Art. 30) + 5 (Ley Aduanera Art. 36-A) = consultar al mayor`,
    { label: 'bitacora-aduana', phase: 'Acreditamiento' }
  ),
  () => agent(
    `Genera reporte ejecutivo en importadores/${importador_rfc.slice(0, 4)}/${folio}-resumen.md:
     - Resumen pedimento + agente aduanal
     - Top 5 mercancías por valor
     - Desglose impuestos
     - Plan de acreditamiento IVA
     - Próximos pasos (firma agente, pago, ingreso)
     - Alertas: permisos previos pendientes, fracciones dudosas, IMMEX no aprovechado`,
    { label: 'reporte', phase: 'Acreditamiento' }
  ),
])

return {
  status: 'completado',
  folio_interno: folio,
  importador: importador_rfc.slice(0, 4) + '***',
  aduana: pedimento_borrador.puerto_entrada,
  pais_origen: pedimento_borrador.pais_origen,
  mercancias_clasificadas: clasificaciones.length,
  fracciones_con_observaciones: fraccionesProblematicas.length,
  valor_en_aduana_mxn: valoracion.valor_en_aduana_mxn,
  impuestos: {
    igi_mxn: impuestos.igi_total_mxn,
    dta_mxn: impuestos.dta_mxn,
    iva_mxn: impuestos.iva_total_mxn,
    ieps_mxn: impuestos.ieps_total_mxn || 0,
    total_pagar_mxn: impuestos.total_pagar_mxn,
  },
  immex_aprovechado: !!immex?.certificacion_vigente,
  iva_acreditable_mxn: impuestos.iva_total_mxn,
  siguiente_paso: 'Validar con agente aduanal antes de transmisión SAAI',
}

// ============================================================
// Schemas
// ============================================================
function clasificacionSchema() {
  return {
    type: 'object',
    properties: {
      fraccion_8d: { type: 'string' },
      descripcion_oficial: { type: 'string' },
      tasa_igi_pct: { type: 'number' },
      umt: { type: 'string' },
      regulaciones_no_arancelarias: { type: 'array' },
      requiere_permiso_previo: { type: 'boolean' },
      observaciones: { type: 'array' },
      base_legal: { type: 'string' },
    },
  }
}

function valoracionSchema() {
  return {
    type: 'object',
    required: ['valor_en_aduana_mxn'],
    properties: {
      valor_factura_mxn: { type: 'number' },
      ajuste_flete_mxn: { type: 'number' },
      ajuste_seguro_mxn: { type: 'number' },
      valor_en_aduana_mxn: { type: 'number' },
      tc_dof_aplicado: { type: 'number' },
      fecha_tc_dof: { type: 'string' },
    },
  }
}

function impuestosSchema() {
  return {
    type: 'object',
    required: ['total_pagar_mxn'],
    properties: {
      igi_total_mxn: { type: 'number' },
      dta_mxn: { type: 'number' },
      iva_total_mxn: { type: 'number' },
      ieps_total_mxn: { type: 'number' },
      cuotas_compensatorias_mxn: { type: 'number' },
      total_pagar_mxn: { type: 'number' },
      opcion_immex_virtual: { type: 'object' },
      desglose_por_mercancia: { type: 'array' },
    },
  }
}

function pedimentoSchema() {
  return {
    type: 'object',
    properties: {
      clave_pedimento: { type: 'string' },
      json_estructurado: { type: 'object' },
      markdown_legible: { type: 'string' },
      ruta_archivo: { type: 'string' },
    },
  }
}
