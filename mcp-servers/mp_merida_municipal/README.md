# mp_merida_municipal

## Tools

- `merida_mun_consultar_predial(calle, numero)` — handoff humano (`motivo: bot_manager`).
  El portal busca por dirección, no por cuenta.

Multas estatales: sin portal público verificado (ver `mp_multas_mx`); la URL anterior
(`transito.yucatan.gob.mx/multas`) no resolvía DNS.

## Estado real

| Fecha | URL | Resultado |
|---|---|---|
| 2026-10-14 | `GET https://isla.merida.gob.mx/serviciosinternet/predialmid/index.php` | 200 tras redirect a reto de Radware Bot Manager con hCaptcha (`hcaptcha.com/1/api.js`) |
| 2026-10-14 (2ª) | mismo `GET` con httpx | 200 con el formulario; carga Radware (`stormcaster.js`, `verify.perfdrive.com`) y reCAPTCHA **v3** del formulario (sitekey `6Lc3EjQmAAAAAEYFAUWTNk_k2wGN6rXoauSJ5jlS`, acción `submit`, verificado en `wServices/captcha/verify.php`) |
| 2026-10-14 (2ª) | `GET assets/js/plus/forms.js` (la lógica de envío) 5 s después | **403** página de bloqueo de Radware ("¡Ooops! Algo salió mal", REF #20000041) |

- Estado: **handoff humano**, sin solver. El captcha del formulario (reCAPTCHA v3)
  sería resoluble, pero Radware Bot Manager bloquea a un cliente httpx antes de
  completar el flujo (403 desde la segunda petición; a veces reto hCaptcha de
  Radware desde la primera). Ese hCaptcha es el reto del bot manager, no un campo
  del formulario: resolverlo sería evadir el anti-bot. No se agrega stealth ni
  proxies. Los datos salen de `wservice.merida.gob.mx/wsducat2/api/predios/sigot/KIOWEB`;
  no se llama directo porque saltaría la verificación del captcha.

Mock solo con `PLUGINS_MX_MOCK=1`.
