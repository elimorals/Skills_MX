# mp_puebla_municipal

## Tools

- `puebla_mun_consultar_predial(cuenta_predial)` — handoff humano (`motivo: captcha`).

El portal pide cuenta + delegación + LC + CAPTCHA de imagen (`answer`). No se intenta
resolver el CAPTCHA. Multas estatales: sin portal público verificado (ver `mp_multas_mx`);
la URL anterior (`hacienda.puebla.gob.mx/multas`) no resolvía DNS.

## Estado real

| Fecha | URL | Resultado |
|---|---|---|
| 2026-10-14 | `GET https://srvappayt.pueblacapital.gob.mx:7016/pabel/iniciopredial` | 200; form `forma` con `cuenta`, `delegacion`, `lc`, `answer` (CAPTCHA) y `_csrf` |

Sin solver: handoff humano. Solver opt-in (`PLUGINS_MX_CAPTCHA_SOLVER=2captcha` + `TWOCAPTCHA_API_KEY`) y
`delegacion` (o LC de 24 dígitos): GET al form, `simpleImg.jpg` a 2captcha, POST con `_csrf`; hasta 3 intentos.
Estado: con solver opt-in: real sin validar en vivo (falta llave); el parseo del resultado y del mensaje de captcha incorrecto es
heurístico hasta ver una respuesta real. Test live: `TWOCAPTCHA_API_KEY` + `PUEBLA_PREDIAL_CUENTA_LIVE`
(+ `PUEBLA_PREDIAL_DELEGACION_LIVE`).

Mock solo con `PLUGINS_MX_MOCK=1`.
