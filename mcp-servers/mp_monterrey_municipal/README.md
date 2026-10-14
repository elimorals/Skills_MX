# mp_monterrey_municipal — AMM (Área Metropolitana de Monterrey)

## Tools

| Tool | Estado |
|---|---|
| `nl_consultar_predial(municipio, cuenta_predial)` | Real para **Monterrey** (expediente catastral de 8 dígitos). Otros municipios del AMM → `UpstreamError` explícito (portal no verificado). |
| `nl_listar_catalogos()` | Municipios AMM y cuáles tienen predial real. |

Se retiraron `nl_consultar_multas` y `nl_consultar_calidad_aire`: devolvían datos
inventados y no hay fuente real verificada (multas: ver `mp_multas_mx`).

## Estado real

| Fecha | URL | Resultado |
|---|---|---|
| 2026-10-14 | `GET https://asp.monterrey.gob.mx/predial/` | 200, ASP.NET WebForms, sin CAPTCHA |
| 2026-10-14 | `POST https://asp.monterrey.gob.mx/predial/` (`txt_buscar=00000001`) | 200, `lbl_warning`: "El expediente consultado no existe…" → `NotFoundError` |

El adeudo se lee del GridView `grv_Adeudos` (`lbl_Totales_empty` / `lbl_Totales_bnf`,
nombres tomados de `Scripts/funcionesPredial.js`). La tabla con adeudo no se ha visto
con un expediente real: validar con `MTY_EXPEDIENTE=… PLUGINS_MX_LIVE=1 pytest -m live`.
