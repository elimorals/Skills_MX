---
name: calculador-comisiones-aseguradoras
description: Calcula comisiones que el agente de seguros debe recibir de cada aseguradora con tabla de porcentajes vigentes por ramo (auto típicamente 15-25%, GMM 10-15%, vida 30-50% primer año + 5-10% renovaciones, daños 8-15%, fianzas 8-12%), descuento de bonos de calidad cuando aplica (siniestralidad baja eleva comisión), retención de premium tax cuando aplica para vida (ISR sobre comisión de PFAE 612), y emisión de CFDI de honorarios para cobrar a la aseguradora (régimen 612 con 10% ISR + 10.67% IVA retenido por la aseguradora PM, o régimen 626 con 1.25% ISR). Cubre comisiones de subagentes con cálculo del % a transferir según contrato (típico 30-50% del bruto del agente). Diferencia entre comisión por venta nueva y por renovación. Usar cuando el usuario diga "comisiones aseguradora", "cobrar comisión seguros", "facturar AXA", "calculador comisión agente", "CFDI honorarios seguros". NO usar para emisión de CFDI al asegurado (lo emite la aseguradora) ni para devolución de prima.
allowed-tools: Read, Write, Edit
---

# Calculador de comisiones a recibir

## Tabla típica por ramo

| Ramo | Venta nueva | Renovación | Notas |
|---|---|---|---|
| Auto | 18-25% | 15-20% | Mayor en regional |
| GMM | 10-15% | 8-12% | Bono por siniestralidad |
| Vida individual | 30-50% año 1 | 5-10% siguientes | Front-loaded |
| Vida grupal | 15-20% | 10-15% | |
| Daños hogar | 12-18% | 10-15% | |
| Daños empresa | 8-15% | 6-12% | |
| Fianzas | 8-12% | 8-12% | Plana |

## Cálculo

```
prima_neta = prima_total - IVA
comision_bruta = prima_neta * %_comision
bono_calidad = comision_bruta * %_bono (si siniestralidad < umbral)
comision_para_subagentes = (comision_bruta + bono) * %_subagente
comision_neta_agente = comision_bruta + bono - comision_subagentes
ISR_retenido = comision_neta * tasa_retencion_regimen
IVA_retenido = (comision_neta * 0.16) * tasa_iva_retencion
total_a_recibir = comision_neta + IVA_traslado - ISR_retenido - IVA_retenido
```

## CFDI a la aseguradora

- TipoComprobante: I
- UsoCFDI: G03 (gastos en general)
- ClaveProdServ: 84121500 (servicios financieros de seguros)
- ClaveUnidad: E48
- Impuestos: IVA 16% trasladado + retenciones según régimen

## Validación pendiente

⚠ Porcentajes pueden variar por contrato individual con cada aseguradora. Esta tabla es referencia, NO sustituye el contrato firmado.
