---
name: contrato-prestacion-servicios-legales
description: Genera un contrato de prestación de servicios profesionales jurídicos entre despacho o abogado y cliente, con base civil (Arts. 2606-2615 CCF para servicios profesionales y Arts. 2546 y ss. para el mandato, o el código civil del estado), con objeto específico del servicio (asesoría, litigio, gestión, dictamen, opinión), forma de cobro (iguala mensual, honorarios por etapas, cuota litis con desglose porcentual o esquema mixto), gastos y costas (a cargo de quién según el resultado), terminación anticipada con honorarios devengados, confidencialidad por secreto profesional, jurisdicción (por defecto la sede del despacho) y aviso de privacidad para datos sensibles del proceso. Diferencia asunto contencioso vs no contencioso para la cláusula de cuota litis. Usar cuando el usuario diga "contrato abogado", "honorarios legales", "cuota litis", "iguala mensual despacho", "contrato prestación servicios legales", "carta compromiso abogado", "engagement letter abogado". NO usar para contrato comercial general ni laboral.
allowed-tools: Read, Write, Edit
---

# Contrato de prestación de servicios profesionales — jurídico

## Cláusulas obligatorias

1. **Identificación**: nombres, RFC y cédula profesional del abogado. La cédula se puede consultar con `sep_consultar_cedula` (MCP `mp_sep_profesional`); si devuelve resultado nulo o pide captcha, entrega al usuario la URL del Registro Nacional de Profesionistas para que la verifique.
2. **Objeto**: específico del asunto (no genérico tipo "asesoría legal").
3. **Honorarios** (Art. 2606 CCF: las partes fijan la retribución de común acuerdo):
   - Iguala: monto mensual + IVA 16% − retenciones si el cliente es persona moral (PF 612: 10% ISR + 2/3 del IVA; PF RESICO 626: 1.25% ISR + 2/3 del IVA). Ver `cfdi-honorarios-d01`.
   - Por etapas: hito → monto, con un CFDI por cada etapa cobrada.
   - Cuota litis: % del beneficio obtenido, honorarios mínimos garantizados y qué pasa si se pierde.
4. **Gastos y costas**: normalmente a cargo del cliente; la cuota litis puede absorberlos. Pactar si el despacho los anticipa (Art. 2588 fr. II CCF) y cómo se reembolsan.
5. **Terminación anticipada**: honorarios devengados; obligación del abogado de avisar con oportunidad si deja el asunto (Art. 2614 CCF).
6. **Confidencialidad**: secreto profesional (Art. 36 de la Ley Reglamentaria del Art. 5o. Constitucional; la revelación de secretos es delito en los códigos penales, p. ej. Art. 213 del Código Penal de la CDMX).
7. **Datos personales**: aviso de privacidad con sección de datos sensibles del proceso (LFPDPPP 2025; ver `compliance-lfpdppp`).
8. **Jurisdicción**: por defecto la sede del despacho.
9. **Prescripción**: informar que la acción de cobro de honorarios prescribe en 2 años (Art. 1161 fr. I CCF), para fijar fechas de pago claras.

## Cláusula de cuota litis (especial)

> Requiere revisión del abogado titular. Algunos códigos de ética y leyes estatales de profesiones limitan el porcentaje o exigen pactarlo por escrito. Verifica la ley de profesiones del estado.

## Output

```
contratos-legales/<rfc-hash>/<expediente-id>/
  ├── contrato.md   (versión editable)
  └── contrato.pdf  (versión firma)
```

> El contrato es un borrador: debe revisarlo y firmarlo el abogado responsable.
