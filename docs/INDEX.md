# Índice de documentación — plugins-mx

Mapa completo de la documentación del monorepo. Si llegas nuevo, empieza por **INDEX → README raíz → arquitectura.md → guía del vertical que te interesa**.

## Documentos de arquitectura y diseño

| Documento | Propósito |
|---|---|
| [arquitectura.md](arquitectura.md) | Modelo `_shared/` + verticales, convenciones, criterios producción-grade |
| [versionado.md](versionado.md) | Política de versiones semver + git tags por plugin |
| [seguridad.md](seguridad.md) | Manejo de credenciales, secrets, datos personales en tránsito |

## Documentos de estado y planeación

| Documento | Propósito |
|---|---|
| [estado-real.md](estado-real.md) | Auditoría honesta: score 4.7/9 promedio, riesgo por skill |
| [gap-analysis-2026-06.md](gap-analysis-2026-06.md) | Gap vs planeación original: 6 MCPs, 15 verticales, 13 hooks, 28 crons, 12 webhooks faltantes (~7,780-10,740h) |
| [STATUS.md](STATUS.md) | **Checklist vivo del proyecto** — actualizar cada sesión al cerrar un módulo |
| [specs/README.md](specs/README.md) | Specs detallados de items novedosos (webhook receiver, Playwright real, verticales TOP) |
| [plan-afinacion.md](plan-afinacion.md) | Roadmap 36 semanas para llevar a producción-grade |
| [roadmap.md](roadmap.md) | Visión a 12 meses: nuevos verticales, integraciones, ecosistema |

## Guías de uso e instalación

| Documento | Propósito |
|---|---|
| [guia-instalacion.md](guia-instalacion.md) | Cómo instalar plugins en Claude Code y skills standalone |
| [guia-desarrollo.md](guia-desarrollo.md) | Cómo contribuir, crear skills nuevos, agregar verticales |
| [troubleshooting.md](troubleshooting.md) | Problemas comunes y soluciones |
| [faq.md](faq.md) | Preguntas frecuentes |

## Guías por vertical

| Documento | Propósito |
|---|---|
| [guia-vertical-freelancers.md](guia-vertical-freelancers.md) | Casos de uso, flujos, métricas para freelancers-mx |
| [guia-vertical-agencia.md](guia-vertical-agencia.md) | Casos de uso, flujos, métricas para agencia-marketing-mx |
| [guia-vertical-colegios.md](guia-vertical-colegios.md) | Casos de uso, flujos, métricas para colegios-mx |
| [guia-vertical-talleres.md](guia-vertical-talleres.md) | Casos de uso, flujos, métricas para talleres-mx |
| [flujos-operativos.md](flujos-operativos.md) | Workflows típicos cross-vertical |

## Integraciones

| Documento | Propósito |
|---|---|
| [integracion-pac.md](integracion-pac.md) | Facturama, SW Sapien, Solución Factible — cómo conectar |
| [integracion-whatsapp.md](integracion-whatsapp.md) | Gupshup, Twilio, Meta Cloud — cómo conectar |
| [integracion-pagos.md](integracion-pagos.md) | Stripe, Mercado Pago, Conekta — cómo conectar |

## Compliance y métricas

| Documento | Propósito |
|---|---|
| [compliance-checklist.md](compliance-checklist.md) | Checklist por sector: salud, educación, ecommerce, servicios |
| [metricas.md](metricas.md) | KPIs por vertical, valor entregado al cliente |

## Glosarios

| Documento | Propósito |
|---|---|
| [glosario-fiscal-mx.md](glosario-fiscal-mx.md) | Términos SAT, CFDI, regímenes, retenciones, etc. |
| [glosario-tecnico.md](glosario-tecnico.md) | Plugin, skill, agent, MCP, frontmatter, etc. |

## Recursos técnicos adicionales (fuera de `docs/`)

| Directorio | Contenido |
|---|---|
| `../scripts/` | Scripts ejecutables Python (`validar_rfc.py`, `format_mxn.py`, `calcular_iva_retenciones.py`, `mock_pac.py`) + shell tooling (`sync-shared.sh`, `lint-skills.sh`, `new-skill.sh`, `version-bump.sh`, `run-fixtures.sh`) |
| `../schemas/` | JSON Schemas para validación de outputs estructurados |
| `../tests/fixtures/` | Fixtures de regresión por skill (input + expected output) |
| `../evals/` | Calibration prompts por skill (should-trigger + should-not-trigger) |
| `../_shared/*/references/` | References detalladas: catálogos SAT, complementos CFDI, matriz retenciones, palabras inconvenientes, templates WA aprobables, tono MX, Banxico, ARCO, regímenes |
| `../<plugin>/agents/` | Subagents en core-mexico (`validador-cfdi-batch`), freelancers-mx (`auditor-fiscal-mensual`, `revisor-cobranza-cartera`), talleres-mx (`defensor-profeco`) |

## Convención de navegación

Cada documento empieza con:
- **Propósito**: para qué sirve
- **Audiencia**: quién debe leerlo
- **Pre-lectura**: documentos que conviene leer antes

Documentos relacionados aparecen al final como "Ver también".

---

**Última actualización del índice**: 2026-06-11.
