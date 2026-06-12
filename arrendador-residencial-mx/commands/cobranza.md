---
description: Corrida de cobranza escalada para inquilinos morosos (5 niveles).
---

Invoca `cobranza-mensual-renta` para cada propiedad con días de mora > 0.

Determina nivel de escalamiento (1-5) según días + historial del inquilino. Genera plantilla WA/email con tono adaptado.

Niveles:
- 1: D-3 recordatorio pre-vencimiento
- 2: D+3 amable
- 3: D+7 firme
- 4: D+15 formal (escrito documentado)
- 5: D+30 protocolo desalojo (requiere abogado + notario)
