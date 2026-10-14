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

No se intenta pasar el bot manager. Mock solo con `PLUGINS_MX_MOCK=1`.
