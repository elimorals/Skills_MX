# mp_sep_profesional

MCP standalone para validación de cédulas profesionales SEP (Registro Nacional de Profesionistas).

**Portal**: https://cedulaprofesional.sep.gob.mx/ — cada consulta exige token **reCAPTCHA v3**; el MCP devuelve handoff humano.

## Por qué importa

- Desbloquea verticales que por ley requieren validar cédula:
  - **`telemedicina-mx`** (NOM-004-SSA3-2012 + Acuerdo COFEPRIS 28-mar-2024)
  - **`consultorio-especialista-mx`**, `clinica-salud-mx`, `psicoterapia-mx`
  - **`despacho-legal-mx`** (Ley General de Profesiones Art. 26)
  - **`despacho-contable-mx`** (LISR firma dictamen)
  - `inmobiliaria-mx` (arquitectos firma de planos)

## Tools expuestas

| Tool | Modo | Para qué |
|------|------|----------|
| `sep_consultar_cedula` | Por número | Validar cédula que el cliente proporcionó |
| `sep_consultar_por_datos` | Por nombre+apellidos | Cuando no se tiene el número |
| `sep_validar_medico_para_consulta` | Compuesto | Telemedicina-mx: ¿este médico puede dar consulta? |
| `sep_listar_profesiones_reguladas` | Catálogo | Saber qué profesiones requieren validación |

## Flujo `sep_validar_medico_para_consulta` (NOM-004 + COFEPRIS 2024)

```
input: cedula="1234567", cedula_especialidad="7654321"
   │
   ├─→ Valida cédula general:
   │    - debe existir en RNP
   │    - debe estar vigente
   │    - debe ser de salud (Médico Cirujano u homólogo)
   │
   ├─→ Si especialidad: valida también
   │    - debe estar vigente
   │
   └─→ Resultado:
        - puede_dar_consulta = cédula_general_ok
        - puede_recetar_controlados = cédula_general_ok AND cédula_especialidad_ok
        - cumple_nom_004 = puede_dar_consulta
        - cumple_cofepris_2024 = puede_dar_consulta
```

## Estado real

| Fecha | URL | Resultado |
|---|---|---|
| 2026-10-14 | `GET https://cedulaprofesional.sep.gob.mx/assets/config.json` | 200, declara `recaptchaSiteKey` |
| 2026-10-14 | `main.*.js` del portal | `POST /api/rnp/solr/profesionista/consultar/byDetalle` exige `Authorization: Bearer` + `X-Recaptcha-Token` |
| 2026-10-14 | `GET /api/auth/token` (headers públicos `X-Client-Id`/`X-API-Key` de `config.json`) | 200, `access_token` JWT |

- Estado sin solver: **handoff humano**. Las tools devuelven `requiere_humano: true`,
  URL, pasos y los datos prellenados.
- Estado con solver opt-in (`PLUGINS_MX_CAPTCHA_SOLVER=2captcha` + `TWOCAPTCHA_API_KEY`):
  **real sin validar en vivo (falta llave)**. reCAPTCHA v3 (api.js, no Enterprise),
  sitekey `6Leb1M4rAAAAAP_gRcAyMiOo99-j6eqQajKuMlB9` (se lee en vivo de `config.json`),
  action `submit`. Flujo: token 2captcha → `GET /api/auth/token` → `POST byDetalle`
  con `X-Recaptcha-Token`; body `{"numCedula"}` o `{"nombre","primerApellido","segundoApellido","curp"}`
  en mayúsculas. 401/403 (o 400 que mencione captcha) = token rechazado → hasta 2
  reintentos, luego `UpstreamError`. Campos del resultado tomados del bundle
  (`cedula`, `nombre`, `primerApellido`, `segundoApellido`, `genero`, `profesion`,
  `institucion`, `entidadInstitucion`, `anioRegistro`). Test live:
  `PLUGINS_MX_LIVE=1 TWOCAPTCHA_API_KEY=… SEP_CEDULA_LIVE=… pytest -m live mp_sep_profesional`.
- `sep_validar_medico_para_consulta` en real devuelve `puede_dar_consulta: null`
  (desconocido) con el handoff, nunca `true`/`false` sin dato.
- Mock solo con `PLUGINS_MX_MOCK=1` (`simulated: true`).
- Test live verifica que el portal siga declarando reCAPTCHA.

## Caché

30 días por cédula. Los datos del RNP cambian raramente (correcciones, defunciones).

## Bitácora

Las cédulas y CURP se hashean antes de loggearse (datos personales).

## Tests

```bash
PYTHONPATH=mcp-servers pytest mcp-servers/mp_sep_profesional/tests/ -v
```
