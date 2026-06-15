# mp_llave_mx

SSO ciudadano oficial gob.mx (Llave MX) + Portal Unificado de Trámites.

**Universo**: 130M habitantes.

## Tools

- `llave_autenticar(curp, password)` — token SSO 8h.
- `llave_validar_token(token)` — verifica vigencia.
- `llave_listar_tramites(categoria?, dependencia?)` — 20 trámites curados.
- `llave_detalle_tramite(clave)` — info trámite + requisitos.
- `llave_vincular_e_firma(curp)` — vincular FIEL al SSO.
