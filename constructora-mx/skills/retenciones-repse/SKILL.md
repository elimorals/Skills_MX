---
name: retenciones-repse
description: Calcula la retención de IVA de 6% del valor de la contraprestación (Art. 1-A fr. IV LIVA, no 6% del IVA) que la constructora persona moral o PFAE hace cuando un subcontratista le pone personal a disposición, y valida antes de pagar que el proveedor de servicios especializados tenga registro REPSE vigente en el padrón de la STPS. Distingue servicios especializados con personal (REPSE y retención) de suministro de materiales, renta de equipo sin operador u obra que el contratista ejecuta con su propia dirección. Revisa los requisitos para deducir y acreditar (Art. 27 fr. V LISR, Art. 5 fr. II LIVA): CFDI de nómina, pagos IMSS e INFONAVIT y declaración de IVA del contratista. Usar cuando el usuario diga "retención REPSE", "subcontratista construcción", "6% IVA servicios especializados", "retención 6%", "padrón STPS subcontratistas". NO usar para retenciones de salarios ni de honorarios profesionales (10% ISR).
allowed-tools: Read, Write, Edit
---

# Retenciones REPSE — subcontratistas construcción

## Marco legal

- Reforma de subcontratación (DOF 23-04-2021): Art. 15 LFT y Art. 15-A LSS
- Art. 1-A fr. IV LIVA: retención de 6% del valor de la contraprestación
- Art. 27 fr. V LISR y Art. 5 fr. II LIVA: requisitos para deducir y acreditar
- Padrón REPSE de la STPS (registro renovable cada 3 años)

## ¿Cuándo hay retención de 6%?

La retención aplica cuando el proveedor pone personal a disposición del contratante (en sus instalaciones o fuera), con independencia del nombre del contrato. El análisis es de hecho: valida con contador.

| Escenario | ¿REPSE? | Retención IVA |
|---|---|---|
| Subcontratista especializado con su personal en tu obra (instalación eléctrica, herrería) | Sí, si es servicio especializado | 6% del valor |
| Obra completa que el contratista ejecuta con su propia dirección y riesgo | Revisar caso por caso | Revisar |
| Suministro de materiales | No | No |
| Renta de equipo sin operador | No | No |
| Renta de equipo con operador | Revisar: el operador es personal a disposición | Probable 6% |
| Persona física que presta el servicio sola, sin trabajadores | No es subcontratación laboral | Retenciones de PF según su régimen |

## Validación previa REPSE

Antes de contratar y antes de cada pago:
1. `repse_verificar_proveedor` (MCP `mp_repse_stps`, validado en vivo) por RFC, razón social o número de registro. El objeto del contrato debe coincidir con las actividades registradas.
2. Sin registro vigente: la subcontratación está prohibida, el gasto no es deducible, el IVA no es acreditable y respondes solidariamente por las obligaciones laborales (Art. 15 LFT).
3. Pide cada mes: CFDI de nómina de los trabajadores asignados, comprobantes de pago de cuotas IMSS y aportaciones INFONAVIT, y declaración de IVA con acuse.
4. El contratista presenta cada cuatrimestre sus informativas ICSOE (IMSS) y SISUB (INFONAVIT); pide copia del acuse.

## Cálculo y CFDI

- **6% del valor de la contraprestación sin IVA**. Ej.: servicio $100,000 + IVA $16,000 → retención $6,000 → pagas $110,000.
- En el CFDI del subcontratista la retención va como IVA retenido con TasaOCuota `0.060000`.
- Entera la retención a más tardar el día 17 del mes siguiente.
- CFDI de Retenciones e información de pagos (estándar Retenciones 2.0, no es un TipoDeComprobante de CFDI 4.0) cuando se lo pidan o aplique.

## ⚠ Compliance

La calificación de un servicio como especializado y la procedencia de la retención requieren revisión de contador o abogado laboral.
