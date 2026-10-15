---
name: calculador-comisiones-aseguradoras
description: Calcula las comisiones que el agente de seguros debe recibir de cada aseguradora con una tabla de referencia por ramo (auto, GMM, vida, daños, fianzas), bonos de calidad cuando aplican (baja siniestralidad), el tratamiento de IVA (comisiones de seguros de vida exentas, Art. 15 fr. IX LIVA; auto, GMM y daños gravados al 16%), las retenciones que aplica la aseguradora persona moral (2/3 del IVA en ramos gravados; ISR 1.25% si el agente es RESICO 626; sin retención de ISR si tributa en actividad empresarial 612) y el CFDI de comisiones a la aseguradora. Cubre el reparto a subagentes según contrato y la diferencia entre comisión de venta nueva y de renovación. Verifica que el agente tenga cédula CNSF vigente para el ramo. Usar cuando el usuario diga "comisiones aseguradora", "cobrar comisión seguros", "facturar a la aseguradora", "calculador comisión agente", "CFDI comisiones seguros", "retención comisión agente". NO usar para emisión de CFDI al asegurado (lo emite la aseguradora) ni para devolución de prima.
allowed-tools: Read, Write, Edit
---

# Calculador de comisiones a recibir

## Requisito previo: cédula CNSF

La intermediación de seguros requiere autorización de la CNSF (Art. 93 LISF), otorgada por operaciones y ramos. Antes de calcular, confirma que la cédula del agente esté vigente y cubra el ramo. La vigencia y el refrendo los fija el Reglamento de Agentes de Seguros y de Fianzas y la CNSF: verificar en el portal de la CNSF (no hay MCP para consultarla).

## Tabla de referencia por ramo (no normativa)

| Ramo | Venta nueva | Renovación | Notas |
|---|---|---|---|
| Auto | 18-25% | 15-20% | Mayor en regional |
| GMM | 10-15% | 8-12% | Bono por siniestralidad |
| Vida individual | 30-50% año 1 | 5-10% siguientes | Front-loaded |
| Vida grupal | 15-20% | 10-15% | |
| Daños hogar | 12-18% | 10-15% | |
| Daños empresa | 8-15% | 6-12% | |
| Fianzas | 8-12% | 8-12% | Plana |

Los porcentajes reales son los del contrato con cada aseguradora; esta tabla es solo referencia de mercado (confianza baja, sin fuente oficial).

## Cálculo

```
prima_neta = prima_total − IVA − derecho_de_póliza − recargo_por_pago_fraccionado
comision = prima_neta × %_comision
bono = comision × %_bono            (si la siniestralidad < umbral del contrato)
base = comision + bono              (lo que factura el agente a la aseguradora)

IVA_trasladado = base × 16%          (0 si el ramo es vida: comisión exenta)
ISR_retenido   = base × 1.25%        (solo si el agente es RESICO 626; 0 en 612)
IVA_retenido   = IVA_trasladado × 2/3
total_a_recibir = base + IVA_trasladado − ISR_retenido − IVA_retenido

pago_subagentes = base × %_subagente   (costo del agente; no reduce la base facturada)
```

### Ejemplo (auto, prima neta $10,000, comisión 20%, sin bono)

| Concepto | Agente 612 | Agente RESICO 626 |
|---|---|---|
| Comisión (base) | 2,000.00 | 2,000.00 |
| IVA 16% | 320.00 | 320.00 |
| ISR retenido | 0.00 | −25.00 |
| IVA retenido 2/3 | −213.33 | −213.33 |
| **Total a recibir** | **2,106.67** | **2,081.67** |

Si fuera vida con la misma comisión: IVA exento, sin retención de IVA; total 2,000.00 (612) o 1,975.00 (626).

## Régimen del agente

- **Agente con contrato mercantil (Art. 93 fr. II LISF)**: las comisiones son actividad empresarial. La retención de 10% de ISR del Art. 106 LISR es solo para servicios profesionales, así que no aplica (confianza media: lectura del Art. 106 LISR y guía de Praxium, 10-09-2026).
- **RESICO 626**: retención de 1.25% de ISR por pagos de personas morales (Art. 113-J LISR).
- **Asimilados a salarios (Art. 94 LISR, por opción escrita) o empleado de la aseguradora (Art. 93 fr. I LISF)**: la aseguradora retiene ISR con tarifa y emite CFDI de nómina; no hay IVA.
- **IVA retenido**: 2/3 del IVA por comisiones pagadas por personas morales (Art. 1-A fr. II inciso a) LIVA y Art. 3 RLIVA). Ver `iva-retenciones-mx`.

## CFDI a la aseguradora

- TipoDeComprobante: I · UsoCFDI: G03
- ClaveProdServ: el catálogo SAT no tiene clave específica de intermediación de seguros. Usa la del ramo intermediado (p. ej. `84131503` seguro de automóviles, `84131601` seguros de vida, `84131602` gastos médicos) y confírmala con la aseguradora, que suele indicar la clave en su portal de comisiones. Verificar.
- ClaveUnidad: E48
- Impuestos: IVA 16% trasladado (o Exento en vida) + retenciones según régimen.
- Algunas aseguradoras emiten el comprobante por cuenta del agente desde su portal; si es así, no dupliques el CFDI.

> Revisión profesional: confirma régimen y retenciones con el contador del agente.
