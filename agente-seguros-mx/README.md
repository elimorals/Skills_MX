# agente-seguros-mx

Plugin para agentes y promotores de seguros independientes autorizados CNSF en México. Cubre múltiples ramos: auto, GMM, vida, daños, fianzas. Construido sobre `core-mexico` + `gmm-asegurado-mx`.

## Skills propios (5)

| Skill | Propósito |
|---|---|
| `cartera-polizas` | Registro + alertas vencimiento 60-30-7 días |
| `calculador-comisiones-aseguradoras` | % por ramo + bonos + CFDI honorarios a aseguradora |
| `comparador-polizas-cliente` | Cuadro comparativo multi-aseguradora con calidad servicio |
| `seguimiento-siniestro` | Bitácora end-to-end + plazos CNSF + escalación CONDUSEF |
| `recordatorios-renovacion` | Cadencia 60-30-7 con personalización por ramo + KPI |

## Comandos (4)

- `/agente-seguros:registrar-poliza`
- `/agente-seguros:cotizar-comparativa`
- `/agente-seguros:seguimiento-siniestro`
- `/agente-seguros:cobrar-comisiones`

## Compliance crítico

- **CNSF**: autorización vigente del agente + cédula de identificación
- **30 días naturales** plazo legal aseguradora para resolver siniestro
- **CONDUSEF**: vía de queja cuando aseguradora rechaza sin base o se excede el plazo
- **LISF + UMA**: regulación específica por ramo (vida vs daños vs salud)
- **LFPDPPP**: datos sensibles del asegurado especialmente GMM

## Aseguradoras cubiertas (típicas)

AXA, GNP, Quálitas, Mapfre, MetLife, Allianz, Inbursa, BUPA, Seguros Monterrey, ANA, Banorte Seguros.

## Validación pendiente

⚠ Score honesto: 4.5/9 inicial. Para producción-grade:
- Tabla de comisiones debe confirmarse con contratos reales del agente (varían por aseguradora)
- Templates WhatsApp aprobados Meta antes de campañas masivas
- Validar plazos CNSF vigentes (puede cambiar con reforma)
- Partner agente con cartera 100+ pólizas para dogfooding

## Ver también

- `gmm-asegurado-mx/README.md` — dependencia para reembolsos del asegurado
- `docs/specs/` (pendiente spec agente-seguros)
