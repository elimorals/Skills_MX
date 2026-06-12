---
description: Evalúa un inquilino candidato (RFC + Buró con autorización + ingresos + referencias).
---

Invoca `screening-inquilino-completo`.

⚠ Requiere `autorizacion_token` (≥16 chars) que confirme autorización formal del candidato para consulta a Buró. Sin esto, el skill aborta — consultar Buró sin autorización es DELITO.

Output: recomendación de decisión (APROBADO / APROBADO_CON_DEPOSITO_MAYOR / RECHAZADO) + razones.
