---
name: cfdi-honorarios-d01
description: Emite CFDI 4.0 tipo Ingreso por honorarios profesionales legales (UsoCFDI G03 si cliente lo declara deducible, D01 si es PF que paga honorarios médicos/dentales/hospitalarios — para legales típicamente G03), con clave de producto/servicio 80101502 (servicios legales), tasa IVA 16% trasladado al cliente, retenciones cuando receptor es PM (10% ISR + 10.67% IVA si emisor es PFAE 612; sin retención si RESICO 626), forma de pago consistente con cuándo se cobró (PUE si cobrado al emitir, PPD si se cobra después), y método de pago coherente con el medio (TDC, SPEI, efectivo, etc.). Diferencia entre iguala mensual y honorarios por etapa para ObjetoImp. Usar cuando el usuario diga "factura abogado", "CFDI honorarios legales", "facturar iguala", "facturar honorarios despacho", "factura por servicios legales". NO usar para CFDI de retenciones del despacho hacia subagentes ni para CFDI tipo P (REP).
allowed-tools: Read, Write, Edit
---

# CFDI de honorarios legales

## Configuración correcta

- **TipoComprobante**: I (Ingreso)
- **UsoCFDI**: G03 (gastos en general — el más común para despachos a empresas) o D01 (honorarios médicos — NO para legales)
- **ClaveProdServ**: `80101502` (servicios legales)
- **ClaveUnidad**: `E48` (unidad de servicio)
- **ObjetoImp**: `02` (sí objeto de impuesto)

## Retenciones por escenario

| Receptor | Emisor | Retiene ISR | Retiene IVA |
|---|---|---|---|
| PM | PFAE 612 | 10% | 10.67% (2/3) |
| PM | RESICO 626 | 1.25% | 0 |
| PF | cualquier | 0 | 0 |

## Validación pre-timbrado

1. RFC receptor en padrón
2. CP receptor válido
3. Si retención calculada, debe estar reflejada en Impuestos.Retenciones
4. Total = subtotal + IVA − ISR retenido − IVA retenido
5. Forma + método consistente (PUE↔específico, PPD↔99)

## Output

JSON listo para `mp_facturama_extendido.timbrar_cfdi` + bitácora.
