# Changelog — plugins-mx (monorepo)

Cambios al monorepo como un todo: arquitectura, tooling, documentación, cambios cross-plugin.

Para cambios específicos de un plugin, ver `CHANGELOG.md` de cada plugin.

Formato: [Keep a Changelog](https://keepachangelog.com).

## [Unreleased]

### Added
- Docs: 20+ archivos de documentación profunda en `docs/`
- Schemas: JSON Schemas para outputs estructurados en `schemas/`
- Scripts ejecutables: `validar_rfc.py`, `format_mxn.py`, `calcular_iva_retenciones.py`, `mock_pac.py`
- Scripts de tooling: `new-skill.sh`, `version-bump.sh`, `run-fixtures.sh`
- References bundleados en `_shared/`: regímenes fiscales, complementos CFDI, integración SAT, ARCO, Banxico, tono MX

## [0.2.0] — 2026-06-11

### Added
- Auditoría honesta: `docs/estado-real.md` con score por skill
- Plan de afinación productiva: `docs/plan-afinacion.md`
- Banderas `⚠ Datos que requieren verificación vigente` en 7 skills críticos
- Calibration prompts ejecutables en `evals/` (8 archivos con 170+ prompts)
- Fixtures de regresión en `tests/fixtures/` (15 casos en 4 skills)

## [0.1.0] — 2026-06-11

### Added
- Scaffold inicial del monorepo
- 5 plugins: core-mexico, freelancers-mx, agencia-marketing-mx, colegios-mx, talleres-mx
- 6 skills compartidos en `_shared/`
- 18 skills propios en verticales
- 17 commands cross-plugin
- Tooling: `sync-shared.sh`, `lint-skills.sh`
- Documentación base: README, marketplace.json, arquitectura.md
- 7 references bundleados iniciales
- Git inicializado con historial limpio

[Unreleased]: ...
[0.2.0]: ...
[0.1.0]: ...
