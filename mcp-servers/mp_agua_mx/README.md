# mp_agua_mx

Consulta unificada de adeudo de agua en organismos operadores de México.

## Tools

- `agua_consultar_adeudo(organismo, cuenta)` — según el organismo:
  - **real** (`consultable=True`, validado en vivo): `jmas_juarez`.
  - **handoff humano** (`metodo="publica_captcha"`): `siapa` (reCAPTCHA v2, verificado); `sadm` (marcado con captcha en el catálogo, no verificado en vivo).
  - **error explícito** (`upstream_error`, `details.implementado=false`): el resto.
    Nunca devuelve un adeudo inventado ni `0.0` por "no implementado".
- `agua_listar_organismos(solo_consultables)`, `agua_buscar_por_estado(estado)`,
  `agua_estadisticas()` — catálogo local (`shared/agua_mx.py`).

Datos simulados solo con `PLUGINS_MX_MOCK=1` (`simulated: true`). La respuesta real de
JMAS no incluye nombre ni dirección del titular aunque el portal los muestre.

## Estado real

| Fecha | URL | Resultado |
|---|---|---|
| 2026-10-14 | `GET https://jmasjuarez.gob.mx/v026/pago.php?cuenta=…` | 200; HTML con "Saldo Actual", "Fecha de Vencimiento", "Detalle del Cobro". Cuenta inexistente → alerta "No se encontró la cuenta…" (`NotFoundError`) |
| 2026-10-14 | `GET https://www.siapa.gob.mx/aplicaciones/pagoenlinea/` | 200; form `form_pago_linea` con reCAPTCHA v2 (cadena TLS incompleta en el servidor) |
| 2026-10-14 | `GET https://www.cespt.gob.mx/EnLinea/Adeudo.aspx` | 404 — pendiente redescubrir |
| 2026-10-14 | `https://pagoenlinea.ooapas.gob.mx/index_pago_express.php` | 200, sin CAPTCHA; parser pendiente de un folio de recibo real |

Se eliminó el path SIAPA con Playwright y la variable `PLUGINS_MX_SIAPA_RECAPTCHA_TOKEN`
(permitía inyectar un token de reCAPTCHA resuelto por terceros).

Tests live: `PLUGINS_MX_LIVE=1 pytest mp_agua_mx -m live`. Con cuenta propia de JMAS:
`JMAS_CUENTA=…` (no usar cuentas ajenas: el portal muestra datos personales).
