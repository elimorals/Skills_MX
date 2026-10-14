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

Mock solo con `PLUGINS_MX_MOCK=1`.
