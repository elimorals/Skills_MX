---
description: Onboarding completo de un nuevo cliente con captura fiscal, contacto y contrato marco.
argument-hint: "<nombre-cliente>"
allowed-tools: Read, Write, Edit, Bash
---

# /freelancers:onboarding

Onboarding para: $ARGUMENTS

1. Invoca el skill `cliente-onboarding`.
2. Conduce el flujo de captura en 6 pasos: fiscal, contacto, comercial, operativo, compliance, generación.
3. Valida RFC con `rfc-validacion` mientras capturas.
4. Valida CP y régimen con `cfdi-emision`.
5. Genera ficha JSON en `clientes/[id]/ficha.json`.
6. Genera contrato marco pre-llenado en `clientes/[id]/contrato-marco.md`.
7. Genera aviso de privacidad con `compliance-lfpdppp` en `clientes/[id]/aviso-privacidad.md`.
8. Sugiere mensaje breve para mandar al cliente con los documentos para firma.
