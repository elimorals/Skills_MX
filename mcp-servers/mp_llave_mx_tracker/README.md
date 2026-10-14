# mp_llave_mx_tracker

Tracker público de adopción **Llave MX** por dependencia federal y estatal.

**Universo**: 20 dependencias monitoreadas (15 federales + 5 estatales).
**Producto**: para ATDT, IMCO, México Evalúa, prensa especializada.

## Tools

- `llave_mx_listar_dependencias(nivel?)` — lista filtrable por federal/federal_autonomo/estatal.
- `llave_mx_estatus_dependencia(clave)` — status curado (marcado `status_curado_verificado: false`)
  + detección en vivo del 2026-10-14.
- `llave_mx_estadisticas_nacionales()` — conteos por status curado y por detección en vivo.
- `llave_mx_verificar_en_vivo(clave)` — **real**: GET a la portada y detección de OAuth, enlace
  o mención de Llave MX.

## Estado real

Real por defecto (httpx, sin Playwright, sin fallback). Mock solo con `PLUGINS_MX_MOCK=1`.
Portal caído, 403 o captcha → `deteccion: inaccesible` (dato, no error).

Pasada completa 2026-10-14 (20 portadas, 5 s entre hosts):

| Detección | Dependencias |
|---|---|
| `enlace_llave_gob_mx` | bc (la portada enlaza a www.llave.gob.mx; el status curado decía "no_integrado") |
| `inaccesible` | imss (403), infonavit (403 Akamai), sre_pasaporte (captcha Radware) |
| `no_detectado_en_portada` | sat, issste, sep, ine, renapo, profeco, cofepris, cre, conagua, atdt, gobmx, bienestar, cdmx, edomex, jal, nl |

Límite: solo se revisa la portada. `no_detectado_en_portada` no prueba que el portal no use
Llave MX en un login interno (p. ej. atdt y gobmx, curados como "integrado").

Se retiró la "meta LNETB 2030 del 80 %" y la cita a "Lineamientos SIDOF 2025": no se encontró
sustento verificable. Live: `PLUGINS_MX_LIVE=1 pytest mp_llave_mx_tracker -k live`.
