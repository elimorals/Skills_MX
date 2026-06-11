# Política de versionado

**Propósito**: cómo se versionan los plugins y skills del monorepo.

**Audiencia**: desarrolladores y mantenedores.

**Pre-lectura**: [guia-desarrollo.md](guia-desarrollo.md).

---

## Versioning semántico (semver)

Cada plugin tiene su propio `version` en `plugin.json` siguiendo [Semantic Versioning](https://semver.org).

Formato: `MAJOR.MINOR.PATCH`

### MAJOR (1.0.0)
Cambio breaking. Incrementar cuando:
- Cambias el `name:` o `description:` de un skill de forma que rompe triggering esperado
- Cambias la estructura del output de un skill (clientes consumidores esperarían el viejo)
- Renombras o eliminas un command (los scripts existentes se rompen)
- Cambias significativamente el flujo operativo (lo que el skill hace)

### MINOR (0.X.0)
Funcionalidad nueva backwards-compatible. Incrementar cuando:
- Agregas un skill nuevo
- Agregas un command nuevo
- Agregas integración con un servicio nuevo
- Agregas referencias bundleadas
- Mejoras significativas a un skill que no cambian su output

### PATCH (0.0.X)
Bugfix o mejora menor. Incrementar cuando:
- Fix de bug en un skill
- Ajuste del `description:` para mejor triggering (sin cambiar el nombre)
- Actualización de catálogos (ej. SAT publica nuevos UsoCFDI)
- Mejora de tono/redacción en templates
- Corrección de typos en SKILL.md

---

## Pre-releases

### Versión 0.x.x
Indica que el plugin está en **beta**, no se garantiza estabilidad de API.

Política para pre-1.0:
- Cambios breaking entre minors están permitidos
- Documentar en CHANGELOG.md

### Cuando llegar a 1.0.0
Cuando un plugin alcanza score ≥ 7.5/9 en [estado-real.md](estado-real.md) y ha tenido al menos 3 meses de uso real con clientes externos sin issues graves.

### Versiones alpha/beta/rc
Para releases experimentales:
- `0.5.0-alpha.1`: muy experimental
- `0.5.0-beta.1`: feature-complete pero requiere validación
- `0.5.0-rc.1`: candidato a release (release candidate)

---

## Tags git

Convención: `<plugin-name>-v<version>`.

```bash
# Después de actualizar version en plugin.json
git tag freelancers-mx-v0.2.0
git push origin freelancers-mx-v0.2.0
```

### Por qué tags por plugin (no monorepo)
Cada plugin evoluciona a su ritmo. `core-mexico` puede ir en 0.3 mientras `talleres-mx` está en 0.1. Tags por plugin permiten referenciar versión específica de cada uno.

### Tag global del monorepo (opcional)
Para releases coordinados:
```bash
git tag plugins-mx-v0.2.0
```

Refleja un estado coherente del monorepo entero.

---

## CHANGELOG.md por plugin

Cada plugin debe tener su propio `CHANGELOG.md` con formato [Keep a Changelog](https://keepachangelog.com).

### Estructura

```markdown
# Changelog — freelancers-mx

Todos los cambios notables de este plugin se documentan aquí.
Formato: [Keep a Changelog](https://keepachangelog.com).
Versioning: [Semantic Versioning](https://semver.org).

## [Unreleased]

### Added
- Nuevos features que se sumarán al próximo release

### Changed
- Cambios en funcionalidad existente

### Deprecated
- Features que serán eliminados pronto

### Removed
- Features ya eliminados

### Fixed
- Bug fixes

### Security
- Mejoras de seguridad

## [0.2.0] — 2026-09-15

### Added
- Integración con Facturama sandbox para timbrado real
- Nuevo skill `clabe-validacion`

### Changed
- `cotizacion-mxn` ahora soporta moneda USD con TC del DOF

### Fixed
- Cálculo de IVA con redondeo correcto en cotizaciones con descuentos

## [0.1.0] — 2026-06-11

### Added
- Scaffolding inicial del vertical
- 5 skills propios: cotizacion-mxn, propuesta-comercial, cobranza-seguimiento, cliente-onboarding, freelance-tax-mx
- 5 commands: /freelancers:cotizar, etc.
- Integración con _shared/ vía sync-shared.sh
```

### Convenciones del CHANGELOG

- Versiones desc (más reciente arriba)
- Fecha en formato ISO (YYYY-MM-DD)
- Categorías: Added, Changed, Deprecated, Removed, Fixed, Security
- `[Unreleased]` para cambios sin publicar todavía
- Cada entrada: 1 línea descriptiva

---

## CHANGELOG.md raíz

Documenta cambios del monorepo como un todo:
- Arquitectura
- Tooling (scripts/)
- Documentación
- Cambios en `_shared/` que afectan a todos los plugins

---

## Política de actualización de `_shared/`

Cambios en `_shared/` impactan a TODOS los plugins que lo usan. Reglas:

### Cambio que rompe contratos (breaking)
- Bump **MINOR** de TODOS los plugins que consumen el skill afectado
- Documentar en CHANGELOG de `_shared/` y de cada plugin
- Notificar mediante PR/release notes

### Cambio backwards-compatible
- Bump **PATCH** de los plugins que se benefician (opcional)
- Documentar en CHANGELOG de `_shared/`

### Después del cambio
1. Editar en `_shared/<skill>/`
2. Correr `./scripts/sync-shared.sh`
3. Verificar lint
4. Commit
5. (Si es minor de plugins) bump versions

---

## Política de deprecación

Cuando un skill o feature será eliminado:

1. **Anunciar** en CHANGELOG bajo `Deprecated`
2. **Mantener funcional** por al menos un MINOR release
3. **Migración path** documentada
4. **Remover** en el siguiente MINOR

Ejemplo:
- v0.5.0: deprecar skill `viejo-skill`, agregar `nuevo-skill`
- v0.5.x: ambos coexisten
- v0.6.0: remover `viejo-skill`

---

## Bumps masivos

Si todo el monorepo cambia coordinado (ej. nueva versión de Claude Code):

```bash
# Script (opcional, futuro)
./scripts/version-bump.sh minor
# Bumpa MINOR de todos los plugin.json
```

---

## Release process

### Pre-release
1. Asegurar lint passing
2. Asegurar fixtures pasan (cuando exista runner)
3. Actualizar CHANGELOG del plugin con cambios
4. Bump version en `plugin.json`
5. Commit: `chore(<plugin>): bump version to X.Y.Z`
6. Tag: `git tag <plugin>-vX.Y.Z`

### Push del release
1. Push commit + tag al remote
2. (Si hay GitHub Releases) crear release con notas del CHANGELOG
3. Notificar usuarios si hay cambios breaking

### Post-release
1. Verificar instalación limpia funciona
2. Monitorear issues los primeros días
3. PATCH release rápido si hay bugs críticos

---

## Referencias de versionado por plugin

| Plugin | Versión actual | Próximo target |
|---|---|---|
| core-mexico | 0.1.0 | 0.2.0 (con más references) |
| freelancers-mx | 0.1.0 | 0.2.0 (con dogfooding) |
| agencia-marketing-mx | 0.1.0 | 0.2.0 |
| colegios-mx | 0.1.0 | 0.2.0 |
| talleres-mx | 0.1.0 | 0.2.0 |

---

## Ver también

- [guia-desarrollo.md](guia-desarrollo.md) — cómo agregar features
- [roadmap.md](roadmap.md) — qué viene en próximas versiones
- [CHANGELOG.md](../CHANGELOG.md) — cambios del monorepo
