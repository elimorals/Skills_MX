---
description: Descarga masiva de CFDIs emitidos+recibidos del ejercicio fiscal (12 meses).
---

Invoca el skill `recopilar-cfdis-anuales`.

Argumentos sugeridos:
- `ejercicio` (default: año previo si hoy > enero)
- `rfc` (de variable de sesión o env)

Si la e.firma no está configurada, devuelve datos sintéticos (mock).
Si está configurada y `PLUGINS_MX_PLAYWRIGHT_REAL=1`, orquesta descarga real via `mp_sat_portal` (tarda 4-24h por cola SAT).

Después de completar, sugiere al usuario el siguiente skill:
- Si quiere clasificar deducciones → `/pf-anual:dashboard` después
- Si quiere ir directo a cálculo → `/pf-anual:calcular`
