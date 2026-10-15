# Índice de documentación — Skills_MX (plugins-mx)

La fuente de verdad es el [README raíz](../README.md). El estado de cada MCP está en [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md), que se genera desde la sección "Estado real" de cada `mcp-servers/mp_*/README.md`. Si un documento de esta carpeta contradice a esos dos, mandan ellos.

Ruta sugerida si llegas nuevo: README raíz → [arquitectura](architecture/arquitectura.md) → [guía de instalación](guides/guia-instalacion.md) → guía del vertical que te interese.

## Estado y planeación (vigente)

| Documento | Propósito |
|---|---|
| [`../mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md) | Estado y tools de los 83 MCPs (generado) |
| [plan-mock-a-real.md](plan-mock-a-real.md) | Plan y grupos de la migración de mock a datos reales (oleadas 1-3) |
| [roadmap.md](roadmap.md) | Visión a 12 meses |

## Arquitectura y decisiones

| Documento | Propósito |
|---|---|
| [architecture/arquitectura.md](architecture/arquitectura.md) | Modelo `_shared/` + verticales, MCPs, workflows y hooks |
| [architecture/seguridad.md](architecture/seguridad.md) | Credenciales, e.firma, datos personales, repo público |
| [architecture/versionado.md](architecture/versionado.md) | Semver y tags por plugin |
| [architecture/apis-oficiales-mx.md](architecture/apis-oficiales-mx.md) | Inventario de APIs y portales oficiales de México |
| [architecture/PATRONES-MCP-MUNICIPAL.md](architecture/PATRONES-MCP-MUNICIPAL.md) | Stacks de portales municipales y cómo agregar un municipio |
| [adrs/](adrs/README.md) | Decisiones de arquitectura (ADR 001-008) |

## Guías

| Documento | Propósito |
|---|---|
| [guides/guia-instalacion.md](guides/guia-instalacion.md) | Instalar plugins desde el marketplace y MCPs sueltos |
| [guides/guia-desarrollo.md](guides/guia-desarrollo.md) | Contribuir: skills, verticales, MCPs, pruebas |
| [guides/guia-vertical-freelancers.md](guides/guia-vertical-freelancers.md) | Casos de uso de `freelancers-mx` |
| [guides/guia-vertical-agencia.md](guides/guia-vertical-agencia.md) | Casos de uso de `agencia-marketing-mx` |
| [guides/guia-vertical-colegios.md](guides/guia-vertical-colegios.md) | Casos de uso de `colegios-mx` |
| [guides/guia-vertical-talleres.md](guides/guia-vertical-talleres.md) | Casos de uso de `talleres-mx` |

## Integraciones

| Documento | Propósito |
|---|---|
| [integrations/integracion-pac.md](integrations/integracion-pac.md) | PAC para CFDI (Facturama vía `mp_facturama_extendido`) |
| [integrations/integracion-pagos.md](integrations/integracion-pagos.md) | Mercado Pago, Conekta, Stripe y otras pasarelas |
| [integrations/integracion-whatsapp.md](integrations/integracion-whatsapp.md) | WhatsApp Business (Meta Cloud API y BSPs) |

## Operación

| Documento | Propósito |
|---|---|
| [operational/flujos-operativos.md](operational/flujos-operativos.md) | Workflows típicos entre verticales |
| [operational/hooks-setup.md](operational/hooks-setup.md) | Instalar los hooks de Claude Code |
| [operational/compliance-checklist.md](operational/compliance-checklist.md) | Checklist de cumplimiento por sector |
| [operational/metricas.md](operational/metricas.md) | KPIs por vertical |
| [operational/troubleshooting.md](operational/troubleshooting.md) | Problemas comunes |
| [`../scripts/crons/README.md`](../scripts/crons/README.md) | Crons y launchd |
| [`../webhooks/README.md`](../webhooks/README.md) | Receptor de webhooks (FastAPI) |

## Referencia

| Documento | Propósito |
|---|---|
| [reference/faq.md](reference/faq.md) | Preguntas frecuentes |
| [reference/glosario-fiscal-mx.md](reference/glosario-fiscal-mx.md) | Términos SAT, CFDI, regímenes, retenciones |
| [reference/glosario-tecnico.md](reference/glosario-tecnico.md) | Plugin, skill, agente, MCP, hook, workflow |

## Histórico (no vigente)

Estos documentos registran cómo se llegó al estado actual. Cada uno empieza con un aviso: sus cifras y el diseño mock-first no son vigentes.

| Carpeta | Contenido |
|---|---|
| [historial/](historial/) | Bitácora de sprints de junio 2026, `STATUS-2026-06.md`, `estado-real-2026-06.md` (auditoría de scores por skill) |
| [sprints/](sprints/) | Resúmenes de sprints A-H |
| [audits/](audits/) | Auditorías y validaciones de portales de junio 2026 |
| [discoveries/](discoveries/) | Discovery de portales, cobertura nacional, trámites no implementados |
| [specs/](specs/README.md) | Specs de diseño de junio 2026 (webhooks, Playwright, verticales) |
| [consultorias/](consultorias/) | Briefs para consultas con contador y abogado |
| [dogfooding/](dogfooding/) | Prueba de `pf-anual-mx` con un caso real |
| [plan-afinacion.md](plan-afinacion.md) | Plan de 36 semanas de junio 2026 |

## Recursos fuera de `docs/`

| Directorio | Contenido |
|---|---|
| `../scripts/` | Sync de `_shared/`, lint, generadores (`generar-estado-mcps.py`, `generar-marketplace.py`, `mcp-config-portable.py`), evals golden, crons, hooks |
| `../schemas/` | JSON Schemas de salida |
| `../tests/fixtures/` | Casos de regresión por skill |
| `../evals/` | Triggering por skill, golden deterministas y promptfoo |
| `../_shared/` | 6 skills base (fuente de verdad) |

---

**Última actualización del índice**: 2026-10-14.
