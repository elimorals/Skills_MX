---
name: inscripcion-alumno-curso
description: Onboarding de un alumno a un curso de academia particular o en línea: datos básicos, aviso de privacidad (LFPDPPP 2025) y consentimiento del padre o tutor si es menor, asignación de curso y grupo, condiciones de pago informadas por escrito (precio con IVA, política de cancelación y reembolso), cobro del primer mes y datos fiscales para CFDI. Usar cuando el usuario diga inscripción alumno curso, inscribir alumno, alta de alumno, nuevo alumno academia, registro a curso en línea.
allowed-tools: Read, Write
---

# Inscripción de alumno a curso

## Datos mínimos

- Nombre completo, email y WhatsApp
- Fecha de nacimiento (para saber si es menor de edad)
- Si es menor: nombre y contacto del padre, madre o tutor, quien firma y paga
- Curso, grupo u horario y fecha de inicio
- Datos fiscales solo si pide factura: RFC, nombre, CP y régimen de su constancia (si no, factura global a público en general)

Pide solo lo necesario. CURP únicamente si el curso tiene RVOE o se emitirá DC-3.

## Avisos y consentimiento

- Aviso de privacidad antes de recabar datos (LFPDPPP publicada DOF 20-03-2025; la autoridad es la Secretaría Anticorrupción y Buen Gobierno). Para menores, consentimiento del padre o tutor. Ver `compliance-lfpdppp`.
- Opt-in para WhatsApp (avisos del curso) y opt-in separado para promociones.

## Condiciones de pago (por escrito antes de cobrar)

- Precio total con IVA (16% si el curso no tiene RVOE). Publica precios con IVA incluido para el consumidor final (LFPC).
- Periodicidad, fecha de cargo, recargos (si los hay) y política de cancelación y reembolso.
- Si es suscripción, cómo cancelarla.

## Primer pago

- Link de pago: `conekta_create_payment_link` (MCP `mp_conekta`) o `mercadopago_create_preference` (MCP `mp_mercado_pago`); requieren credenciales, sin ellas modo mock y se comparte CLABE para SPEI.
- Para cargos recurrentes, crea la suscripción desde `cobranza-recurrente-cursos`.
- Emite el CFDI al cobrar con `cfdi-mensualidad-curso`.

## Output esperado

```json
{
  "operation": "inscripcion-alumno-curso",
  "data": {
    "alumno_hash": "…",
    "es_menor": false,
    "curso": "Inglés B1 sabatino",
    "inicio": "2026-11-07",
    "precio_mensual_con_iva": "1740.00",
    "aviso_privacidad_aceptado": true,
    "optin_whatsapp": true,
    "requiere_factura": false,
    "primer_pago": "pendiente"
  },
  "vigencia_validada": true
}
```

Guarda los datos en el tracker local con identificadores hasheados.
