# mp_multas_mx — Multas de tránsito estatales

Tools: `multas_consultar(estado, placa)`, `multas_estados_disponibles()`.

Todos los portales vigentes exigen CAPTCHA o consulta manual: el tool hace un
GET real que confirma el portal y devuelve un handoff humano (`status:
requiere_humano`, URL y pasos). Mock solo con `PLUGINS_MX_MOCK=1`.

## Estado real (2026-10-14)

| Estado | URL | Status | CAPTCHA |
|---|---|---|---|
| cdmx | https://data.finanzas.cdmx.gob.mx/sma/Consultaciudadana | 200 | imagen |
| edomex | https://infracciones.ssedomex.gob.mx/Search | 200 | Turnstile |
| jal | https://gobiernoenlinea1.jalisco.gob.mx/serviciosVehiculares/adeudos | 200 | reCAPTCHA v2 |
| nl | https://www.icvnl.gob.mx/estadodecuenta | 200 | — (solo refrendo; multas son municipales) |
| nl_sanpedro | https://aplicativos.sanpedro.gob.mx/esanpedro/multas/multasnew.asp | 200 | reCAPTCHA v2 |

Retirados (GET del 2026-10-14): semovi.cdmx.gob.mx/.../infracciones y
nl.gob.mx/.../multas (404); multas.jalisco.gob.mx, transito.yucatan.gob.mx,
transitobc.gob.mx, hacienda.puebla.gob.mx, control-vehicular.queretaro.gob.mx
(DNS inexistente).

## Tests

```bash
cd mcp-servers && .venv/bin/pytest -q mp_multas_mx
```
