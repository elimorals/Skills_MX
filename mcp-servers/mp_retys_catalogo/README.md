# mp_retys_catalogo

Catálogo Nacional de Regulaciones, Trámites y Servicios (**CONAMER**).

## Tools

- `retys_listar_sectores()` — los 27 "Temas de interés" de la portada (verificados 2026-10-14).
- `retys_buscar_en_vivo(q)` — **real**: regulaciones + inspecciones (primera página de cada una)
  con homoclave, dependencia y URL de la ficha.
- `retys_buscar_tramite(q, sector?)` — fuera de mock delega en `retys_buscar_en_vivo` (el buscador
  ya no publica trámites); con `PLUGINS_MX_MOCK=1` usa el catálogo curado.
- `retys_detalle_tramite(homoclave)` — fuera de mock devuelve la URL oficial de la ficha
  (`R-…` regulación, `I-…` inspección).
- `retys_exportar_dcat()` — solo con `PLUGINS_MX_MOCK=1` (exporta el catálogo curado, cuyas
  homoclaves no son oficiales); fuera de mock → `ConfigError`.

## Estado real

Validado en vivo 2026-10-14 en `https://www.catalogonacional.gob.mx/`:

| Cliente | Resultado |
|---|---|
| curl / httpx (con UA de navegador) | 403 Akamai "Access Denied" |
| Chromium headless (`playwright_session`) | 403 Akamai → `UpstreamError` con instrucción |
| Chromium con ventana (`MP_PLAYWRIGHT_HEADLESS=0`) | 200; `buscar_en_vivo("salud")` → 10 regulaciones + 10 inspecciones; `"cofepris"` → 7 inspecciones |

- Endpoints: `GET /Buscador/SearchRegulacionResult` y `/Buscador/SearchInspeccionResult`
  (`search`, `txtTipo=Todos`, `nivelId`, `estadoId`, `municipioId`, `dependenciaId`, `tem`), llamados
  con `fetch` desde la página para heredar la sesión que acepta Akamai.
- El buscador ya solo muestra Inspecciones / Inspectores / Regulaciones; los trámites no aparecen.
- La sección de regulaciones falla del lado del servidor con algunos términos ("cofepris",
  "licencia sanitaria": `42601: syntax error at or near "["`). Se devuelve como `error` de esa
  sección; las inspecciones siguen funcionando.
- Requiere el extra `publicos-federales-2` y `playwright install chromium`. Sin fallback a mock.

Fixtures reales en `tests/fixtures/`. Live:
`MP_PLAYWRIGHT_HEADLESS=0 PLUGINS_MX_LIVE=1 pytest mp_retys_catalogo -k live`.
