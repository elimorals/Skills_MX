# mp_ine_verificacion

Credencial para Votar (INE): formatos por modelo, regla de vigencia y handoff a la consulta oficial.

**Compliance**: `ine_verificar_datos` exige `autorizacion_token` del titular (datos personales).

## Tools

- `ine_verificar_datos(modelo, autorizacion_token, cic?, id_ciudadano?, ocr?, clave_elector?, numero_emision?)`
  — valida los campos que pide el INE para ese modelo. Sin solver: **handoff humano** (reCAPTCHA).
  Con solver opt-in: `estado` (`vigente` / `no_vigente` / `no_encontrada`), `mensaje_oficial`,
  `fecha_portal`, `fecha_consulta` y `aviso_privacidad` (LFPDPPP).
- `ine_consultar_vigencia(modelo, anio_emision)` — regla publicada: modelo vigente y 10 años
  desde la emisión. No ve bajas por robo/extravío.
- `ine_verificar_qr(qr_payload)` — no verificable localmente (`autentica: null`).
- `ine_generar_autorizacion(curp, proposito, vigencia_dias?)` — plantilla de texto.
- `ine_listar_modelos()` — modelos A-J con campos y vigencia según el INE.

## Estado real

**Handoff humano en la práctica; solver opt-in conectado pero sin validar en vivo.**
Revisado 2026-10-14 en `https://listanominal.ine.mx/scpln/` (solo GET):

- httpx/curl → 403 con `cf-mitigated: challenge` (Cloudflare "Just a moment", challenge JS)
  **antes** del formulario. No se agrega stealth, proxies ni evasión del challenge.
- Navegador real → 200: cuatro formularios `POST /scpln/resultado.html` (urlencoded) con
  `modelo` oculto (`e` = E-J, `d`, `c`; `r` = reporte de robo/extravío), campos `cic`,
  `idCiudadano`, `ocr`, `claveElector`, `numeroEmision` y `g-recaptcha-response`.
- Captcha: **reCAPTCHA v2 checkbox** (`api.js`, no Enterprise, sin action), sitekey
  `6LdAe1sUAAAAACrdhVFHK5KmZ5TA8ZJ0iWQ6i64b` en los cuatro widgets.

Con `PLUGINS_MX_CAPTCHA_SOLVER=2captcha` + `TWOCAPTCHA_API_KEY` (`solver_activo("ine_verificacion")`):
GET al formulario → si Cloudflare responde challenge, handoff `motivo="bot_manager"` sin gastar
captcha (hoy es lo que ocurre desde httpx) → si carga, token v2 por 2captcha → POST → parseo.
Token rechazado (vuelve al formulario o "Captcha necesario") → reintento con `con_token`, luego
`UpstreamError`. El parseo de `resultado.html` usa frases inferidas: nunca se vio un resultado
real (falta llave de 2captcha y no se enviaron datos de personas); si no reconoce la respuesta
falla en vez de adivinar. Test live: `PLUGINS_MX_LIVE=1` + `TWOCAPTCHA_API_KEY` + `INE_TEST_MODELO`,
`INE_TEST_CIC`, `INE_TEST_ID_CIUDADANO` (o `_OCR`, `_CLAVE_ELECTOR`, `_NUMERO_EMISION`) de tu credencial.

Privacidad: sin caché de resultados; la bitácora guarda solo hashes de los campos.
- Campos (maxlength del formulario): CIC 9, Identificador del ciudadano 9, OCR 13,
  clave de elector 18, número de emisión 2.
- Vigentes según el INE: E (jul-2014), F (extranjero, feb-2016), G y H (dic-2019), I y J (jun-2026).
  D y A-C: "No vigente". "La vigencia de cada credencial es de diez años a partir de su emisión."

Corregido respecto al mock: autenticidad y "similitud de huellas" se decidían por el último
dígito; el CIC tenía 13 dígitos (son 9); los modelos C/D/D1/E/F y sus años eran incorrectos.
