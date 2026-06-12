# ADR 005 — Selectores Playwright versionados en módulo separado

**Status**: ACEPTADO  (2026-06-12)

## Context

`mp_sat_portal` y `mp_bancos_mx` requieren Playwright para portales sin API. El portal SAT cambia su HTML cada 3-6 meses (botones renombrados, IDs nuevos, flujo reordenado). Cuando esto pasa, el scraper rompe en producción.

Si los selectores CSS/XPath están embebidos dentro del código del cliente (`page.click('button.btn-submit')`), actualizar requiere editar el código, redeploy, posiblemente fork si el operador no es el maintainer.

## Decision

Separar los selectores del código del cliente. Crear `mp_sat_portal/selectors.py` con dataclasses inmutables por versión:

```python
@dataclass(frozen=True)
class SelectorsV1:
    version: str = "v1-2026-Q2"
    login_input_cer: str = "input[type='file'][accept*='.cer']"
    # ...

CURRENT_VERSION = SelectorsV1
```

Cuando el portal cambie:
1. Crear `SelectorsV2(SelectorsV1)` heredando + sobrescribiendo solo los que cambiaron.
2. Bumpear `CURRENT_VERSION`.
3. Actualizar fixture HTML para tests de detección de breakage.

El cliente toma `selectors` como parámetro, default `default_selectors()`:

```python
def __init__(self, *, selectors: SelectorsV1 | None = None):
    self.selectors = selectors or default_selectors()
```

## Alternatives considered

1. **Selectores embebidos en código** — más simple inicialmente pero costoso de mantener. Descartado.
2. **JSON externo cargado en runtime** — más dinámico pero pierde tipado y autocompletado. Descartado.
3. **Web scraping resiliente con heurísticas (sin selectores fijos)** — ej. buscar input por label cercano. Demasiado costoso de mantener + frágil. Descartado.

## Consequences

**Positivas**:
- Cuando el portal cambie, basta crear `SelectorsV2`, NO modificar `playwright_client.py`.
- Tests pueden validar V1 vs V2 contra fixtures HTML snapshot.
- Strategy pattern permite el equivalente a rollback: `SatPlaywrightClient(selectors=SelectorsV3())` si V4 rompe.
- 13 tests del registry + helpers.

**Negativas**:
- Los selectores propuestos en `SelectorsV1` son **hipótesis razonables** sin haber validado contra portal SAT vivo (requiere e.firma vigente + acceso). Documentado claramente en `SETUP_PLAYWRIGHT_REAL.md`.
- El operador debe entender el patrón al momento de la primera ruptura del portal. Mitigación: documentación + ejemplo de implementación de `_real_verificar_efirma_vigente`.

## Ver también

- `mcp-servers/mp_sat_portal/selectors.py`
- `mcp-servers/mp_sat_portal/SETUP_PLAYWRIGHT_REAL.md`
