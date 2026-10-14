# mp_clabe_validador_oficial

Validador de CLABE: dígito de control con el algoritmo oficial (pesos 3,7,1)
y banco confirmado contra el catálogo vigente de participantes SPEI de Banxico.

No existe un servicio público que confirme que una cuenta concreta existe o
quién es su titular; eso solo lo confirma el banco al recibir un SPEI (o el
CEP, ver `mp_banxico_cep`).

## Tools

- `clabe_validador_validar_clabe(clabe)` — estructura + dígito + participante SPEI vigente.
- `clabe_validador_info_banco_clabe(codigo_o_clabe)` — institución SPEI para un código de 3 dígitos o una CLABE.

## Estado real

| Fecha | URL | Resultado |
|---|---|---|
| 2026-10-14 | `GET https://www.banxico.org.mx/cep/instituciones.do?fecha=DD-MM-YYYY` | 200 JSON (catálogo SPEI); test live `012` → BBVA MEXICO |

- Estado: **real validado**.
- Catálogo cacheado 24 h. Si Banxico falla → `UpstreamError` (sin fallback).
- Mock solo con `PLUGINS_MX_MOCK=1` (`simulated: true`).

Test live: `PLUGINS_MX_LIVE=1 .venv/bin/pytest mp_clabe_validador_oficial -m live`.

## Credenciales

Ninguna.
