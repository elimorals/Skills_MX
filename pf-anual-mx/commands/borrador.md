---
description: Genera PDF borrador de la declaración anual lista para revisar/presentar.
---

Invoca `generar-borrador-declaracion`.

Requisitos:
- Cálculo previo hecho (vía `/pf-anual:calcular`)
- Librería PDF instalada (`reportlab` o `weasyprint`)

Output: PDF en `~/.local/share/plugins-mx/declaraciones/<ejercicio>/<rfc_hash>-borrador.pdf` + resumen.

⚠ El PDF NO se presenta automáticamente al SAT. Es solo para revisión y carga manual en DeclaraSAT.
