# mp_sacpi_michoacan

Predial de 95 municipios de Michoacán vía SACPI (Gobierno del Estado).

## Tools

- `sacpi_consultar(municipio, cuenta_predial, tipo)` — real por default (Playwright,
  extra `sat-playwright`). Antes de lanzar el navegador verifica que SACPI responda; si
  no, devuelve `upstream_error` con la página oficial. Mock solo con `PLUGINS_MX_MOCK=1`.
- `sacpi_listar_municipios()`, `sacpi_codigo_municipio(nombre)` — catálogo local.

## Estado real

| Fecha | URL | Resultado |
|---|---|---|
| 2026-10-14 | `https://secfinanzas.michoacan.gob.mx/impuesto-predial-consulta-tu-adeudo/` | 200; embebe `<iframe src="https://sacpi.michoacan.gob.mx/frm_cpredial.aspx">` |
| 2026-10-14 | `http://www.sacpi.michoacan.gob.mx/frm_cpredial.aspx` y `https://sacpi.michoacan.gob.mx/…` | **NXDOMAIN** (8.8.8.8 y DNS local; SOA de michoacan.gob.mx responde) |

**No validado en vivo**: el host está caído. Los selectores de `consulta_sacpi`
(`ddlMunicipios`, `ddlTipo`, `txtCuenta`) vienen de 2026-06-13 y deben revalidarse
cuando SACPI vuelva. `PLUGINS_MX_LIVE=1 pytest mp_sacpi_michoacan -m live` falla hoy
a propósito y pasará cuando el host resuelva.
