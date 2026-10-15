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

## [0.3.0] — 2026-10-14

Cifras a esta versión: 40 plugins, 342 skills, 83 MCPs con 417 tools, 26 workflows, 17 scripts de hook (12 registrados), 12 handlers de webhook, 1,900 tests. Licencia Apache-2.0.

### Changed — oleadas 1 y 2 (PR #1)
- **MCPs de mock a real** por grupos (SAT web services y portal con e.firma, federales públicos, estatales y municipales, APIs privadas): sin fallback silencioso a datos de ejemplo. Sin credenciales responden `simulated: true`; con credenciales los errores se propagan como error tipado; `PLUGINS_MX_MOCK=1` fuerza el modo de ejemplo. Decisión en `docs/adrs/008-estado-real-sin-fallback-silencioso.md`, que reemplaza al ADR 002 (mock-first).
- **Estado real por MCP**: sección "Estado real" en cada `mcp-servers/mp_*/README.md`. `scripts/generar-estado-mcps.py` arma con ellas `mcp-servers/CATALOGO.md`, la tabla del README y los JSON del sitio (24 reales validados en vivo, 13 reales sin validar, 17 con entrega a humano, 6 sin API pública, 10 de cálculo normativo, 2 bloqueados, 11 sin verificar).
- **SAT**: login con e.firma por HTTP, CSF, opinión 32-D propia, padrón de donatarias desde el XLSX oficial, listas 69/69-B reales por defecto.
- **Cálculos normativos** corregidos contra su fuente: UMA 2026 y salario mínimo, LFT/NOM-035/NOM-037, NOM-024, umbrales LSE de interconexión solar.
- **APIs privadas** alineadas a la doc oficial (Facturama, Mercado Libre, Shopify 2026-07, Amazon SP-API); las que no tienen API pública verificable devuelven `ConfigError` con la alternativa.

### Added
- `mcp-servers/shared/portal_handoff.py`: entrega a humano unificada (URL, pasos y campos prellenados) para portales con CAPTCHA o login.
- `mcp-servers/shared/captcha_solver.py`: solver de CAPTCHA opt-in (`PLUGINS_MX_CAPTCHA_SOLVER=2captcha` + `TWOCAPTCHA_API_KEY`) en SAF CDMX, predial Puebla y Guadalajara, cédula SEP, REPUVE, adeudos Jalisco, multas EdoMex y San Pedro, CURP e INE. No evade anti-bots de red; `citas_monitor` y REPEP quedan excluidos.
- Evals de salida (casos golden deterministas) y CI de calidad de skills (sync de `_shared`, SkillSpector).
- Tests de e.firma con certificado autofirmado generado al vuelo; la e.firma de prueba del SAT se lee de `SAT_EFIRMA_PRUEBA_DIR`, fuera del repo.

### Changed — portabilidad
- Marketplace instalable: `/plugin marketplace add elimorals/Skills_MX` y `/plugin install <plugin> --marketplace elimorals/Skills_MX`. El único `marketplace.json` vive en `.claude-plugin/` y lo genera `scripts/generar-marketplace.py`.
- Los MCPs se lanzan con `uv run --no-project --with "plugins-mx-mcp-servers[extras] @ git+https://github.com/elimorals/Skills_MX@main#subdirectory=mcp-servers" python -m mp_x.server`. Sin `cwd` ni rutas locales; `scripts/mcp-config-portable.py --check` lo verifica y el CI falla si aparece una ruta de máquina local fuera de `docs/historial`, `docs/sprints`, `docs/audits` y `website/`.
- `uv` es el único requisito además de Claude Code.

### Docs
- README raíz reestructurado como fuente de verdad; bitácora de sprints de junio en `docs/historial/`.
- `docs/INDEX.md`, guías de instalación y desarrollo, arquitectura, seguridad, integraciones, FAQ, glosarios y operación actualizados al modelo sin fallback silencioso y a la instalación por marketplace.
- `STATUS.md`, `estado-real.md` y el roadmap de junio movidos a `docs/historial/` (`*-2026-06.md`); roadmap nuevo en `docs/roadmap.md`.
- Aviso de documento histórico en sprints, auditorías, discoveries, consultorías, dogfooding, specs y `plan-afinacion.md`.
- Los 40 README de plugin tienen sección "Instalación"; los README de MCPs usan el lanzador `uv` portable.

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
[0.3.0]: ...
[0.2.0]: ...
[0.1.0]: ...
