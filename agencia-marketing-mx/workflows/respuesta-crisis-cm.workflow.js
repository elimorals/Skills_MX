// Workflow ejecutable: respuesta-crisis-cm
//
// Disparado por trigger manual o detección automática de crisis en CM:
// comentario negativo viral, hashtag negativo, mensaje compartido masivamente.
//
// args: { cliente_id, plataforma, url_post, severidad_inicial: "leve"|"moderada"|"grave" }

export const meta = {
  name: 'respuesta-crisis-cm',
  description: 'Crisis CM: clasificación + escalación + respuesta pública + mover a DM + resolución + documentar. Tiempos: < 30 min para alertar, < 2 hrs respuesta pública, < 24 hrs resolución DM.',
  whenToUse: 'Manual o trigger: comentario con engagement viral, hashtag negativo trending, mensaje compartido masivamente.',
  phases: [
    { title: 'Clasificación', detail: 'evaluar severidad real + impacto potencial' },
    { title: 'Escalación', detail: 'notificar manager/dueño cliente en < 30 min' },
    { title: 'Respuesta pública', detail: 'borrador empático medido < 2 hrs' },
    { title: 'Mover a DM', detail: 'tratar caso privado' },
    { title: 'Resolución', detail: '< 24 hrs solución acordada' },
    { title: 'Documentación', detail: 'guardar caso para protocolo' },
  ],
}

const { cliente_id, plataforma, url_post, severidad_inicial = 'moderada' } = args || {}
if (!cliente_id || !plataforma || !url_post) {
  throw new Error('args requeridos: { cliente_id, plataforma, url_post }')
}

log(`Crisis CM: cliente ${cliente_id} en ${plataforma}`)

phase('Clasificación')

const clasificacion = await agent(
  `Analiza el post viral en ${plataforma} URL ${url_post} usando skill community-management-mx + reglas de detección:
   - Severidad final: leve / moderada / grave / catastrofica
   - Impacto potencial: número de personas alcanzadas, riesgo legal, riesgo reputacional
   - Tipo: queja válida, mentira maliciosa, troll, competencia
   - Tono recomendado de respuesta: empático, factual, legal, ignorar
   Devuelve análisis estructurado.`,
  { label: 'analizar-crisis', phase: 'Clasificación', schema: { type: 'object', properties: { severidad: { enum: ['leve', 'moderada', 'grave', 'catastrofica'] }, impacto: { type: 'object' }, tipo: { type: 'string' }, tono_recomendado: { type: 'string' } } } }
)

if (clasificacion.severidad === 'leve' && clasificacion.tipo !== 'queja válida') {
  log('Severidad leve sin queja válida — ignorar o respuesta corta')
  return { veredicto: 'ignorar', clasificacion }
}

phase('Escalación')

await agent(
  `Notifica al manager/dueño del cliente ${cliente_id} en < 30 min via WhatsApp con:
   - URL del post: ${url_post}
   - Severidad: ${clasificacion.severidad}
   - Impacto estimado: ${JSON.stringify(clasificacion.impacto)}
   - Acción recomendada inmediata
   Template "utility_crisis_cm_urgente".`,
  { label: 'escalar-manager', phase: 'Escalación' }
)

phase('Respuesta pública')

const respuestaPublica = await agent(
  `Genera borrador de respuesta pública al post en ${plataforma} con:
   - Tono ${clasificacion.tono_recomendado}
   - Reconocer la situación específica
   - NO discutir en público ni atacar
   - Invitar a DM para resolver
   - Mostrar acción correctiva concreta si aplica
   - Profesional, máximo 280 caracteres para Twitter, sin restricción para Facebook/Instagram

   La respuesta la VEN futuros clientes — tiene que verse buena.`,
  { label: 'borrador-respuesta', phase: 'Respuesta pública', schema: { type: 'object', properties: { texto: { type: 'string' }, idiomas: { type: 'array' } } } }
)

log(`Borrador respuesta listo — REQUIERE APROBACIÓN HUMANA antes de publicar.`)

phase('Mover a DM')

const dmTemplate = await agent(
  `Genera template de mensaje directo (DM) para mover el caso a privado:
   "Hola [Nombre], lamentamos lo sucedido. Te escribimos por DM para resolverlo en privado y darte solución concreta. ¿Tienes 5 minutos para platicar?"`,
  { label: 'template-dm', phase: 'Mover a DM' }
)

phase('Resolución')

await agent(
  `Crea plan de resolución estructurado:
   1. Contactar al cliente en DM dentro de 2 horas de respuesta pública
   2. Escuchar versión completa
   3. Ofrecer 3 opciones de compensación (reembolso, replacement, gesto comercial)
   4. Acordar solución concreta
   5. Documentar acuerdo por escrito
   6. Implementar solución dentro de 24 horas
   7. Follow-up 7 días después`,
  { label: 'plan-resolucion', phase: 'Resolución' }
)

phase('Documentación')

await agent(
  `Documenta el caso completo en crisis-cm/<cliente_id>/<fecha>/:
   - clasificacion.json
   - respuesta-publica-publicada.txt
   - dm-conversacion-resumen.md
   - solucion-acordada.md
   - lecciones-aprendidas.md (qué causó la crisis para evitar futuras)`,
  { label: 'documentar', phase: 'Documentación' }
)

return {
  status: 'manejada',
  cliente_id,
  plataforma,
  severidad_final: clasificacion.severidad,
  borrador_respuesta_publica: respuestaPublica.texto,
  dm_template: dmTemplate,
  tiempo_respuesta_objetivo: '2 horas',
  tiempo_resolucion_objetivo: '24 horas',
}
