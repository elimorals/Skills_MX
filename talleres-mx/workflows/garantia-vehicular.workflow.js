// Workflow ejecutable: garantia-vehicular
//
// Disparado por reclamo de cliente sobre servicio previo + posible trigger PROFECO.
// Documenta el caso con bitácora WA + diagnóstico + decisión + documento legal final.
//
// args: { ot_original, motivo_reclamo, fecha_reclamo, cliente_contacto, gravedad: "leve"|"media"|"grave" }

export const meta = {
  name: 'garantia-vehicular',
  description: 'Manejo de reclamo de garantía en taller: valida vigencia (mano obra 30d / refacciones 90d PROFECO), diagnostica si aplica (Caso A/B/C/D), comunica al cliente con bitácora WhatsApp, genera carta formal de respuesta si rechazo, prepara defensa PROFECO. Cuida documentar TODO el flujo porque la bitácora ES la defensa.',
  whenToUse: 'Cliente regresa con falla post-servicio. Trigger manual desde /talleres:garantia o automático al recibir queja PROFECO.',
  phases: [
    { title: 'Validar vigencia', detail: 'OT original + plazos PROFECO' },
    { title: 'Diagnóstico', detail: 'mecánico evalúa Caso A/B/C/D' },
    { title: 'Comunicación', detail: 'WhatsApp formal al cliente con resolución' },
    { title: 'Resolución', detail: 'ejecutar reparación gratis o cobrar nueva OT' },
    { title: 'Documentación', detail: 'archivo defensable para PROFECO' },
  ],
}

const { ot_original, motivo_reclamo, fecha_reclamo, cliente_contacto, gravedad = 'media' } = args || {}
if (!ot_original || !motivo_reclamo || !cliente_contacto) {
  throw new Error('args requeridos: { ot_original, motivo_reclamo, cliente_contacto }')
}

log(`Reclamo de garantía OT ${ot_original} | ${motivo_reclamo} | ${gravedad}`)

phase('Validar vigencia')

const vigencia = await agent(
  `Lee la OT original ${ot_original} y su certificado de garantía. Valida:
   1. Días transcurridos desde fecha de entrega vs plazo de garantía aplicable
   2. Kilómetros transcurridos desde entrega vs garantía-km si aplica
   3. El motivo del reclamo (${motivo_reclamo}) ¿coincide con servicios en garantía o son nuevos?

   Plazos PROFECO mínimos:
   - Mano de obra: 30 días naturales mínimo
   - Refacciones: 90 días naturales mínimo

   Devuelve { en_vigencia: bool, plazo_restante_dias: number, servicios_en_garantia: [...], razon_si_vencida: string }`,
  { label: 'validar-vigencia', phase: 'Validar vigencia', schema: { type: 'object', properties: { en_vigencia: { type: 'boolean' }, plazo_restante_dias: { type: 'number' }, servicios_en_garantia: { type: 'array' } } } }
)

if (!vigencia.en_vigencia) {
  return {
    status: 'sin_vigencia',
    razon: vigencia.razon_si_vencida,
    accion: 'Cotizar nueva OT — sin garantía aplicable',
    documento_a_emitir: 'Carta de aviso de vigencia agotada',
  }
}

phase('Diagnóstico')

const diagnostico = await agent(
  `Mecánico (idealmente el mismo que hizo el trabajo original) inspecciona y determina:

   - Caso A: garantía cubre — el servicio o refacción falló dentro de plazo y por causa imputable al taller → ATENDER SIN COSTO
   - Caso B: falla nueva no relacionada al servicio original → COTIZAR NUEVA OT con cliente
   - Caso C: uso indebido por el cliente (sin mantenimiento, modificaciones, abuso) → COBRAR DIAGNÓSTICO + sugerir reparación
   - Caso D: requiere más análisis (varios días) → COTIZAR diagnóstico extendido con autorización

   Devuelve { caso: "A"|"B"|"C"|"D", justificacion_tecnica: string, fotos_evidencia: [], costo_si_aplica: number }`,
  { label: 'diagnostico-mecanico', phase: 'Diagnóstico', schema: { type: 'object', properties: { caso: { enum: ['A', 'B', 'C', 'D'] }, justificacion_tecnica: { type: 'string' }, costo_si_aplica: { type: 'number' } } } }
)

phase('Comunicación')

const mensajeCliente = await agent(
  `Genera mensaje WhatsApp al cliente ${cliente_contacto} explicando la decisión basada en el Caso ${diagnostico.caso}:

   Caso A: "Hola [Nombre], evaluamos tu reclamo y procede en garantía. Vamos a reparar sin costo. Tiempo estimado: [X días]."
   Caso B: "Hola [Nombre], la falla actual no corresponde al servicio anterior. Te dejamos cotización de la nueva reparación: $[X]. ¿Autorizas?"
   Caso C: "Hola [Nombre], al revisar encontramos [razón uso indebido]. Esto no es cubierto por garantía. Cobro de diagnóstico: $[X]. Si autorizas reparación, costo: $[Y]."
   Caso D: "Hola [Nombre], necesitamos más tiempo de diagnóstico ([X días]). Cobro de diagnóstico extendido: $[Y]. ¿Autorizas?"

   Mantén tono respetuoso. Documenta el envío para defensa PROFECO.`,
  { label: 'mensaje-cliente', phase: 'Comunicación', schema: { type: 'object', properties: { mensaje: { type: 'string' }, plantilla: { type: 'string' } } } }
)

phase('Resolución')

let acciones = []
if (diagnostico.caso === 'A') {
  acciones = ['Crear OT-bis vinculada a la original', 'Reparar sin costo', 'Documentar reparación', 'Actualizar certificado garantía extendida si aplica']
} else if (diagnostico.caso === 'B') {
  acciones = ['Esperar autorización del cliente', 'Si autoriza: crear nueva OT', 'Si no autoriza: documentar y entregar vehículo']
} else if (diagnostico.caso === 'C') {
  acciones = ['Cobrar diagnóstico autorizado', 'Si autoriza reparación: nueva OT', 'Si rechaza: entregar vehículo con bitácora detallada del uso indebido (FOTOS clave para defensa)']
} else {
  acciones = ['Cobrar diagnóstico extendido', 'Comunicar resultado en plazo', 'Retornar al flujo según resultado']
}

phase('Documentación')

await agent(
  `Archiva caso defensable en garantias/${ot_original}/reclamo-${fecha_reclamo}/:
   - reclamo.json: motivo + fecha + gravedad
   - vigencia.json: validación de plazos
   - diagnostico.json: Caso A/B/C/D + justificación técnica + fotos
   - comunicacion-cliente.json: mensaje enviado + screenshot WA + respuesta del cliente
   - resolucion.json: qué se hizo + comprobantes
   - defensa-profeco.md: documento maestro listo para imprimir si PROFECO recibe queja

   Estos archivos son tu PROTECCIÓN. El día que PROFECO llegue, los entregas y ganas el caso.`,
  { label: 'archivar-defensa', phase: 'Documentación' }
)

return {
  ot_original,
  caso: diagnostico.caso,
  vigencia_aplicable: vigencia.en_vigencia,
  costo_cliente: diagnostico.costo_si_aplica || 0,
  mensaje_enviado: mensajeCliente.mensaje,
  acciones,
  proteccion_profeco_armada: true,
  ruta_documentacion: `garantias/${ot_original}/reclamo-${fecha_reclamo}/`,
}
