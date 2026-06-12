---
name: retenciones-repse
description: Calcula retenciones REPSE (Padrón Público de Contratistas de Servicios Especializados) que la constructora hace a subcontratistas registrados en el padrón, aplicando 6% de IVA por servicios especializados (vigente desde reforma 2021 outsourcing) y validando que el proveedor tenga registro REPSE activo vía padrón STPS. Diferencia entre prestación de servicios especializados (REPSE aplica) y obra cerrada por precio alzado (no aplica REPSE típicamente). Genera CFDI de retenciones y pagos (Tipo Retenciones del SAT) que el contratista debe expedir al subcontratista por las retenciones efectuadas. Cubre validación previa del estado REPSE del proveedor para evitar gastos no deducibles, declaración informativa mensual de subcontratación al SAT (Art. 27 LISR), y registro de la operación para que el subcontratista pueda acreditar las retenciones. Usar cuando el usuario diga "retención REPSE", "subcontratista construcción", "6% IVA servicios especializados", "Art. 27 LISR retención", "padrón STPS subcontratistas". NO usar para retenciones de salarios ni para retenciones de honorarios profesionales (10% ISR).
allowed-tools: Read, Write, Edit
---

# Retenciones REPSE — subcontratistas construcción

## Marco legal

- Reforma 2021 outsourcing
- Art. 27 LISR fracc. V — informativa subcontratación
- Acuerdo STPS REPSE — padrón de contratistas
- Anexo 20 SAT — campos del CFDI

## Cuándo aplica retención del 6% IVA

| Escenario | ¿REPSE aplica? | Retención |
|---|---|---|
| Servicio especializado (electricista, plomero, herrero contratado a hora) | Sí | 6% IVA |
| Obra cerrada precio alzado | Típicamente no | No |
| Suministro de materiales | No | No |
| Renta de equipo sin operador | No | No |
| Renta de equipo con operador | Sí | 6% IVA |

## Validación previa REPSE

Antes de pagar al subcontratista:
1. Consultar estado REPSE en padrón STPS (`mp_imss_patronal` o consulta manual)
2. Si NO está en REPSE: gastos NO deducibles + sin acreditamiento de IVA
3. Si está pero VENCIDO: pendiente renovar — riesgo

## CFDI de retenciones

Por cada subcontratista REPSE, mensualmente:
- CFDI tipo R (Retenciones y pagos)
- Concepto: "Retenciones por servicios especializados Art. 27 LISR"
- ImpRetenido = 6% del IVA trasladado
