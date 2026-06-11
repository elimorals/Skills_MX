---
description: Captura nuevo diagnóstico de vehículo y genera cotización estructurada con desglose mano de obra + refacciones.
argument-hint: "<cliente> <auto: marca-modelo-año>"
allowed-tools: Read, Write, Edit, Bash
---

# /talleres:nuevo-diagnostico

Diagnóstico para: $ARGUMENTS

1. Invoca `diagnostico-cotizacion`.
2. Captura datos del vehículo (marca, modelo, año, VIN, placas, km, color).
3. Captura datos del propietario y si requiere CFDI.
4. Captura síntomas verbatim del cliente.
5. Estructura diagnóstico técnico con hallazgos categorizados (urgente / recomendado / opcional).
6. Genera cotización con desglose MO + refacciones con marca/parte y resumen económico con IVA.
7. Solicita fotos/video del problema para incluir.
8. Guarda en `diagnosticos/[fecha]-[placas]/diagnostico.md`.
9. Genera mensaje resumido para enviar al cliente por WhatsApp con `autorizacion-cliente-wa`.
