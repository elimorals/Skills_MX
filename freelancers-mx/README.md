# freelancers-mx

Plugin para freelancers, consultores y agencias unipersonales operando en México.

## Instalación

```bash
/plugin marketplace add elimorals/Skills_MX
/plugin install core-mexico --marketplace elimorals/Skills_MX   # base de todos los verticales
/plugin install freelancers-mx --marketplace elimorals/Skills_MX
```

Los MCPs del plugin se descargan solos con [`uv`](https://docs.astral.sh/uv/) la primera vez. Sin credenciales responden datos de ejemplo marcados `simulated: true`; con credenciales, los errores del proveedor se propagan. Estado por MCP: [`mcp-servers/CATALOGO.md`](../mcp-servers/CATALOGO.md).

## Skills propios

| Skill | Propósito |
|---|---|
| `cotizacion-mxn` | Cotización profesional formato MX con IVA, retenciones, vigencia, términos de pago |
| `propuesta-comercial` | Propuesta con scope, deliverables, milestones, payment schedule, T&Cs |
| `cobranza-seguimiento` | Flujo escalado de cobranza (5 etapas: recordatorio amable → bloqueo de servicio) |
| `cliente-onboarding` | Captura completa de datos fiscales del cliente (RFC, régimen, CFDI, dirección) + contrato marco |
| `freelance-tax-mx` | Cálculo de pago provisional ISR para PFAE (612) y RESICO (626 PF) |

## Skills heredados de `core-mexico`

`cfdi-emision`, `iva-retenciones-mx`, `rfc-validacion`, `whatsapp-business-mx`, `compliance-lfpdppp`, `mxn-formato`.

## Commands

- `/freelancers:cotizar [cliente] [scope]` — genera cotización formal
- `/freelancers:propuesta [cliente] [proyecto]` — propuesta comercial completa
- `/freelancers:cobranza [cliente]` — siguiente paso de cobranza
- `/freelancers:onboarding [cliente]` — captura datos nuevo cliente
- `/freelancers:pago-provisional [mes]` — cálculo del mes para SAT

## Quién es el usuario objetivo

- Consultor tech (full-stack, DevOps, IA) facturando entre $50k y $300k MXN/mes
- Diseñador, copywriter, fotógrafo, productor con clientes recurrentes
- Agencia unipersonal o de hasta 3 personas
- Régimen 612 (PFAE) o 626 (RESICO PF) — son ~95% de los freelancers en MX

## Filosofía

Reducir el tiempo administrativo del freelancer **al menos un 60%**. El tiempo de un freelancer vale $400-$1,500 MXN/hora; cada hora ahorrada en cotizar, cobrar, facturar y declarar es revenue real.

## Estado

`v0.1.0` — scaffolding inicial. Skills propios en estado de plantilla denso; afinar con dogfooding.
