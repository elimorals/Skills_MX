# talleres-mx

Plugin para talleres mecánicos y servicios automotrices operando en México (~150,000+ talleres independientes).

## Skills propios

| Skill | Propósito |
|---|---|
| `diagnostico-cotizacion` | Flow estructurado de diagnóstico → cotización con desglose |
| `autorizacion-cliente-wa` | Autorización del cliente vía WhatsApp con foto/video del problema |
| `garantia-servicio` | Términos de garantía PROFECO + gestión de reclamos |
| `orden-trabajo` | OT con desglose mano de obra + refacciones, firma digital |

## Skills heredados de `core-mexico`

CFDI, IVA, RFC, WhatsApp Business, LFPDPPP, MXN.

## Commands

- `/talleres:nuevo-diagnostico [cliente] [auto]`
- `/talleres:autorizacion [OT]`
- `/talleres:orden-trabajo [OT]`
- `/talleres:garantia [auto/OT]`

## Usuario objetivo

- Dueño de taller mecánico (1-15 empleados)
- Refaccionaria con servicio (mostrador + taller)
- Servicio electromecánico especializado

## Problema endémico que resuelve

El flujo roto en talleres MX:
- Cliente deja auto → diagnóstico verbal → cotización por WhatsApp ambiguo → cliente no responde → auto detenido en taller → conflicto.

Este plugin estructura el flow para que:
1. Diagnóstico documentado con foto/video.
2. Cotización clara con plazos.
3. Autorización digital del cliente registrada.
4. OT firmada al inicio.
5. Garantía con términos claros.

## Estado

`v0.1.0` — scaffolding inicial.

## Marco legal MX

- **Ley Federal de Protección al Consumidor (PROFECO)**: garantía mínima en servicios. Para reparación de automotores: 30 días mínimo en mano de obra y 90 días en refacciones nuevas instaladas.
- **CFDI por servicios de reparación**: ClaveProdServ 78180100 (servicios de mantenimiento/reparación de vehículos).
- **Refacciones**: se facturan separadas con su propia ClaveProdServ del catálogo de partes.
