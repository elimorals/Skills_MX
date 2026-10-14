# mp_llave_mx

Llave MX (SSO ciudadano gob.mx) por OAuth2 + datos abiertos de adopción.

## Tools

- `llave_iniciar_oauth(redirect_url, state?)` — arma la URL de autorización
  `oauthV2.xhtml?client_id&redirect_url&state` con `LLAVE_MX_CLIENT_ID` (alta con la ATDT).
  Sin client_id → `ConfigError`.
- `llave_estado_endpoints()` — **real**: ¿llave.gob.mx responde y redirige a OAuth?
- `llave_estadisticas_adopcion(entidad?)` — **real**: altas de usuarios por entidad y mes
  (dataset `usuarios_sistema_llave_mx`, ATDT, CC-BY-4.0).
- `llave_validar_token(token)` — no hay endpoint público de introspección → `ConfigError`.
- `llave_listar_tramites` / `llave_detalle_tramite` — catálogo orientativo (`verificado: false`).
- `llave_vincular_e_firma(curp)` — handoff al titular.

`llave_autenticar(curp, password)` se retiró: un tercero no debe recibir la contraseña del
ciudadano, y el formulario de Llave MX tiene CAPTCHA.

## Estado real

Validado en vivo 2026-10-14:

| URL | Status | Resultado |
|---|---|---|
| https://www.llave.gob.mx/ | 200 | redirige a `oauthV2.xhtml?client_id=…&redirect_url=…&state=…`; form `frmLogin` (correo + contraseña) con CAPTCHA |
| https://www.llave.gob.mx/.well-known/openid-configuration | 404 | sin discovery OIDC |
| datos.gob.mx `package_show?id=usuarios_sistema_llave_mx` | 200 | 3 recursos CSV |
| CSV oct-2024 a may-2025 (datos.gob.mx) | 200 | 225 filas, 8,439,610 altas |
| CSV ene/feb-2026 (repodatos.atdt.gob.mx) | 403 | Akamai bloquea clientes no-navegador |

El canje de código por token y su URL no son públicos: se obtienen en el convenio con la ATDT.
Fixture: `tests/fixtures/nuevos_usuarios.csv`. Live: `PLUGINS_MX_LIVE=1 pytest mp_llave_mx -k live`.
