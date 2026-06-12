# `docs/specs/` — Specs detallados

Specs detallados para items **novedosos** del proyecto (sin patrón previo en el repo).

## Cuándo crear un spec

Crea un spec ANTES de codificar si:
- ✅ Es la primera implementación de su tipo (primer webhook receiver, primer hook runtime, primer Playwright real)
- ✅ Combina múltiples MCPs/skills de formas no probadas (ej. workflow que cruza 5+ MCPs)
- ✅ Tiene auth o compliance compleja (e.firma, autorización Buró, OAuth + AWS Sig)
- ✅ Vertical con score >= 9.0 (riesgo de mal scope alto)
- ✅ Esfuerzo estimado > 100h

NO crees spec para:
- ❌ Otro MCP siguiendo patrón conocido (otro Tier B REST = clonar mp_conekta)
- ❌ Otro vertical clonable (otro plugin = clonar talleres-mx)
- ❌ Otro workflow variante (clonar workflow-cobranza-multinivel)
- ❌ Skill suelto en vertical existente

## Estructura de cada spec

Usa `_template.md` como base. Cada spec debe responder:

1. **Propósito** — 1 párrafo, qué resuelve
2. **Contexto** — qué existe ya, por qué este es novedoso
3. **Inputs / outputs / schemas** — contratos exactos
4. **Tools / endpoints / triggers** — qué expone
5. **Casos edge** — mínimo 5
6. **Dependencias** — MCPs, skills, librerías
7. **Criterios de aceptación** — qué tests deben pasar
8. **Esfuerzo estimado** — rango con confianza
9. **Riesgos + mitigaciones**
10. **Decisiones pendientes** — preguntas abiertas

## Specs vivos

| # | Spec | Estado | Item del gap |
|---|---|---|---|
| 01 | [webhook-receiver](01-webhook-receiver.md) | ✅ DRAFT | 12 webhook handlers |
| 02 | [sat-portal-playwright-real](02-sat-portal-playwright-real.md) | ✅ DRAFT | MCP crítico |
| 03 | [bancos-mx-playwright-real](03-bancos-mx-playwright-real.md) | ✅ DRAFT | MCP crítico |
| 04 | [hooks-runtime-claude-code](04-hooks-runtime-claude-code.md) | ✅ DRAFT | 13 hooks |
| 05 | [vertical-pf-anual-mx](05-vertical-pf-anual-mx.md) | ✅ DRAFT | Vertical score 9.5 |
| 06 | [vertical-arrendador-residencial-mx](06-vertical-arrendador-residencial-mx.md) | ✅ DRAFT | Vertical score 9.3 |
| 07 | [vertical-telemedicina-mx](07-vertical-telemedicina-mx.md) | ✅ DRAFT | Área no cubierta — telemedicina + COFEPRIS + NOM-004 |
| 08 | [vertical-nomina-pymes-mx](08-vertical-nomina-pymes-mx.md) | ✅ DRAFT | Área no cubierta — CFDI Nómina 4.0 + IMSS-SUA-IDSE |
| 09 | [vertical-cripto-fiscal-mx](09-vertical-cripto-fiscal-mx.md) | ✅ DRAFT | Área no cubierta — cripto + CARF 2026 |
| 10 | [vertical-educacion-particular-b2c-mx](10-vertical-educacion-particular-b2c-mx.md) | ✅ DRAFT | Área no cubierta — cursos online + CFDI D10/G03 |
| 11 | [vertical-donatarias-ongs-mx](11-vertical-donatarias-ongs-mx.md) | ✅ DRAFT | Área no cubierta — donatarias autorizadas + transparencia |
| 12 | [vertical-importadores-mx](12-vertical-importadores-mx.md) | ✅ DRAFT | Área no cubierta — pedimentos + IVA + IMMEX |
| 13 | [vertical-sucesion-empresa-familiar-mx](13-vertical-sucesion-empresa-familiar-mx.md) | ✅ DRAFT | Área no cubierta — sucesión + donaciones + protocolo familiar |
| 14 | [vertical-crowdfunding-itf-mx](14-vertical-crowdfunding-itf-mx.md) | ✅ DRAFT | Área no cubierta — Ley Fintech + IFC + P2P |
| 15 | [vertical-energia-solar-pyme-mx](15-vertical-energia-solar-pyme-mx.md) | ✅ DRAFT | Área no cubierta — CFE bidireccional + net metering + GDMTH |

## Workflow recomendado

```
1. Crear spec → DRAFT
2. Revisar con stakeholder (opcional pero recomendado para verticales)
3. Codificar siguiendo el spec
4. Si descubres cambios necesarios en el spec → actualizarlo (no solo en el código)
5. Marcar spec como IMPLEMENTED + linkear PR/commit
6. Marcar el item en docs/STATUS.md como [x]
```

## Convenciones

- Numerar con prefijo `NN-` para orden
- Kebab-case del nombre del módulo
- Estado en el frontmatter: `DRAFT | IN_PROGRESS | IMPLEMENTED | DEPRECATED`
- Linkear desde STATUS.md
