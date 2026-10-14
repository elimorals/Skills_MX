# mp_tenencia_mx

Tenencia + refrendo vehicular 2026 por estado. Cálculo local con montos
citados; no hay tasas planas ni factores de depreciación inventados.

## Tools

- `tenencia_calcular(estado, valor_factura, anio_modelo)` — subsidio, tenencia y refrendo.
- `tenencia_info_estado(estado)` — reglas, fuentes y confianza del estado.
- `tenencia_listar_estados(solo_con_tenencia)`
- `tenencia_comparar_estados(estados, valor_factura, anio_modelo)` — los estados sin monto verificado van en `sin_monto_verificado`.

## Reglas de cálculo

- Bajo el umbral de subsidio (valor factura con IVA): `tenencia_mxn = 0` y
  `subsidio_100_elegible = true` (sujeto a `condiciones_subsidio`).
- Arriba del umbral: `tenencia_mxn = null` y `requiere_calculo_oficial = true`.
  La tarifa progresiva de cada código fiscal no se verificó contra el texto 2026.
- Refrendo sin fuente 2026: `refrendo_mxn = null`.

## Estado real (2026-10-14)

Es un cálculo local: no consulta portales. Montos verificados contra notas de
prensa 2026 que citan a las secretarías de finanzas (no se localizó el acuerdo
de subsidio en gaceta, por eso confianza "media" como máximo).

| Estado | Tenencia 2026 | Refrendo 2026 | Confianza | Fuente |
|---|---|---|---|---|
| CDMX | subsidio 100% si factura ≤ $638,000 | $760 | media | Infobae 31-mar-2026, Récord |
| EdoMex | subsidio 100% si factura ≤ $638,000 (placas 2021+) | $990 | media | N+, UnoTV |
| Querétaro | "Cero Tenencia" < $800,000 | variable ($760–$1,300) → null | media | El Congresista, Infobae |
| Jalisco | no cobra | $1,000 | baja (UnoTV dice $1,100) | ADN40 3-mar-2026 |
| NL, PUE, MOR, HGO, OAX, TLAX | no confirmado | ver catálogo / null | baja | UnoTV 2026 |

Se retiraron del catálogo los estados sin ninguna fuente 2026 (BC, BCS, CAM,
CHIH, SIN, TAM, AGS, YUC, MICH, SLP, GTO, SON, VER): sus montos anteriores no
tenían respaldo.

## Tests

```bash
cd mcp-servers && .venv/bin/pytest -q mp_tenencia_mx
```
