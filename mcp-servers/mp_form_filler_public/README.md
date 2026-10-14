# mp_form_filler_public

Preparación de **formularios públicos gob.mx sin login**: catálogo, validación
pre-flight y handoff humano con los campos listos para pegar.

## Formularios en catálogo

| Clave | Portal | CAPTCHA | MCP que consulta de verdad |
|---|---|---|---|
| `sat_rfc_consulta` | SAT Padrón | imagen | — |
| `sat_verifica_cfdi` | SAT Verifica CFDI | imagen | — |
| `repse_consulta` | STPS REPSE | sin captcha | `mp_repse_stps` (real validado) |
| `repuve_consulta` | REPUVE | reCAPTCHA v3 | `mp_repuve` (handoff) |
| `repep_consulta` | PROFECO REPEP | sin captcha | — |
| `curp_consulta` | RENAPO CURP | reCAPTCHA Enterprise + Akamai | `mp_curp_renapo` (handoff) |
| `buro_comercial` | PROFECO Buró | sin captcha | — |
| `sat_opinion_32d` | SAT 32-D | sin captcha | — |

## Tools

- `form_listar_formularios(sin_captcha?)` — catálogo filtrable
- `form_validar_inputs(clave, datos)` — pre-flight local (sin red)
- `form_llenar(clave, datos)` — valida y devuelve handoff humano

## Estado real

| Fecha | URL | Resultado |
|---|---|---|
| 2026-10-14 | URLs de `repse_consulta`, `repep_consulta`, `buro_comercial` (GET, test live) | < 500 |
| 2026-10-14 | REPUVE / RENAPO | CAPTCHA confirmado (ver READMEs de `mp_repuve`, `mp_curp_renapo`) |

- Estado: **handoff humano**. `form_llenar` ya no abre un navegador ni envía
  nada: devuelve `requiere_humano: true`, URL, pasos, `campos_prellenados`
  validados y, si existe, `mcp_real` (el MCP que consulta ese portal por API).
- Se eliminó el path Playwright con fallback silencioso.
- **NUNCA** intenta resolver CAPTCHA.
- Mock solo con `PLUGINS_MX_MOCK=1` (`simulated: true`).

## Validaciones MX integradas

`RFC_RE`, `CURP_RE`, `NSS_RE`, `PLACA_RE`, `TEL_RE` — fallan rápido sin tocar red.

## Bitácora

Hashea RFC, CURP, NSS, teléfono, placa antes de log (LFPDPPP-compliant).
