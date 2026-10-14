# mp_predial_mx — Predial unificado multi-municipio

Tools: `predial_consultar`, `predial_listar_municipios`, `predial_buscar_municipio`,
`predial_estadisticas_catalogo`.

Routing real (sin fallback a mock; mock solo con `PLUGINS_MX_MOCK=1`):

1. CDMX → handoff humano a OVICA (ALTCHA).
2. Toluca → httpx contra la Tesorería (sin CAPTCHA).
3. Municipios SACPI (Michoacán) → `shared.plataformas_saas_mx`.
4. Municipios con URL en el catálogo central → Playwright genérico
   (`pip install -e ".[estatal-centro]" && playwright install chromium`).
5. Sin URL ni SaaS → `upstream_error`.

## Estado real (2026-10-14)

| Municipio | URL | Status | Resultado |
|---|---|---|---|
| CDMX | https://ovica.finanzas.cdmx.gob.mx/cuenta-predial-liquidacion | 200 | ALTCHA → handoff |
| Toluca | http://predial.toluca.gob.mx/Formas/ImpuestoPredial.aspx | 200 | Real (clave ficticia → `not_found`) |
| Resto del catálogo | ver `shared/catalogo_municipios_mx.py` | — | Selectores del discovery 2026-06; no revalidados en esta oleada (catálogo compartido con E2) |

## Tests

```bash
cd mcp-servers && .venv/bin/pytest -q mp_predial_mx
```
