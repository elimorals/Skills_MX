---
description: Busca multas pendientes por placa en portales municipales y prepara pago.
---

Invoca `multas-deteccion-pago`. Cruza con tracker de placas + consulta `mp_cdmx_municipal`/`mp_edomex_municipal`/`mp_monterrey_municipal` según entidad.

Output: lista de multas con línea de captura + monto con descuento por pronto pago si aplica.
