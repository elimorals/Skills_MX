// Workflow ejecutable: migracion-rfc-a-otro-regimen
//
// Helper fiscal: analiza pros/contras de cambiar de régimen y guía el proceso.
// Caso típico: PFAE 612 → RESICO PF 626 (más simple), o RESICO → PFAE (al rebasar tope).
//
// args: { rfc, regimen_actual, regimen_propuesto, ejercicio_actual: int, decision_real?: bool }

export const meta = {
  name: 'migracion-rfc-a-otro-regimen',
  description: 'Analiza cambio de régimen fiscal (PFAE↔RESICO PF típicamente) con proyección ISR comparativa + checklist de pasos administrativos + comunicación a clientes + recordatorios calendario.',
  whenToUse: 'Cuando usuario considera cambiar régimen o se ve obligado (RESICO rebasó $3.5M).',
  phases: [
    { title: 'Análisis', detail: 'pros/contras + ISR comparativo proyectado' },
    { title: 'Decisión', detail: 'requiere confirmación humana antes de ejecutar' },
    { title: 'Ejecución', detail: 'pasos SAT + cambios locales + comunicar clientes' },
    { title: 'Validación', detail: 'confirmar régimen en padrón post-cambio' },
  ],
}

const { rfc, regimen_actual, regimen_propuesto, ejercicio_actual, decision_real = false } = args || {}
if (!rfc || !regimen_actual || !regimen_propuesto || !ejercicio_actual) {
  throw new Error('args requeridos: { rfc, regimen_actual, regimen_propuesto, ejercicio_actual }')
}

if (regimen_actual === regimen_propuesto) {
  return { status: 'sin_cambio', razon: 'régimen actual = propuesto' }
}

log(`Migración régimen ${regimen_actual} → ${regimen_propuesto} para ${rfc}`)

phase('Análisis')

const analisis = await agent(
  `Compara régimen ACTUAL (${regimen_actual}) vs PROPUESTO (${regimen_propuesto}) para RFC ${rfc} ejercicio ${ejercicio_actual}.

   Para cada régimen calcula con datos del ejercicio ACTUAL (a la fecha):
   - ISR proyectado anual con ese régimen
   - Carga administrativa (RESICO no permite gastos deducibles, PFAE sí)
   - Retenciones que tus clientes te harán (RESICO 1.25%, PFAE 10%+10.67% IVA)
   - Posibilidad de saldo a favor / a pagar
   - Riesgo de SAT (RESICO menos auditado pero más estricto en tope)

   Genera:
   - tabla_comparativa
   - recomendacion: "migrar" | "mantener" | "depende_volumen"
   - razon_principal: una oración`,
  { label: 'analisis', phase: 'Análisis', schema: { type: 'object', properties: { recomendacion: { type: 'string' }, razon_principal: { type: 'string' }, tabla_comparativa: { type: 'object' } } } }
)

log(`Recomendación: ${analisis.recomendacion} — ${analisis.razon_principal}`)

if (!decision_real) {
  return {
    status: 'analisis_dry_run',
    analisis,
    siguiente_paso: 'Ejecutar de nuevo con decision_real=true para proceder',
  }
}

phase('Decisión')

if (analisis.recomendacion === 'mantener') {
  return {
    status: 'aborto_decision_humana',
    analisis,
    razon: 'recomendación = mantener — no proceder con migración',
  }
}

phase('Ejecución')

const checklist = await agent(
  `Genera checklist de migración ${regimen_actual} → ${regimen_propuesto}:

   1. SAT — Aviso de cambio:
      - Portal SAT → mi RFC → actualización de obligaciones
      - Requiere e.firma vigente
      - Cambio efectivo desde el siguiente ejercicio fiscal (1 enero ${ejercicio_actual + 1})
      - Si urgente: ciertos cambios aplican al mes siguiente con justificación

   2. Comunicación a clientes (CRÍTICO):
      - WhatsApp/email a TODOS los clientes con régimen 612 cambia a 626:
        "A partir de [fecha], cambio mi régimen fiscal a RESICO PF. La retención que me hacías cambia de 10% ISR + 10.67% IVA a 1.25% ISR. Te paso mi nueva Constancia de Situación Fiscal: [link]."

   3. Cambios en config local:
      - Editar config.json: regimen_fiscal: "${regimen_propuesto}"
      - freelance-tax-mx automáticamente usará la nueva tarifa

   4. Calendario:
      - Última declaración bajo régimen viejo (diciembre ${ejercicio_actual})
      - Primera bajo régimen nuevo (enero ${ejercicio_actual + 1})
      - Declaración anual ejercicio ${ejercicio_actual} bajo régimen viejo
      - Anual ejercicio ${ejercicio_actual + 1} bajo régimen nuevo

   5. Validaciones post-cambio:
      - Verificar en padrón SAT que el cambio surtió efecto
      - Validar que primer CFDI emitido bajo régimen nuevo tenga régimen correcto`,
  { label: 'checklist', phase: 'Ejecución', schema: { type: 'object', properties: { pasos: { type: 'array' }, plazo_dias: { type: 'number' } } } }
)

phase('Validación')

await agent(
  `Programa recordatorio cron para validar el ${new Date(Date.UTC(ejercicio_actual + 1, 0, 5)).toISOString().slice(0, 10)} (1 sem post-cambio):
   1. Consultar padrón SAT del RFC ${rfc} y confirmar régimen es ${regimen_propuesto}
   2. Si no cambió: alertar para revisar manualmente
   3. Si cambió: marcar config local como vigencia_validada=true`,
  { label: 'agendar-validacion', phase: 'Validación' }
)

return {
  status: 'migracion_iniciada',
  rfc,
  regimen_anterior: regimen_actual,
  regimen_nuevo: regimen_propuesto,
  fecha_efectiva: `${ejercicio_actual + 1}-01-01`,
  analisis,
  checklist,
  validacion_post_cambio: `${ejercicio_actual + 1}-01-05`,
}
