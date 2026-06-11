# Plan de afinación productiva — de scaffolding a producción

Roadmap concreto semana a semana para llevar cada vertical de **4.5/9 puntos** (estado actual) a **7-8/9 puntos** (producción-grade).

## Supuestos del plan

- Trabajas tú (Elias) en estos plugins **part-time**, ~10-15 horas/semana por vertical activo.
- No hay equipo todavía; cuando aparezca, los plazos se reducen.
- Se prioriza UN vertical a la vez para no diluir esfuerzo.
- Conseguir partner del sector toma ~2-4 semanas en paralelo a la afinación técnica.

## Orden recomendado de afinación

```
Semanas 1-8:   freelancers-mx (dogfooding inmediato, riesgo bajo)
Semanas 9-16:  agencia-marketing-mx (alineado a tu día a día, riesgo bajo)
Semanas 17-24: talleres-mx (riesgo medio — necesita validación legal)
Semanas 25-36: colegios-mx (riesgo alto — necesita partner del sector indispensable)
```

Total: **~9 meses calendario** para los 4 verticales en producción.

---

## Vertical 1: freelancers-mx — semanas 1-8

### Semana 1: Dogfooding inicial
- [ ] Instalar el plugin `freelancers-mx` en tu Claude Code (`claude --plugin-dir ./freelancers-mx`)
- [ ] Crear tu ficha de cliente con `/freelancers:onboarding` para tus 3-5 clientes actuales reales (incluyendo @desimmortels)
- [ ] Generar cotizaciones reales con `/freelancers:cotizar` para próximos proyectos
- [ ] Anotar en `evals/freelancers-mx/results/2026-W01.md`: qué triggea bien, qué no, qué falta

### Semana 2: Calibración de descriptions
- [ ] Correr `evals/freelancers-mx/cotizacion-mxn.eval.json` manualmente con prompts
- [ ] Para cada false positive/false negative, ajustar `description:` del skill
- [ ] Repetir hasta ≥85% accuracy en el eval set
- [ ] Aplicar al resto de skills propios del vertical (propuesta-comercial, cobranza-seguimiento, cliente-onboarding, freelance-tax-mx)

### Semana 3: Validación fiscal del skill más riesgoso (freelance-tax-mx)
- [ ] Conseguir contador certificado para 2-4 horas de revisión (~$3-8k MXN). Linkedin, recomendación, o tu propio contador
- [ ] Validar tarifa Art. 96 vigente 2026 contra portal SAT
- [ ] Validar tasas RESICO PF vigentes
- [ ] Validar topes deducción personal Art. 151 vigentes
- [ ] Actualizar `freelance-tax-mx/SKILL.md` con valores verificados
- [ ] Marcar `vigencia_validada` en los fixtures correspondientes

### Semana 4: Integración Facturama sandbox
- [ ] Crear cuenta sandbox en Facturama (gratuita)
- [ ] Configurar `.env` con API key
- [ ] Activar el MCP server de Facturama en `.mcp.json`
- [ ] Correr fixture `case-01-cfdi-clasico` contra sandbox real
- [ ] Documentar discrepancias entre lo que el skill genera y lo que el PAC valida
- [ ] Ajustar `cfdi-emision` para producir output exacto que pasa validación PAC

### Semana 5: Validación legal de contratos y cartas
- [ ] Conseguir abogado mercantilista para revisión de:
  - `cliente-onboarding/SKILL.md` (contrato marco)
  - `propuesta-comercial/SKILL.md` (cláusulas T&Cs)
  - `cobranza-seguimiento/SKILL.md` (carta formal de requerimiento)
- [ ] ~4-6 horas de consulta (~$5-12k MXN)
- [ ] Aplicar correcciones

### Semana 6: Casos edge expandidos
- [ ] Documentar 10 casos edge reales que aparecieron en dogfooding
- [ ] Agregarlos como fixtures de prueba
- [ ] Ajustar skills para cubrirlos
- [ ] Expandir `references/` de los skills con esos casos

### Semana 7: Refinamiento final + métricas
- [ ] Score honesto por skill (apuntar a 7-8/9 en checklist)
- [ ] Documentar qué KPI esperar al usar el plugin (horas ahorradas/semana, CFDIs sin error, etc.)
- [ ] Testimonios propios documentados

### Semana 8: Empaquetado producción
- [ ] Versión `0.2.0` del plugin con tag git
- [ ] README actualizado con casos de uso reales y métricas
- [ ] Listing en marketplace (privado por ahora)
- [ ] **Hito**: freelancers-mx en estado "producción para uso personal y posibles primeros clientes piloto"

---

## Vertical 2: agencia-marketing-mx — semanas 9-16

### Semana 9-10: Dogfooding + calibración
- [ ] Si tienes clientes de agencia: usar `/agencia:reporte` para el cierre mensual real
- [ ] Si no: simular con datos públicos de cuentas demo de Meta Ads Manager
- [ ] Calibrar descriptions con evals

### Semana 11-12: Validación con CM senior
- [ ] Conseguir community manager senior con cuenta WhatsApp Business activa (~$2-5k MXN por 4-6 horas de consulta)
- [ ] Validar templates `whatsapp-business-mx`
- [ ] Probar 3-5 templates en aprobación Meta real
- [ ] Validar tasas y políticas vigentes Meta 2026
- [ ] Ajustar

### Semana 13-14: Validación con Meta Ads expert
- [ ] Conseguir performance marketer senior (~$3-6k MXN por revisión)
- [ ] Validar checklist de `meta-ads-optimization` contra prácticas 2026
- [ ] Probar reportes con clientes reales (con permiso)

### Semana 15-16: Refinamiento + empaque
- [ ] Score 7-8/9 por skill
- [ ] Versión 0.2.0
- [ ] **Hito**: agencia-marketing-mx listo para vender implementación a 1 cliente piloto

---

## Vertical 3: talleres-mx — semanas 17-24

### Semana 17-18: Conseguir partner del sector
- [ ] Identificar 5-10 dueños de taller mecánico tech-savvy (Monterrey/CDMX/GDL)
- [ ] Contactar con propuesta: "te automatizo el 60% de tu admin a cambio de tu input 4 hrs/semana"
- [ ] Cerrar uno como partner

### Semana 19-20: Dogfooding con partner real
- [ ] Instalar plugin en operación del partner
- [ ] Operar 2-3 semanas en paralelo a su flujo actual
- [ ] Capturar feedback diario
- [ ] Ajustar skills según operación real

### Semana 21: Validación legal PROFECO
- [ ] Conseguir abogado defensa del consumidor (~$5-10k MXN)
- [ ] Validar:
  - Certificado de garantía
  - Política de auto detenido
  - Carta de requerimiento legal
  - Procedimiento de reclamo
- [ ] Aplicar correcciones

### Semana 22-23: Calibración + casos edge
- [ ] Correr evals
- [ ] Documentar casos reales del partner (anonimizados)
- [ ] Score 7-8/9

### Semana 24: Empaque
- [ ] Versión 0.2.0
- [ ] **Hito**: talleres-mx listo con partner validado y 1 implementación real funcionando

---

## Vertical 4: colegios-mx — semanas 25-36

### Semanas 25-27: Partner indispensable + setup
- [ ] **Sin partner del sector NO arrancar este vertical**
- [ ] Conseguir directora administrativa de colegio K-12 (50-500 alumnos)
- [ ] Acuerdo de prueba: 8-12 semanas a cambio de implementación gratuita

### Semanas 28-30: Validación regulatoria intensa
- [ ] Conseguir contador especializado en colegios (~$5-15k MXN)
- [ ] Validar CFDI con complemento InsEduc contra timbrado real
- [ ] Validar topes deducción colegiaturas 2026
- [ ] Validar formato de constancias SEP para el estado del partner
- [ ] Validar política de cobranza con abogado educativo (~$3-8k MXN)

### Semanas 31-33: Dogfooding con partner real
- [ ] Operar paralelo a sus sistemas actuales 6 semanas
- [ ] Probar emisión real de CFDIs a 10-20 padres (con su autorización)
- [ ] Probar comunicación masiva real con padres
- [ ] Capturar feedback de directora + de padres mismos

### Semanas 34-35: Refinamiento + casos edge
- [ ] Documentar 15-20 casos reales del ciclo escolar
- [ ] Ajustar skills

### Semana 36: Empaque
- [ ] Versión 0.2.0
- [ ] **Hito**: colegios-mx listo con caso de referencia validado

---

## Métricas de éxito por hito

Cada vertical debe alcanzar al cierre de su ciclo:

1. **Score honesto promedio ≥ 7.5/9** según `docs/estado-real.md`
2. **Evals con accuracy ≥ 85%** en triggering
3. **Al menos 5 casos reales documentados** (anonimizados) operando
4. **Validación experta firmada** por al menos un experto del sector
5. **Integración real con al menos 2 servicios externos** (PAC, WA, pasarela de pago)
6. **Sin tickets críticos en backlog**
7. **README con cifras de valor entregado** (horas ahorradas, cartera reducida, etc.)

---

## Inversión estimada

### Honorarios de expertos (por los 4 verticales)

| Vertical | Expertos requeridos | Inversión total estimada |
|---|---|---|
| freelancers-mx | Contador (semana 3), Abogado mercantilista (semana 5) | $8k-20k MXN |
| agencia-marketing-mx | CM senior, Performance marketer | $5k-11k MXN |
| talleres-mx | Abogado defensa consumidor, Partner (revenue share) | $5k-10k MXN + 30-40% rev share |
| colegios-mx | Contador especializado, Abogado educativo, Partner | $8k-23k MXN + revenue share |

**Total efectivo**: $26k-64k MXN en consultorías.

### Tu tiempo

- 10-15 horas/semana × 36 semanas = **360-540 horas**.
- A tu tarifa horaria implícita: tiempo significativo pero recuperable con primeros clientes pagos.

### Servicios SaaS (sandbox y subscriptions)

| Servicio | Costo aproximado |
|---|---|
| Facturama sandbox | Gratuito |
| Meta Business Manager + WhatsApp Business sandbox | Gratuito |
| Gupshup/Twilio cuenta WA con saldo prueba | $20-50 USD/mes |
| Stripe / Mercado Pago sandbox | Gratuito |
| Dominio + hosting marketplace privado | $20-50 USD/mes |

**Total mensual**: ~$50-100 USD = ~$1k-2k MXN/mes.

---

## Cuándo ofrecer el primer cliente externo pagado

**No antes** de los siguientes 3 criterios concurrentes:

1. El vertical alcanzó score ≥ 7.5/9 en estado-real.md
2. Tienes 1 partner del sector validándolo
3. Tienes 1 caso de éxito propio (dogfooding) o del partner

**Pricing sugerido para primer cliente piloto** (descuento por riesgo de early adopter):
- Implementación: $30k-60k MXN one-time
- Retainer: $8k-15k MXN/mes
- Acuerdo de caso de éxito documentable (con anonimato si pide)

**Pricing escala una vez con 2-3 casos de éxito**:
- Implementación: $60k-150k MXN
- Retainer: $15k-35k MXN/mes

---

## Riesgo de no seguir este plan

Si saltas pasos (especialmente el de validación experta):
- Riesgo legal con cliente (multa SAT, queja PROFECO, demanda)
- Riesgo reputacional (un caso público de error apaga el negocio)
- Riesgo de churn alto (cliente piloto descontento te enrarece referencias)

El scaffolding rápido es **engañoso** porque se siente como progreso. El verdadero progreso es la calidad cuantificable contra el checklist de 9 puntos.
