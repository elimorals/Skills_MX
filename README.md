# Plugins MX — Monorepo de Skills, Agentes y Plugins para México y LATAM

Monorepo de **plugins de Claude Code** y **skills standalone** para operación diaria de PyMEs y profesionistas en México y LATAM.

## Filosofía

- **Capa `_shared/`**: skills base reutilizables (CFDI 4.0, IVA, retenciones, RFC, WhatsApp Business, LFPDPPP, formato MXN). Se sincronizan a cada plugin vertical antes de release.
- **Plugins verticales**: paquetes autocontenidos por industria (freelancers, ecommerce, colegios, talleres, etc.) que combinan `_shared/` + skills específicos + commands + MCPs + hooks.
- **Skills standalone**: misma capacidad empaquetada como skills portables (instalables vía `skillkit` o subida directa a Claude.ai).

## Estructura

```
plugins-mx/
├── _shared/                  Skills base reutilizables (fuente de verdad)
│   ├── cfdi-emision/
│   ├── iva-retenciones-mx/
│   ├── rfc-validacion/
│   ├── whatsapp-business-mx/
│   ├── compliance-lfpdppp/
│   └── mxn-formato/
├── core-mexico/              Plugin base (instalación obligatoria)
│   ├── .claude-plugin/plugin.json
│   ├── skills/               Sync de _shared/ vía sync-shared.sh
│   └── commands/
├── freelancers-mx/           Vertical (próximamente)
├── colegios-mx/              Vertical (próximamente)
├── talleres-mx/              Vertical (próximamente)
├── scripts/
│   ├── sync-shared.sh        Copia _shared/ a cada plugin pre-release
│   └── lint-skills.sh        Valida YAML frontmatter de cada SKILL.md
├── marketplace.json          Manifiesto del marketplace privado
└── docs/
    └── arquitectura.md
```

## Distribución

**Como plugins de Claude Code:**
```bash
/plugin marketplace add elias/plugins-mx
/plugin install freelancers-mx
```

**Como skills standalone:**
```bash
skillkit install cfdi-emision   # desde _shared/
```

## Estado actual

| Componente | Estado |
|---|---|
| `_shared/` | 6 skills compartidos con references/ bundleados |
| `core-mexico` | Plugin base con 3 commands |
| `freelancers-mx` | 5 skills propios + 5 commands |
| `agencia-marketing-mx` | 5 skills propios + 4 commands |
| `colegios-mx` | 4 skills propios + 4 commands |
| `talleres-mx` | 4 skills propios + 4 commands |
| **Total skills** | **54 (lint-passing)** |
| **Verticales pendientes** | 15+ (ver `marketplace.json > comingSoon`) |

## Convenciones

- `description:` del frontmatter siempre en español MX con sinónimos en inglés para triggering robusto
- Skills sub-500 líneas; referencias largas a `references/`
- Toda integración (PAC, WhatsApp, banca) abstraída detrás de interfaces mockeables
- Cumplimiento LFPDPPP por defecto en cualquier skill que toque datos personales
