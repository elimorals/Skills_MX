---
description: Consulta predial en paralelo de toda tu cartera + genera dashboard XLSX consolidado con vencimientos, descuentos y plan de pagos priorizado.
argument-hint: "[ruta-a-propiedades.json] [opcional: --enviar-wa <tel>]"
---

Invoca el skill `dashboard-cartera-predial-xlsx` que a su vez orquesta el workflow `inmobiliaria-mx/workflows/cartera-predial-multi-municipio.workflow.js`.

Input esperado: archivo JSON con array de propiedades. Formato mínimo por propiedad:
```json
{"id": "...", "estado": "...", "municipio": "...", "cuenta_predial": "..."}
```

Si el usuario no provee archivo, pídele:
1. Listado de propiedades (puede ser texto libre, lo estructuras)
2. Si tiene RFC del cliente (opcional, para nombrar archivo)
3. Si quiere alerta WhatsApp con resumen (requiere número)

Output: ruta al XLSX generado + resumen en chat con totales.
