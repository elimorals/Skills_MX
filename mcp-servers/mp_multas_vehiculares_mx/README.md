# mp_multas_vehiculares_mx

Multas vehiculares en CDMX, EdoMex, NL (ICVNL y San Pedro) y Jalisco.

## Tools

- `multas_consultar_por_placa(estado, placa)` — handoff humano verificado.
- `multas_calcular_total(estado, placa)` — en real devuelve el mismo handoff (no hay montos sin pasar el CAPTCHA); con `PLUGINS_MX_MOCK=1` calcula sobre datos simulados.
- `multas_listar_sistemas()` — sistemas con tipo de CAPTCHA.

Se retiró `PLUGINS_MX_MULTAS_LIVE` y el flujo que pedía el CAPTCHA de SAF por
env var / stdin.

## Estado real (2026-10-14)

Un GET por portal con ≥5 s entre llamadas (`PLUGINS_MX_LIVE=1 pytest -m live mp_multas_vehiculares_mx`):

| Estado | URL | Status | CAPTCHA |
|---|---|---|---|
| cdmx | https://data.finanzas.cdmx.gob.mx/sma/Consultaciudadana | 200 | imagen (con solver opt-in: real sin validar en vivo (falta llave)) |
| edomex | https://infracciones.ssedomex.gob.mx/Search | 200 | Cloudflare Turnstile |
| nl | https://www.icvnl.gob.mx/estadodecuenta | 200 | — (consulta manual) |
| nl_sanpedro | https://aplicativos.sanpedro.gob.mx/esanpedro/multas/multasnew.asp | 200 | reCAPTCHA v2 |
| jal | https://gobiernoenlinea1.jalisco.gob.mx/serviciosVehiculares/adeudos | 200 | reCAPTCHA v2 |

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
