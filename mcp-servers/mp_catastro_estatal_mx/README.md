# mp_catastro_estatal_mx

Catastros estatales: IGECEM (EdoMex), IRCEP (Puebla), Veracruz, QRoo, Yucatán,
OVICA (CDMX), Jalisco, IRCNL, Guanajuato, ICRESON.

## Tools

- `catastro_consultar_valor(sistema, cuenta_catastral)`
- `catastro_listar_sistemas()`

Ningún catastro estatal del catálogo publica consulta de valor por clave. IGECEM
devuelve handoff humano (trámite de constancia); el resto, `upstream_error` con
el motivo (login, info-only, portal caído). Mock solo con `PLUGINS_MX_MOCK=1`.

## Estado real (2026-10-14)

| Sistema | URL | Status | Resultado |
|---|---|---|---|
| igecem | https://igecem.edomex.gob.mx | 200 | Handoff (`/consulta-cuenta-catastral` da 404) |
| ircep | https://ircep.puebla.gob.mx | — | DNS inexistente → `upstream_error` |
| ircnl | https://catastro.ircnl.gob.mx/sgcnl/ | — | Cadena TLS incompleta; además requiere login |
| ovica_cdmx | https://ovica.finanzas.cdmx.gob.mx | 200 | Login → `upstream_error` |
