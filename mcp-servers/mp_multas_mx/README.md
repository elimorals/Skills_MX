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

**Solver opt-in (edomex, nl_sanpedro)** — con `PLUGINS_MX_CAPTCHA_SOLVER=2captcha` +
`TWOCAPTCHA_API_KEY`: con solver opt-in: real sin validar en vivo (falta llave).
Lógica en `shared/multas_captcha.py`; sin solver, el handoff humano de siempre.

| Estado | Captcha | Sitekey (en vivo, con respaldo) | Envío |
|---|---|---|---|
| edomex | Turnstile, sin action/cData | `0x4AAAAAABvIKlFRR9OpwO3-` | POST `/Search`: `doctype=1`, `Doc`, `__RequestVerificationToken` (+cookie antiforgery), `cf-turnstile-response` |
| nl_sanpedro | reCAPTCHA v2 | `6LfCmAEoAAAAAPZhXqaVaJQ074mEvYZ2kHutYTDA` | POST `e_cuenta_sp.asp`: `placa`, `token` (hidden), `submit`, `g-recaptcha-response` |

- San Pedro: tabla Mun./Boleta/.../Pagado/Saldo vista en vivo; pendiente = saldo > 0.
- EdoMex: la página de resultados no se ha visto (exige token). Parser genérico de tabla;
  si no reconoce tabla ni "sin infracciones", `UpstreamError` (nunca 0 por falta de dato).
- Token rechazado → 2 reintentos y luego `UpstreamError`.
- Test live: `PLUGINS_MX_LIVE=1 TWOCAPTCHA_API_KEY=... MULTAS_EDOMEX_PLACA=... MULTAS_SANPEDRO_PLACA=... pytest -m live shared/tests/test_multas_captcha.py`.

## Tests

```bash
cd mcp-servers && .venv/bin/pytest -q mp_multas_mx
```
