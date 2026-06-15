# Troubleshooting — problemas comunes y soluciones

**Propósito**: catálogo de problemas frecuentes y cómo resolverlos.

**Audiencia**: cualquiera operando plugins-mx.

**Pre-lectura**: [guia-instalacion.md](guia-instalacion.md).

---

## Instalación y carga de plugins

### "Claude Code no detecta el plugin"

**Diagnóstico**:
```bash
# Verificar estructura
ls -la ~/plugins-mx/freelancers-mx/.claude-plugin/
# Debe haber: plugin.json
```

**Solución**:
- Si falta `.claude-plugin/`: revisar que estás apuntando al directorio correcto del plugin (no a la raíz del monorepo)
- Si falta `plugin.json`: el plugin está incompleto
- Si hay typo en `plugin.json`: validar con `jq . freelancers-mx/.claude-plugin/plugin.json`

### "Skills no aparecen"

**Diagnóstico**:
```bash
# Verificar lint
./scripts/lint-skills.sh
```

**Solución**:
- Skills con frontmatter inválido no se cargan. El lint los identifica.
- Re-sincronizar `_shared/` si los skills compartidos están desactualizados:
  ```bash
  ./scripts/sync-shared.sh
  ```

### "Commands no aparecen al escribir /"

**Diagnóstico**:
- Verifica que los archivos `commands/<name>.md` existan
- Verifica que `plugin.json` los liste en `"commands":`

**Solución**:
- Recargar la sesión: salir y volver a entrar a `claude --plugin-dir ...`
- En sesión activa: `/reload-plugins` si tu versión lo soporta

---

## Skills triggering

### "El skill correcto no se invoca cuando hablo del tema"

**Causa**: el `description:` del skill no captura tu fraseo.

**Diagnóstico**:
1. Toma 3-5 fraseos que dirías sobre el tema
2. Compara contra el `description:` del skill

**Solución**:
- Editar `description:` agregando los sinónimos faltantes
- Validar con `lint-skills.sh` (≥80 chars)
- Re-cargar la sesión

**Ejemplo**:
Si dices "necesito sacar factura de Bimbo" y `cfdi-emision` no triggea:
- Agregar "sacar factura" al description
- Probar de nuevo

### "Triggea un skill que no debería"

**Causa**: description demasiado amplio o keyword compartido con otro dominio.

**Solución**:
- Agregar cláusula explícita "NO usar para [X]"
- Reducir keywords ambiguos
- Probar el eval `evals/<skill>.eval.json` con `should_trigger: false` para detectar near-misses

---

## CFDI y timbrado

### "El PAC rechaza el CFDI"

**Causas comunes y soluciones**:

| Error PAC | Causa | Solución |
|---|---|---|
| "RFC del receptor no encontrado" | RFC inválido o no registrado en SAT | Validar con `rfc-validacion`, pedir Constancia al receptor |
| "Uso CFDI incompatible con régimen" | Receptor tiene régimen X pero usaste UsoCFDI no permitido | Cambiar a uso compatible (G03 es universal para empresas) |
| "CP no existe" | CP de 5 dígitos no en catálogo | Confirmar CP correcto del receptor |
| "Forma de pago 99 con PUE" | Inconsistencia método/forma | Cambiar a PUE+forma específica o PPD+99 |
| "Fecha fuera de rango" | CFDI con timestamp >72h pasado o futuro | Ajustar fecha al momento actual |
| "Sello emisor inválido" | CSD vencido o mal configurado | Renovar CSD ante SAT |
| "Total no cuadra" | Suma de conceptos ≠ subtotal | Revisar cálculo, redondeo |

### "Cancelación rechazada"

**Causas**:
- CFDI con >72h y monto >$1,000: requiere aceptación del receptor
- UUID no existe: validar primero
- Motivo no aplica al caso

**Solución**:
- Buzón Tributario del receptor para aceptar
- Esperar 3 días hábiles (default aceptado si no responde)
- Si motivo 01: incluir folio sustituto válido

### "CFDI tipo P (REP) marcado mal"

**Síntoma**: el receptor reporta que su contabilidad no balanceó.

**Causas comunes**:
- Faltó emitir REP del cobro PPD
- REP con monto incorrecto
- Vinculación equivocada al CFDI original

**Solución**:
- Validar que cada cobro de un CFDI PPD genere un REP en <10 días
- Cancelar REP malformado y emitir corregido

---

## RFC y validación

### "Validador dice que el RFC tiene fecha inválida"

**Causa**: los 6 dígitos centrales no son fecha real.

**Ejemplo**: `MAJG891332ABC` → mes 13 no existe.

**Solución**:
- Confirmar con el contribuyente los datos correctos
- Si es typo: corregir antes de timbrar

### "RFC con palabra inconveniente"

**Causa**: las primeras 4 letras forman palabra en la lista SAT.

**Solución**:
- El SAT habría sustituido la 4ta letra por X
- Pedir al contribuyente que confirme su RFC real
- NO bloquear sin verificar; podría ser caso raro real

### "RFC genérico no funciona en mi sistema"

**Causa**: el RFC `XAXX010101000` solo aplica con UsoCFDI `S01`.

**Solución**:
- Cambiar UsoCFDI a S01
- Solo usar genérico para facturas globales o público en general

---

## WhatsApp Business

### "Template rechazado por Meta"

**Razones comunes**:
- Categorización incorrecta (UTILITY que es realmente MARKETING)
- Lenguaje promocional excesivo en UTILITY
- Mayúsculas sostenidas
- Emojis excesivos
- URLs dinámicas (deben ser variables o fijas)
- Falta el ejemplo en el campo `example`

**Solución**:
- Revisar la razón específica en Business Manager
- Ajustar conforme a `_shared/whatsapp-business-mx/SKILL.md`
- Reenviar

### "Mensajes no se entregan"

**Causas**:
- Número destinatario no en WhatsApp
- Quality Rating de tu cuenta bajó (RED)
- Conversation cap alcanzado
- Cliente bloqueó tu número

**Solución**:
- Verificar formato del teléfono (incluir código país)
- Revisar Quality Rating en Business Manager
- Esperar reset diario si alcanzaste el cap
- Si bloqueado: no hay solución técnica, respetar

### "Quality Rating bajó a YELLOW/RED"

**Causas**:
- Muchos reportes de spam
- Templates MARKETING agresivos
- No respetar opt-outs

**Solución**:
- Pausar campañas MARKETING
- Revisar opt-outs no procesados
- Esperar mejora gradual (puede tomar semanas)
- Evitar volumen excesivo

---

## Pagos y CFDI atómico

### "Webhook de pago no llega"

**Diagnóstico**:
- Verificar URL del webhook accesible públicamente
- Verificar firma del webhook
- Revisar logs del servidor

**Solución**:
- Test con ngrok en desarrollo
- Validar HTTPS en producción
- Revisar IP allowlist en panel de pasarela

### "Pago confirmado pero CFDI no se emite"

**Causas**:
- Error en validación local (RFC, CP, etc.)
- Falla del PAC
- Webhook procesó pero CFDI falló silenciosamente

**Solución**:
- Logs del proceso webhook → CFDI
- Manual retry del CFDI
- Validar datos antes de timbrar

### "Refund no genera nota de crédito"

**Causas**:
- Webhook de refund no manejado
- Skill no implementa flujo de Egreso

**Solución**:
- Implementar handler de webhook payment.refunded
- Disparar `cfdi-emision` con TipoComprobante=E, TipoRelacion=01, vinculado al CFDI original

---

## Cobranza y comunicación

### "Cliente no responde recordatorios"

**Flujo esperado**:
- Etapa 1 (día 1-3): recordatorio amable
- Etapa 2 (día 7-15): formal con recargo
- Etapa 3 (día 20+): llamada/escalación
- Etapa 4 (día 30+): carta formal
- Etapa 5 (día 45+): suspensión / extrajudicial

**Si después de etapa 5 no responde**:
- Pasar a despacho de cobranza
- Vender la cuenta a buró
- Dar por perdido si los costos legales superan el monto

### "Padres del colegio piden refacturar CFDIs viejos"

**Causas**:
- CFDI mal emitido inicialmente
- Cambio de RFC del padre
- Cambio de UsoCFDI

**Solución**:
- Refacturación dentro del mismo ejercicio fiscal (sustitución motivo 01)
- Si es de ejercicio cerrado: difícil/imposible. El padre debe presentar declaración con CFDI viejo y consultar contador

### "Garantía: cliente reclama pero ya pasó el plazo"

**Caso**: cliente avisa día 28 pero lleva auto día 35.

**Solución**:
- Si el aviso (mensaje, llamada, email) está documentado del día 28, la garantía aplica
- El criterio es la fecha del aviso, no la fecha de llegada al taller

---

## Tooling

### "sync-shared.sh no sincroniza algo"

**Causa común**: el `plugin.json` del vertical no declara ese skill en `"skills":`.

**Solución**:
- Agregar `"skills/<nombre>"` al array de skills del plugin.json
- Re-correr `./scripts/sync-shared.sh`

### "lint-skills.sh falla"

**Causas**:
- Frontmatter sin delimitadores `---`
- name no kebab-case
- description <80 chars
- name vacío

**Solución**:
- Leer el error específico
- Corregir el SKILL.md
- Re-correr lint

### "Git push rechazado por hooks"

**Si tienes pre-commit configurado**:
- Lint debe pasar antes de commit
- Resolver el error y re-commitear

---

## Performance

### "Sesión de Claude lenta"

**Causas**:
- Demasiados plugins cargados simultáneamente
- Skills muy largos (>1000 líneas) inflando contexto
- MCP servers con respuestas pesadas

**Solución**:
- Cargar solo el plugin del vertical activo
- Mover contenido largo a `references/` (carga bajo demanda)
- Revisar MCP servers desactivar los no usados

### "Lint tarda mucho"

**Causa**: muchos archivos SKILL.md.

**Solución**:
- Es esperado con 50+ skills (segundos)
- Para CI, paralelizar (no implementado aún)

---

## Datos y privacidad

### "Borré accidentalmente datos de un cliente"

**Solución**:
- Restaurar de backup más reciente
- Verificar política de retención
- Si afecta a una solicitud de cancelación ARCO: documentar

### "Cliente pide cancelación de sus datos (ARCO)"

**Procedimiento**:
1. Validar identidad del titular (copia INE)
2. Identificar todos los datos del titular en tu sistema
3. Cancelar conforme a política (período de bloqueo + supresión)
4. Confirmar al titular en 20 días hábiles
5. Documentar en bitácora ARCO

---

## Emergencias

### "Detecté que comprometí mi `.env`"

**Acción inmediata**:
1. Rotar TODAS las credenciales expuestas
2. Revisar logs por uso no autorizado
3. Notificar a clientes si datos pudieron ser accedidos
4. Considerar notificar al INAI si es grave

### "PAC reporta uso anormal de mi cuenta"

**Acción**:
1. Verificar logs del PAC
2. Cambiar API key
3. Revisar timbrados emitidos no autorizados
4. Cancelar los no autorizados con motivo 03

### "Cliente PROFECO me citó por queja"

**Acción**:
1. NO ignorar el citatorio (plazos legales)
2. Recopilar TODA la documentación:
   - Bitácora WhatsApp
   - Cotización autorizada
   - OT firmada
   - Certificado de garantía
3. Asistir a audiencia conciliatoria
4. Si hay buen expediente: conciliar favorablemente
5. Si no: considerar abogado especializado

---

## Ver también

- [seguridad.md](seguridad.md) — para temas de credenciales
- [faq.md](faq.md) — preguntas frecuentes
- [estado-real.md](estado-real.md) — qué está sin validar y por qué puede fallar
