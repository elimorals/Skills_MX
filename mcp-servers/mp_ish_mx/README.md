# mp_ish_mx

Impuesto sobre Hospedaje (ISH) — 27 estados MX que lo cobran (5 sin ISH).

Cálculo offline. Combo con `airbnb-host-mx`. Tasas 1.5% - 5%.

## Tools

- `ish_calcular(estado, monto_hospedaje)` → ISH + total con impuesto.
- `ish_info_estado(estado)` → config + portal.
- `ish_listar_estados(solo_aplicables)` → 32 entidades.
- `ish_comparar_estados([...], monto)` → ranking barato a caro.
