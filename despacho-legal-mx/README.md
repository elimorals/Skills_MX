# despacho-legal-mx

Plugin para despachos jurídicos en México: abogados litigantes, fiscalistas, mercantilistas, laboralistas. Construido sobre `core-mexico`.

## Skills propios (5)

| Skill | Propósito |
|---|---|
| `expediente-cliente-legal` | Alta + estructura de carpetas + aviso ARCO específico legal |
| `contrato-prestacion-servicios-legales` | Iguala / honorarios / cuota litis con cláusulas vigentes |
| `cfdi-honorarios-d01` | CFDI por honorarios con retenciones correctas por régimen |
| `cobranza-litigio` | Cobranza con sensibilidad al estado del proceso del cliente |
| `bitacora-actuaciones` | Log procesal por expediente (defensa por mala práctica + facturación) |

Hereda 6 skills `_shared/` (cfdi-emision, iva-retenciones-mx, rfc-validacion, whatsapp-business-mx, compliance-lfpdppp, mxn-formato).

## Comandos (4)

- `/despacho-legal:expediente-nuevo`
- `/despacho-legal:registrar-actuacion`
- `/despacho-legal:facturar-honorarios`
- `/despacho-legal:cobranza-litigio`

## Casos de uso típicos

1. **Onboarding cliente nuevo en litigio**: validación RFC + 69-B + conflicto interés + contrato + aviso privacidad → expediente foliado.
2. **Cobro iguala mensual**: CFDI honorarios + retenciones régimen + envío WhatsApp + tracking.
3. **Defensa por mala práctica**: bitácora de actuaciones como prueba de diligencia debida.
4. **Cuota litis al éxito**: contrato con desglose + emisión CFDI proporcional al beneficio obtenido.

## Validación pendiente

⚠ Score honesto: scaffolding 4.5/9 inicial. Para producción-grade:
- Abogado mercantilista debe revisar `contrato-prestacion-servicios-legales` (especialmente cláusula cuota litis y jurisdicción)
- Validar cumplimiento Art. 36 LGM (secreto profesional) en `aviso-privacidad` específico legal
- Templates WhatsApp aprobados por Meta antes de cobranza masiva

## Ver también

- `docs/specs/` (pendiente spec específico para despacho-legal)
- `docs/analisis-profundo-2026-06.md` — gap general
