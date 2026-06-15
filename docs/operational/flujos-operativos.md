# Flujos operativos cross-vertical

**Propósito**: workflows comunes que mezclan skills de varios verticales.

**Audiencia**: usuarios power.

**Pre-lectura**: guías por vertical.

---

## Flujo 1: Onboarding cliente completo (cualquier vertical B2B)

```
1. Recopilar datos fiscales y de contacto del cliente
   /freelancers:onboarding <cliente>
   (También aplica para agencia, colegio empresarial, taller flotilla)

2. Skill cliente-onboarding invoca:
   - rfc-validacion: valida RFC del cliente
   - cfdi-emision: valida CP y régimen
   - compliance-lfpdppp: genera aviso de privacidad

3. Genera artifacts:
   - clientes/<id>/ficha.json
   - clientes/<id>/contrato-marco.md
   - clientes/<id>/aviso-privacidad.md

4. Envío al cliente vía WhatsApp con templates approvados
   (whatsapp-business-mx)
   - Contrato para firma
   - Aviso de privacidad para aceptación

5. Recepción de firma y archivo
```

---

## Flujo 2: Cotización → autorización → ejecución → CFDI → cobro

Aplicable transversalmente. Aquí mostrado para `freelancers-mx`:

```
Paso 1: Cotización
   /freelancers:cotizar <cliente> <scope>
   → genera cotizacion.md con desglose IVA/retenciones correctas

Paso 2: Envío al cliente
   → WhatsApp template "utility_cotizacion_lista"
   → Cliente responde "ACEPTO" o pide ajuste

Paso 3: Si acepta, generar contrato si aplica
   (propuesta-comercial si es scope grande)

Paso 4: Recibo de anticipo
   → CFDI tipo I con MétodoPago PUE (cobrado al recibir anticipo)
   → o esquema de "anticipo SAT" (3 CFDIs) si scope final no está definido

Paso 5: Ejecución del trabajo

Paso 6: Cierre y cobro final
   → CFDI tipo I por monto restante
   → Si fue PPD: emitir REP (CFDI tipo P) por el pago

Paso 7: Registro en bitácora
   → clientes/<id>/proyectos/<id>/
```

---

## Flujo 3: Cobranza mensual (multi-cliente)

```
Día 1 del mes:
   Para cada cliente con factura emitida el mes anterior:
   /freelancers:cobranza <cliente>
   → Skill cobranza-seguimiento determina etapa según mora
   → Envía mensajes correspondientes
   → Registra en cobranza/<cliente>/historial.md

Día 7:
   Re-evaluar quien no pagó. Etapa 2 (recordatorio formal con recargo).

Día 15:
   Etapa 3 (llamada o escalación a director).

Día 30:
   Etapa 4 (carta formal).

Día 45:
   Etapa 5 (suspensión / extrajudicial).
```

---

## Flujo 4: Mes de cierre fiscal (freelancer)

```
Día 1-15:
   Recopilar CFDIs emitidos del mes (descarga del PAC o SAT).
   Recopilar CFDIs recibidos del mes (gastos).
   Cobranza día 1, 7.

Día 15:
   /freelancers:pago-provisional <mes> <año>
   → Calcula ISR a pagar.
   → Identifica retenciones acreditables.
   → Alerta sobre depósitos en efectivo > $15k.

Día 16:
   Presentar declaración en sat.gob.mx con e.firma.

Día 17:
   Plazo límite. Realizar pago.

Día 18-31:
   Cobranza día 15 y subsiguientes.
   Empezar a recopilar CFDIs del mes en curso.
```

---

## Flujo 5: Crisis de cliente en redes (agencia)

```
Detección:
   - Comentario negativo con engagement creciente
   - Mensaje viral compartido
   - Hashtag negativo trending

Paso 1: Clasificación
   community-management-mx → "queja con riesgo viral"

Paso 2: Notificar al manager / dueño del cliente
   En < 30 min

Paso 3: Respuesta pública inicial (medida, empática)
   En < 2 horas

Paso 4: Mover a DM
   Plantilla: "Te escribimos por DM para resolverlo"

Paso 5: Resolver en DM en < 24 horas

Paso 6: Follow-up al cliente
   "¿Te resolvimos? ¿Algo más?"

Paso 7: Si resuelve favorablemente, pedir actualización pública

Paso 8: Documentar el caso para retroalimentar protocolos
```

---

## Flujo 6: Reclamación de garantía (taller)

```
Cliente regresa con falla:

Paso 1: Recepción amable, NO defensiva
   /talleres:garantia reclamo <OT-original>

Paso 2: Validar vigencia
   - Días desde cierre vs plazos
   - 30 días MO / 90 días refacciones

Paso 3: Diagnóstico de validación
   - Mecánico (idealmente el mismo) inspecciona
   - Determina Caso A/B/C/D

Paso 4: Comunicación al cliente
   Según caso:
   - A (cubierta): proceder sin costo
   - B (falla nueva): nueva cotización
   - C (uso indebido): cobro diagnóstico
   - D (necesita más análisis): tiempo adicional

Paso 5: Resolución
   - Si A: trabajo sin costo, OT vinculada a original
   - Si B/C: si autoriza, nuevo flujo de cotización-autorización-OT
   - Si rechaza: entregar auto y documentar

Paso 6: Documentación
   - garantias/<OT>/reclamo-<fecha>.md
   - Fotos del estado
   - Comunicación con cliente

Esta documentación es CLAVE para defensa PROFECO si llegara.
```

---

## Flujo 7: Reporte mensual cliente (agencia)

```
Día 1 del mes (cierre del anterior):

Para cada cliente activo (5-25):

   Paso 1: Descargar datos
      - Meta Ads Manager → CSV
      - Google Ads → CSV
      - TikTok Ads → XLSX
      - GA4 → Looker Studio export
      - Redes orgánicas → screenshots de stats

   Paso 2: /agencia:reporte <cliente> <mes>
      → reporte-mensual-cliente estructura el documento
      → Calcula variaciones vs mes anterior
      → Detecta winners/losers
      → Sugiere insights

   Paso 3: Output
      - reportes/<cliente>/<mes>.md (completo)
      - reportes/<cliente>/<mes>-resumen.md (1 página)

   Paso 4: Conversión a Slides
      Usar skill pdf o docx según preferencia

   Paso 5: Presentación al cliente
      Agenda 30-60 min según contrato
      Llevar resumen de 1 página + dashboard

   Paso 6: Documentar decisiones del cliente
      Próximos pasos del mes siguiente
```

---

## Flujo 8: Apertura de ciclo escolar (colegio)

```
Junio-Julio (preparación):

   Para cada familia inscribiéndose:
      /colegios:onboarding <familia>
      → Captura datos fiscales padre receptor de CFDI
      → Datos del alumno (CURP validado)
      → Aviso de privacidad para menores
      → Consentimientos específicos (fotos, marketing eventos)

Agosto (inicio):

   /colegios:aviso-padres bienvenida todo-colegio
   → Bienvenida al ciclo
   → Recordatorio de pago de inscripción

Septiembre y mensual:

   /colegios:cobranza para familias con adeudo
   /colegios:facturar-colegiatura para familias que pagaron

   /colegios:aviso-padres calificaciones <grado>
   → Cuando se cierra cada bimestre

   /colegios:aviso-padres junta <grado>
   → Convocatorias a juntas

Junio (cierre):

   Para cada padre:
      Constancia anual de servicios educativos (CFDI deducible)

   Para cada alumno:
      /colegios:constancia <alumno> boleta
      /colegios:constancia <alumno> estudios

   Para familias que avanzan al siguiente grado:
      Re-inscripción con nueva ficha
```

---

## Flujo 9: Vulneración LFPDPPP detectada

```
Paso 0: Detectar
   - Acceso no autorizado a base de datos
   - Pérdida de dispositivo con datos
   - Compromiso de credenciales

Paso 1: Contener (inmediato)
   - Rotar credenciales afectadas
   - Aislar el sistema comprometido
   - Bloquear accesos

Paso 2: Documentar
   - Fecha y hora del incidente
   - Qué pasó
   - Qué datos pudieron ser afectados
   - Qué titulares afectados

Paso 3: Evaluar gravedad
   - Si afecta significativamente derechos de titulares → notificar

Paso 4: Notificar a titular afectado
   Usar plantilla en compliance-lfpdppp
   "Sin dilación" según LFPDPPP

Paso 5: Notificar al INAI si es grave
   Vía portal INAI o oficio

Paso 6: Mitigar y prevenir
   - Parchar vulnerabilidad
   - Auditar otras posibles brechas
   - Capacitar al personal si fue error humano

Paso 7: Documentar en bitácora de incidentes
   - Para auditorías futuras
   - Para mejorar procesos
```

---

## Flujo 10: Cambio de régimen fiscal (freelancer)

```
Caso: pasar de PFAE (612) a RESICO (626).

Paso 0: Decisión informada
   /freelancers:pago-provisional sin sin (proyección comparativa)
   → Estima ISR en cada régimen para tu volumen

Paso 1: Aviso al SAT
   Trámite en portal con e.firma
   Cambio efectivo desde el siguiente ejercicio fiscal (típicamente)

Paso 2: Actualizar config local
   editar config.json → regimen_fiscal: "626"

Paso 3: Confirmar a clientes
   Enviar mensaje:
   "Te informo que cambié de régimen fiscal a RESICO. 
    A partir de [fecha], la retención que me harás cambia 
    de 10% ISR + 10.67% IVA a 1.25% ISR (sin retener IVA).
    Te paso la nueva Constancia de Situación Fiscal."

Paso 4: Re-validar CFDIs futuros
   freelance-tax-mx usa la nueva tarifa automáticamente

Paso 5: Declaración del ejercicio anterior
   Bajo régimen viejo (PFAE)

Paso 6: Pagos provisionales nuevo ejercicio
   Bajo régimen nuevo (RESICO)
```

---

## Patrones comunes a todos los flujos

### Pattern: Confirmar antes de actuar

Antes de cualquier operación con efecto externo (timbrar CFDI, enviar WhatsApp masivo, ejecutar pago), el skill debe presentar resumen y pedir confirmación.

### Pattern: Bitácora siempre

Cada operación se registra con timestamp en una bitácora. Es lo que te defiende ante auditorías y disputas.

### Pattern: Mock primero

Probar el flujo entero en mock antes de activar integración real. Reduces riesgo a cero durante prueba.

### Pattern: Reversibilidad

Cuando sea posible, hacer cambios reversibles (CFDI cancelable, mensaje editable, registro editable). Lo irreversible (envío masivo de WhatsApp a 500 padres) requiere confirmación extra.

---

## Ver también

- Guías por vertical (freelancers, agencia, colegios, talleres)
- [troubleshooting.md](troubleshooting.md) — cuando algo falla en estos flujos
- [seguridad.md](seguridad.md) — proteger los flujos
