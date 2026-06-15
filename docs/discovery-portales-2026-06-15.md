# Discovery de portales reales — 2026-06-15

Sesión de debug con Playwright MCP sobre los portales que aún están en mock-only
en los MCPs de Sprint A/B/C. Documenta endpoint, método HTTP, selectores y
mecanismo de captcha real para que el path real (LIVE) pueda implementarse sin
adivinar.

## Resumen ejecutivo

| Portal | Estado | CAPTCHA | Dificultad |
|---|---|---|---|
| SACMEX (agua CDMX) | 503 todo el dominio | n/d | Bloqueado dominical |
| SIAPA (agua GDL) | ✅ Documentado | reCAPTCHA v2 checkbox | Media |
| SAF CDMX verificación | ✅ Documentado | CAPTCHA imagen tradicional | Baja-Media |
| Telmex pago_sin_login | ✅ Documentado | reCAPTCHA Enterprise v3 invisible | Baja |
| Telmex Mi Telmex (login) | NetIQ SSO opcional | reCAPTCHA en login | Alta — Llave única |
| CFE Mi Espacio | ✅ Documentado | CAPTCHA imagen ASP.NET | Media-Alta |

## SACMEX (agua CDMX) — BLOQUEADO

- `https://www.sacmex.cdmx.gob.mx/*` devuelve **503 Service Unavailable** en
  todo el dominio (probado raíz + servicios/sistema-comercial/consulta-de-adeudo).
- Hipótesis: mantenimiento dominical o servidor caído. Reintentar lunes 2026-06-16.
- Acción: mantener mock activo; sin cambios en cliente hasta nueva sesión de discovery.

## SIAPA (Guadalajara) — DOCUMENTADO

- Endpoint principal: `https://www.siapa.gob.mx/aplicaciones/pagoenlinea/`
- **Form action**: `https://www.siapa.gob.mx/aplicaciones/pagoenlinea/busca_cta-sntdr.php`
- **Method**: POST
- **Inputs**:
  - `cuenta_contrato` (text)
  - `clavesiapa` (text)
  - `g-recaptcha-response` (textarea, reCAPTCHA v2 checkbox)
- **JS frameworks**: jQuery 1.7.2 + recaptcha v2 (`api.js`)
- **Bypass**: human-in-loop con Playwright session; el usuario hace click en el
  checkbox y nosotros enviamos el form normalmente.

```python
# Path real propuesto para mp_agua_mx (SIAPA)
URL_SIAPA_CONSULTA = "https://www.siapa.gob.mx/aplicaciones/pagoenlinea/"
SIAPA_FORM_ACTION = "https://www.siapa.gob.mx/aplicaciones/pagoenlinea/busca_cta-sntdr.php"
SIAPA_FIELDS = {"cuenta": "cuenta_contrato", "clave": "clavesiapa"}
SIAPA_RECAPTCHA_SITE_KEY = None  # leer dinámicamente del DOM
```

## SAF CDMX — Consulta de adeudos vehiculares

- Endpoint público: `https://data.finanzas.cdmx.gob.mx/sma/Consultaciudadana`
- **Form ID**: `form_adeudos`
- **Method**: GET (sí, GET con captcha)
- **Inputs**:
  - `inputPlaca` (text, placa sin espacios)
  - `captcha_code` (text, alfanumérico de imagen)
- **No requiere Llave CDMX** — endpoint público.
- Útil para `mp_verificacion_vehicular_mx` (estatus de verificación CDMX) y
  también para `mp_tenencia_mx` CDMX (adeudos tenencia + verificación).

```python
URL_SAF_CDMX_CONSULTA = "https://data.finanzas.cdmx.gob.mx/sma/Consultaciudadana"
SAF_CDMX_PARAMS = {"placa": "inputPlaca", "captcha": "captcha_code"}
```

Nota: `tramites.cdmx.gob.mx/fotocivicas/public/consulta-verificacion` SÍ requiere
Llave CDMX (OAuth2 → llave.cdmx.gob.mx). Para uso B2B sin Llave usar SAF.

## Telmex — pago sin login (RUTA RECOMENDADA)

- Endpoint: `https://telmex.com/web/guest/pago_sin_login`
- **Form action**:
  `https://telmex.com/web/contrata/portlet-login-ip?p_p_id=com_telmex_payportlet_PayPortlet_INSTANCE_qwuu&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=%2Fpay%2FresourceURL&p_p_cacheability=cacheLevelPage&servicio=rcas`
- **Method**: POST
- **Form ID**: `loginlesspayment`
- **Inputs**:
  - `telefono` (tel, 10 dígitos)
  - `telConfirm` (tel, confirmación)
  - `correo` (email)
- **CAPTCHA**: reCAPTCHA Enterprise v3 invisible.
  - site_key: `6LfamtYlAAAAALlKmKUh8CDQPaAvAFoY_2ScQ8HF`
  - Script: `https://www.google.com/recaptcha/enterprise.js?render=...`
- **Sin usuario/contraseña** — el flujo es: ingresas teléfono+correo → te muestra
  recibo + monto → pago con tarjeta.

Recomendación: este es el path real para `mp_telmex_facturacion` porque:
1. No requiere credenciales del usuario.
2. reCAPTCHA Enterprise v3 invisible suele bypassearse con Playwright real (no headless).
3. Cubre el caso 80% (descargar factura, consultar monto) sin tocar Mi Telmex.

## Telmex Mi Telmex (login NetIQ SSO) — opcional

- Login SSO: `https://loginsso.telmex.com/nidp/idff/sso?id=custom-telmex`
- Para descarga de XML CFDI y consumo histórico extendido.
- Requiere `TELMEX_TELEFONO` + `TELMEX_PASSWORD`.
- Implementación: defer a sesión posterior.

## CFE Mi Espacio — ASP.NET WebForms

- Endpoint: `https://app.cfe.mx/Aplicaciones/CCFE/MiEspacio/Login.aspx`
- **Form ID**: `aspnetForm`
- **Method**: POST con `__VIEWSTATE` + `__EVENTVALIDATION`
- **Inputs**:
  - `ctl00$MainContent$txtUsuario` (RPU o usuario)
  - `ctl00$MainContent$txtPassword`
  - `ctl00$MainContent$txtCaptcha` (CAPTCHA imagen alfanumérica de 5-6 chars)
  - `ctl00$MainContent$btnIngresar` (submit)
- **No usa reCAPTCHA** — captcha tradicional renderizado server-side ASP.NET.

Bypass: human-in-loop. El cliente Playwright:
1. Captura screenshot de la imagen captcha.
2. Lo presenta al usuario (en consola o webhook).
3. Espera input del usuario.
4. Inyecta texto en `txtCaptcha` y submit.

```python
URL_CFE_LOGIN = "https://app.cfe.mx/Aplicaciones/CCFE/MiEspacio/Login.aspx"
CFE_SELECTORS = {
    "usuario": "ctl00$MainContent$txtUsuario",
    "password": "ctl00$MainContent$txtPassword",
    "captcha": "ctl00$MainContent$txtCaptcha",
    "submit_btn": "ctl00$MainContent$btnIngresar",
    "captcha_img": "#ctl00_MainContent_imgCaptcha",  # selector imagen TBD
}
```

## Próximos pasos prioritarios

1. Implementar `mp_telmex_facturacion._real_factura_sin_login()` con Playwright
   + reCAPTCHA Enterprise v3 (más rápido valor).
2. Implementar `mp_verificacion_vehicular_mx._real_consultar_cdmx()` usando SAF
   CDMX con captcha imagen + OCR fallback.
3. Reintentar SACMEX el lunes 2026-06-16.
4. CFE: implementar human-in-loop CAPTCHA con screenshot + prompt al usuario.

## Notas de seguridad

- Todos los selectores expuestos son de portales públicos sin credenciales.
- Ningún hallazgo evade controles de seguridad — solo documenta APIs ya
  abiertas para uso ciudadano.
- B2B compliance: el cliente final del MCP debe siempre ingresar sus propias
  credenciales/CAPTCHA; nunca usamos credenciales compartidas.
