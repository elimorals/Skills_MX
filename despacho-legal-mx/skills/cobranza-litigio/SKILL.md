---
name: cobranza-litigio
description: Gestiona la cobranza de honorarios legales con una escalación distinta a la cobranza comercial, porque considera el estado del proceso judicial (no presionar al cliente cuando tiene una audiencia clave en los próximos días), el riesgo de queja ante el colegio de abogados por presión indebida y las cantidades del cliente que el despacho tenga en su poder. Etapas: recordatorio D+5 cordial, D+15 llamada o cita, D+30 propuesta de pago en parcialidades, D+45 carta formal y, si procede, aviso de renuncia al patrocinio con la anticipación debida (Arts. 2603 y 2614 CCF), D+60 o más demanda civil de cobro de honorarios antes de que prescriban (2 años, Art. 1161 fr. I CCF). Diferencia entre cliente PF (más cuidado) y PM (más opciones). Usar cuando el usuario diga "cobranza despacho", "cobrar honorarios legales", "iguala vencida", "cliente abogado no paga", "morosidad legal", "demandar honorarios". NO usar para cobranza comercial común (usar cobranza-seguimiento) ni para juicio ejecutivo de terceros.
allowed-tools: Read, Write, Edit
---

# Cobranza de honorarios en despacho legal

## Diferencias vs cobranza comercial

1. **Estado del proceso**: NO presionar antes de audiencias clave.
2. **Dinero del cliente en poder del despacho**: el mandatario debe entregar al mandante lo recibido por el poder (Art. 2570 CCF). Solo se compensa contra honorarios si el contrato lo autoriza por escrito o el cliente lo acepta; documenta cada movimiento.
3. **Dejar el asunto**: el abogado que deja de prestar el servicio debe avisar con oportunidad o responde por daños (Art. 2614 CCF) y, como mandatario, debe seguir el negocio mientras el cliente nombra a otro si de lo contrario hay perjuicio (Art. 2603 CCF). Nunca abandones un plazo corriendo.
4. **Queja profesional**: la presión indebida puede generar queja ante el colegio o barra si el abogado está colegiado.

## Etapas

| Día | Acción | Tono |
|---|---|---|
| D+5 | WhatsApp cordial: "tu pago de iguala de enero, ¿cómo vas con él?" | Suave |
| D+15 | Llamada o cita para revisar el tema | Conversacional |
| D+30 | Propuesta de pago en parcialidades | Formal |
| D+45 | Carta formal por escrito; si no hay arreglo, aviso de renuncia al patrocinio con anticipación suficiente | Severo |
| D+60+ | Demanda civil de cobro de honorarios (si el saldo y el patrimonio del deudor lo justifican) | Legal |

## Vía judicial

- La prestación de servicios profesionales es un contrato civil (Arts. 2606-2615 CCF o su equivalente estatal): la demanda es civil, no mercantil, salvo que el cliente haya firmado un título de crédito (pagaré), que permite vía ejecutiva mercantil.
- **Prescripción**: los honorarios prescriben en 2 años desde que se dejaron de prestar los servicios (Art. 1161 fr. I CCF). Revisa el código civil del estado.
- **Código procesal**: el Código Nacional de Procedimientos Civiles y Familiares entra en vigor por estado mediante declaratoria, a más tardar el 1-abr-2027. Confirma cuál rige en el juzgado competente antes de preparar la demanda.

## Validaciones críticas

- ANTES de cualquier acción: revisar la agenda judicial del cliente (`bitacora-actuaciones`).
- Si hay audiencia en los próximos 5 días: posponer la cobranza.
- DOCUMENTAR cada intento en la bitácora del expediente.
- Si el despacho va a dejar el asunto: notificar por escrito al cliente, indicar plazos pendientes y entregar el expediente.

> Revisión profesional: la decisión de renunciar al patrocinio o demandar la toma el abogado titular.
