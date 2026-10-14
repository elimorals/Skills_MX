# mp_cdmx_municipal — Portales CDMX

Predial, tenencia, multas y Hoy No Circula para Ciudad de México.

## Tools (5)

| Tool | Qué devuelve |
|---|---|
| `cdmx_consultar_predial` | Handoff humano a OVICA (ALTCHA) tras verificar el portal |
| `cdmx_consultar_tenencia` | Handoff humano a SAF Consultaciudadana (CAPTCHA imagen) |
| `cdmx_consultar_multas` | Handoff humano a SAF Consultaciudadana (pestaña Infracciones) |
| `cdmx_consultar_hoy_no_circula` | Restricción ordinaria por fecha (reglas SEDEMA, cálculo local) |
| `cdmx_listar_catalogos` | Portales, hologramas, estatus |

Datos simulados solo con `PLUGINS_MX_MOCK=1` (marcados `simulated: true`).
Si el portal está caído o cambió, el tool devuelve `upstream_error`; nunca cae a mock.

## Estado real (2026-10-14)

| Consulta | URL | Status | Resultado |
|---|---|---|---|
| Predial | https://ovica.finanzas.cdmx.gob.mx/cuenta-predial-liquidacion | 200 | ALTCHA (proof-of-work) → handoff humano |
| Tenencia / multas | https://data.finanzas.cdmx.gob.mx/sma/Consultaciudadana | 200 | `captcha_code` imagen → handoff humano; con solver opt-in: real sin validar en vivo (falta llave) |
| Hoy No Circula | — | — | Cálculo local; no consulta contingencias (CAMe) |

Solver opt-in (`PLUGINS_MX_CAPTCHA_SOLVER=2captcha` + `TWOCAPTCHA_API_KEY`): GET al formulario, captcha a 2captcha,
POST AJAX a `/consulta_adeudos/obtenAdeudos` con `X-CSRF-TOKEN`; hasta 3 intentos si el captcha es incorrecto
(`shared/saf_cdmx.py`). Estado: con solver opt-in: real sin validar en vivo (falta llave). Test live: `TWOCAPTCHA_API_KEY` + `SAF_CDMX_PLACA_LIVE`.

Validación: `PLUGINS_MX_LIVE=1 pytest -m live mp_cdmx_municipal shared/tests/test_portal_handoff.py`
(2026-10-14T19:47Z, verde). Solo se carga la página: no se envía ninguna placa ni cuenta.

## Tests

```bash
cd mcp-servers && .venv/bin/pytest -q mp_cdmx_municipal
```
