# Preguntas frecuentes

**Propósito**: respuestas rápidas a preguntas comunes.

**Audiencia**: usuarios y desarrolladores.

---

## Generales

### ¿Qué es plugins-mx exactamente?

Un monorepo ([github.com/elimorals/Skills_MX](https://github.com/elimorals/Skills_MX)) con 40 plugins de Claude Code, 342 skills y 83 MCP servers (417 tools) para operar una PyME o profesión en México: CFDI 4.0, SAT, nómina e IMSS, pagos, marketplaces y trámites estatales y municipales. Cifras vigentes en el [README raíz](../../README.md).

### ¿Necesito ser desarrollador para usarlo?

Para **operar**: no. Necesitas Claude Code y [`uv`](https://docs.astral.sh/uv/), y seguir [guia-instalacion.md](../guides/guia-instalacion.md).

Para **extender** (crear nuevos skills): sí, conocimiento básico de Markdown + YAML + opcional Python.

### ¿Cuánto cuesta?

El monorepo en sí: gratis, con licencia Apache-2.0.

Costos asociados:
- Claude Code: según tu plan Anthropic
- Servicios externos cuando los actives: ver [integracion-pac.md](../integrations/integracion-pac.md), [integracion-whatsapp.md](../integrations/integracion-whatsapp.md), [integracion-pagos.md](../integrations/integracion-pagos.md)

### ¿Funciona offline?

No. Claude necesita internet, y los MCPs se descargan con `uv` la primera vez y consultan portales y APIs en línea. Los cálculos normativos locales (p. ej. ISN, ISH, NOM-037) no dependen de un servicio externo.

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

Sí. Las skills se pueden subir sueltas a Claude.ai (pierden la parte que depende de un MCP). Ver [guia-instalacion.md](../guides/guia-instalacion.md), sección 5.

### ¿Por qué hay 40 plugins y no uno solo?

Modularidad. Un freelancer no necesita las constancias académicas SEP de un colegio. Cargar solo el vertical que usas reduce contexto y mejora rendimiento.

### ¿Puedo cargar varios plugins simultáneamente?

Sí. Instala cada uno con `/plugin install <plugin> --marketplace elimorals/Skills_MX`. Si tienes operaciones en varios verticales (eres consultor que también tiene escuela), tiene sentido.

---

## Sobre el contenido

### ¿Los datos fiscales están actualizados a 2026?

**NO necesariamente**. Mucho contenido viene de mi training data. Cada skill que cita datos sensibles tiene una sección `⚠ Datos que requieren verificación vigente` listando lo que hay que validar.

El estado de cada MCP (qué consulta en real y qué se validó en vivo) está en [`mcp-servers/CATALOGO.md`](../../mcp-servers/CATALOGO.md).

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

Sí, con credenciales reales del PAC y un MCP de envío de WhatsApp propio (el repo no trae uno; ver [integracion-whatsapp.md](../integrations/integracion-whatsapp.md)). El flujo: cliente paga → webhook (`webhooks/`) → CFDI → WhatsApp al cliente con el enlace de descarga.

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

Ver [guia-desarrollo.md](../guides/guia-desarrollo.md).

### ¿Cómo agrego un vertical nuevo?

Ver [guia-desarrollo.md](../guides/guia-desarrollo.md) sección "Agregar un vertical nuevo".

### ¿Puedo contribuir al monorepo?

Sí, el repo es público: PRs bienvenidos. El CI corre tests, evals golden, lint de skills y validación del marketplace en cada PR.

### ¿Hay tests automatizados?

Sí: 1,900 tests de los MCPs (sin red), 285 evals de triggering, casos golden de cálculo fiscal y fixtures de regresión. Corren en CI en cada PR. Los tests `@pytest.mark.live` contra portales reales corren con `PLUGINS_MX_LIVE=1`.

---

## Sobre el negocio

### ¿Puedo vender implementación con este monorepo?

La licencia Apache-2.0 lo permite. Antes de exponerlo a clientes, las skills fiscales y legales necesitan validación de un contador o abogado, y los MCPs que uses deben estar en estado real validado ([`CATALOGO.md`](../../mcp-servers/CATALOGO.md)). Sin eso hay riesgo regulatorio y reputacional.

### ¿Necesito permiso de Anthropic para distribuir?

Revisa términos vigentes de Claude Code y marketplace. Plugins genéricos típicamente OK; marca/branding requiere revisar.

### ¿Otros pueden clonar mi negocio?

Sí, los plugins son replicables. Tu moat real:
1. Calidad de afinación (`_shared/` validado con horas-hombre)
2. Partners del sector
3. Caso de éxito documentado
4. Velocidad de iteración

---

## Sobre roadmap

### ¿Cuándo habrá más verticales?

Ya hay 40 verticales (lista en el [README raíz](../../README.md#plugins-verticales)). Lo que sigue está en [roadmap.md](../roadmap.md).

### ¿Habrá versión SaaS?

Posible pero no priorizado. El modelo Claude Code permite uso individual; SaaS requeriría infra propia.

### ¿Apoyarán otros idiomas/países?

LATAM primero (Colombia, Argentina, Chile, Perú). Cada país tiene su propio CFDI/equivalente y regulación. Out of scope inicial.

---

## Soporte

### ¿Hay comunidad/chat?

GitHub Issues en [elimorals/Skills_MX](https://github.com/elimorals/Skills_MX/issues).

### ¿Quién mantiene esto?

Elías Rashid Morales Mendoza (`elimoralsmendox@gmail.com`). Más detalles en `.claude-plugin/marketplace.json` o en el `plugin.json` de cada plugin.

---

## Ver también

- [INDEX.md](../INDEX.md) — índice general
- [troubleshooting.md](../operational/troubleshooting.md) — problemas técnicos comunes
- [roadmap.md](../roadmap.md) — qué viene a futuro
