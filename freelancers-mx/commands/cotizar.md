---
description: Genera una cotización profesional formato MX para un cliente con scope específico.
argument-hint: "<cliente> [scope breve]"
allowed-tools: Read, Write, Edit, Bash
---

# /freelancers:cotizar

Genera cotización para: $ARGUMENTS

1. Invoca el skill `cotizacion-mxn`.
2. Si tienes ficha del cliente en `clientes/[id]/ficha.json`, úsala para datos fiscales.
3. Si no, invoca `cliente-onboarding` brevemente para recopilar lo mínimo necesario.
4. Pregunta al usuario por scope detallado:
   - Entregables específicos
   - Cronograma sugerido
   - Esquema de pago (anticipo + saldo, hitos, etc.)
5. Invoca `iva-retenciones-mx` para calcular IVA y retenciones correctas según régimen del emisor y receptor.
6. Genera la cotización en markdown y guárdala en `cotizaciones/YYYY-MM-DD-[cliente]-[serie].md`.
7. Pregunta si quiere versión PDF (usa skill `pdf` del sistema) o Word (skill `docx`).
8. Sugiere mensaje breve para mandar al cliente junto con el documento.
