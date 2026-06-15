# Preguntas frecuentes

**Propósito**: respuestas rápidas a preguntas comunes.

**Audiencia**: usuarios y desarrolladores.

---

## Generales

### ¿Qué es plugins-mx exactamente?

Un monorepo de plugins de Claude Code y skills standalone para automatizar operación diaria de PyMEs y profesionistas en México: CFDI, cobranza, WhatsApp Business, compliance, etc.

### ¿Necesito ser desarrollador para usarlo?

Para **operar**: no. Solo necesitas Claude Code instalado y seguir [guia-instalacion.md](guia-instalacion.md).

Para **extender** (crear nuevos skills): sí, conocimiento básico de Markdown + YAML + opcional Python.

### ¿Cuánto cuesta?

El monorepo en sí: gratis (open source / privado según se decida).

Costos asociados:
- Claude Code: según tu plan Anthropic
- Servicios externos cuando los actives: ver [integracion-pac.md](integracion-pac.md), [integracion-whatsapp.md](integracion-whatsapp.md), [integracion-pagos.md](integracion-pagos.md)

### ¿Funciona offline?

Parcial. Los skills se cargan localmente y Claude opera contra su API (necesita internet para LLM). Los MCP servers desactivados no requieren internet adicional.

### ¿Mis datos se mandan a Anthropic?

Los datos que escribes en la sesión sí van al modelo (es como funciona Claude). Anthropic tiene política de no entrenar con datos de Claude Code por default. Revisa términos vigentes.

### ¿Anthropic conserva mis datos?

Política sujeta a cambios. Revisa términos. Para datos altamente sensibles (clínica, banca), considera implementación con compliance especial.

---

## Sobre plugins vs skills

### ¿Cuál es la diferencia entre plugin y skill?

- **Plugin**: paquete completo con `plugin.json` + skills + commands + opcional MCP + hooks. Distribuible vía marketplace.
- **Skill**: capacidad individual (`SKILL.md` + frontmatter). Puede vivir dentro de un plugin o standalone.

### ¿Puedo usar solo un skill sin todo el plugin?

Sí. Skills son standalone vía `skillkit install` o subida directa a Claude.ai. Ver [guia-instalacion.md](guia-instalacion.md) opción 2.

### ¿Por qué hay 5 plugins y no uno solo?

Modularidad. Un freelancer no necesita las constancias académicas SEP de un colegio. Cargar solo el vertical que usas reduce contexto y mejora rendimiento.

### ¿Puedo cargar varios plugins simultáneamente?

Sí. `claude --plugin-dir A --plugin-dir B`. Si tienes operaciones en varios verticales (eres consultor que también tiene escuela), tiene sentido.

---

## Sobre el contenido

### ¿Los datos fiscales están actualizados a 2026?

**NO necesariamente**. Mucho contenido viene de mi training data. Cada skill que cita datos sensibles tiene una sección `⚠ Datos que requieren verificación vigente` listando lo que hay que validar.

Ver [estado-real.md](estado-real.md) para detalle.

### ¿Puedo confiar en los cálculos fiscales del plugin?

**No para producción real sin validación de contador.** Para dogfooding y aprendizaje, sí. Para presentar declaraciones reales al SAT, no.

Especialmente riesgoso: `freelance-tax-mx` y `cfdi-colegiaturas-deducibles`.

### ¿Los contratos generados son legalmente válidos?

Son **borradores razonables**, no contratos blindados por abogado mexicano. Antes de usar para contrato sustancial, validar con abogado mercantilista.

### ¿Los templates WhatsApp pasarán aprobación Meta?

Probable pero no garantizado. Meta cambia políticas. Validar en sandbox antes de producción.

---

## Sobre uso diario

### ¿Cuánto tiempo me toma onboardear un cliente con el plugin?

`/freelancers:onboarding`: 5-10 minutos vs 20-40 manuales.

### ¿Puedo automatizar el envío de CFDIs por WhatsApp?

Sí, si activas tanto PAC como WhatsApp Business reales. El flujo: cliente paga → webhook → CFDI → WA al cliente con link de descarga.

### ¿Cómo manejo cliente que se atrasa en pagos?

`/freelancers:cobranza <cliente>`. El skill `cobranza-seguimiento` recomienda la etapa apropiada según mora.

### ¿Y si el cliente quiere descuento después de cotizar?

Iterar la cotización: `/freelancers:cotizar <cliente>` con scope ajustado. Genera nueva versión registrada.

---

## Sobre privacidad y compliance

### ¿Cumple LFPDPPP?

El plugin **provee herramientas** para cumplir (aviso de privacidad, ARCO, etc.). El **cumplimiento real es responsabilidad del usuario final**.

### ¿Y si recibo solicitud ARCO?

Usar el skill `compliance-lfpdppp` que tiene procedimiento documentado. Plazo legal 20 días hábiles.

### ¿Mis clientes saben que uso este plugin?

No tienen por qué. Ellos solo reciben los outputs (CFDI, mensaje, contrato). Pero el aviso de privacidad debe declarar las herramientas/proveedores que tocan sus datos (PAC, WhatsApp Business, etc.).

---

## Sobre desarrollo y contribución

### ¿Cómo agrego un skill nuevo?

Ver [guia-desarrollo.md](guia-desarrollo.md).

### ¿Cómo agrego un vertical nuevo?

Ver [guia-desarrollo.md](guia-desarrollo.md) sección "Agregar un vertical nuevo".

### ¿Puedo contribuir al monorepo?

Depende de cómo lo distribuyas. Si es público: PRs bienvenidos. Si es privado: solo el dueño/equipo.

### ¿Hay tests automatizados?

Sí en formato fixtures (regression tests) + evals (triggering tests). Ver `tests/` y `evals/`. Ejecución todavía manual.

---

## Sobre el negocio

### ¿Puedo vender implementación con este monorepo?

Una vez que un vertical alcance score 7-8/9 según [estado-real.md](estado-real.md). Antes: riesgo regulatorio + reputacional.

### ¿Cuánto cobro por implementación?

Sugerido (ver [plan-afinacion.md](plan-afinacion.md)):
- Cliente piloto early adopter: $30k-60k MXN one-time + $8k-15k MXN/mes retainer
- Cliente con 2-3 casos de éxito previos: $60k-150k MXN + $15k-35k MXN/mes

### ¿Necesito permiso de Anthropic para distribuir?

Revisa términos vigentes de Claude Code y marketplace. Plugins genéricos típicamente OK; marca/branding requiere revisar.

### ¿Otros pueden clonar mi negocio?

Sí, los plugins son replicables. Tu moat real:
1. Calidad de afinación (`_shared/` validado con horas-hombre)
2. Partners del sector
3. Caso de éxito documentado
4. Velocidad de iteración

Ver [estado-real.md](estado-real.md).

---

## Sobre roadmap

### ¿Cuándo habrá más verticales?

Ver [roadmap.md](roadmap.md). Próximos candidatos por demanda: salon-mx, veterinaria-mx, wedding-mx, ecommerce-mx, restaurante-mx.

### ¿Habrá versión SaaS?

Posible pero no priorizado. El modelo Claude Code permite uso individual; SaaS requeriría infra propia.

### ¿Apoyarán otros idiomas/países?

LATAM primero (Colombia, Argentina, Chile, Perú). Cada país tiene su propio CFDI/equivalente y regulación. Out of scope inicial.

---

## Soporte

### ¿Hay comunidad/chat?

A definir. Por ahora: GitHub Issues (si es público) o contacto directo con el maintainer.

### ¿Quién mantiene esto?

Elías Rashid Morales Mendoza (`elimoralsmendox@gmail.com`). Más detalles en `marketplace.json` o `plugin.json` de cada plugin.

---

## Ver también

- [INDEX.md](INDEX.md) — índice general
- [troubleshooting.md](troubleshooting.md) — problemas técnicos comunes
- [roadmap.md](roadmap.md) — qué viene a futuro
