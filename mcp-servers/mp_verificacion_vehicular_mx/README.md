# mp_verificacion_vehicular_mx

Verificación vehicular: CDMX, EdoMex, HGO, MOR, PUE, TLAX, JAL.

## Tools

- `verificacion_consultar_estatus(placa, estado)` — CDMX: handoff humano a SAF (CAPTCHA). Otros: `upstream_error` explícito (no hay consulta pública por placa).
- `verificacion_proximo_periodo(placa, estado)` — color de engomado y meses según el calendario 2026 (solo Megalópolis).
- `verificacion_listar_programas()` — costos 2026 donde hay fuente; `null` donde no.

Mock solo con `PLUGINS_MX_MOCK=1`. Se eliminó el flujo que pedía el CAPTCHA por
env var / stdin: un agente podía leer la imagen y resolverlo, lo cual es un bypass.

## Estado real (2026-10-14)

| Qué | Fuente / URL | Resultado |
|---|---|---|
| Estatus CDMX | https://data.finanzas.cdmx.gob.mx/sma/Consultaciudadana (200, `captcha_code`) | Handoff humano |
| Calendario 2026 | SEDEMA, Gaceta 2-ene-2026 (vía Crónica, N+) | Corregido: amarillo ene–feb/jul–ago, rosa feb–mar/ago–sep, rojo mar–abr/sep–oct, verde abr–may/oct–nov, azul may–jun/nov–dic |
| Costo CDMX | El Universal 2026 | $765.45 (5.625 UMA + IVA) |
| Costo EdoMex | UnoTV 2026 | $469.24 hologramas 1 y 2 |

El calendario anterior del repo tenía los meses equivocados (p. ej. amarillo en mar/jul/nov).

## Tests

```bash
cd mcp-servers && .venv/bin/pytest -q mp_verificacion_vehicular_mx
```
