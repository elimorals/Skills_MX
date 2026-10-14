# mp_queretaro_municipal

Predial del municipio de Querétaro.

## Tools

- `queretaro_mun_consultar_predial(clave_catastral, letras_propietario)` — adeudo real.
  Clave catastral de 15 dígitos + 4 letras del nombre del propietario (el portal las valida
  antes de mostrar el adeudo; el cliente respeta esa validación).

Multas estatales: no se exponen aquí (ver `mp_multas_mx`).

## Estado real

| Fecha | URL | Resultado |
|---|---|---|
| 2026-10-14 | `POST https://webservices.municipiodequeretaro.gob.mx/consultaLC/v2/agenda_digital.php` | 200 JSON `{"codigo":"000", "datos": {"status":201}}` (clave ficticia → sin coincidencias) |
| 2026-10-14 | `GET …/consultaLC/v2/functions.php?clave_catastral=…&tpobus=L&periodo_calculo=NULL` | 200 JSON `{"errmsg":"La clave catastral no existe"}` |

Endpoints descubiertos en `js/main.ncc.js` del portal. Sin CAPTCHA. Errores del portal →
`NotFoundError`/`UpstreamError`; nunca datos simulados salvo `PLUGINS_MX_MOCK=1`.

Tests live: `PLUGINS_MX_LIVE=1 .venv/bin/pytest mp_queretaro_municipal -m live`.
Con un predio propio: `QRO_CLAVE_CATASTRAL=… QRO_LETRAS=…` (no se commitean).
