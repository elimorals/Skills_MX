# mp_form_filler_public

Autollenado de **formularios públicos gob.mx sin login** (Nivel 2 — preparación).

## Formularios soportados (8 con selectores validados vivo)

| Clave | Portal | CAPTCHA |
|---|---|---|
| `sat_rfc_consulta` | SAT Padrón | imagen |
| `sat_verifica_cfdi` | SAT Verifica CFDI | imagen |
| `repse_consulta` | STPS REPSE | sin captcha |
| `repuve_consulta` | REPUVE | imagen |
| `repep_consulta` | PROFECO REPEP | sin captcha |
| `curp_consulta` | RENAPO CURP | reCAPTCHA v2 |
| `buro_comercial` | PROFECO Buró | sin captcha |
| `sat_opinion_32d` | SAT 32-D | sin captcha |

## Tools

- `form_listar_formularios(sin_captcha?)` — catálogo filtrable
- `form_validar_inputs(clave, datos)` — pre-flight local (sin red)
- `form_llenar(clave, datos, screenshot?)` — Playwright opt-in

## Comportamiento

- **Sin `MP_PLAYWRIGHT_PUBLIC=1`**: mock con shape realista
- **Con flag**: Playwright real → llena campos → detecta CAPTCHA → marca `requiere_intervencion_humana=True`
- **NUNCA** intenta resolver CAPTCHA — pasa control al humano

## Validaciones MX integradas

`RFC_RE`, `CURP_RE`, `NSS_RE`, `PLACA_RE`, `TEL_RE` — fallan rápido sin tocar red.

## Bitácora

Hashea RFC, CURP, NSS, teléfono, placa antes de log (LFPDPPP-compliant).
