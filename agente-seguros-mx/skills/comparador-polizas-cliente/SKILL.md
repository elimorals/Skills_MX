---
name: comparador-polizas-cliente
description: Genera comparativa de pólizas de distintas aseguradoras para presentar al cliente en proceso de venta, normalizando suma asegurada por cobertura para hacer comparable manzanas con manzanas, deducibles aplicables, exclusiones específicas que el cliente debe conocer (preexistencias en GMM, descubierto en auto, antigüedad en daños), prima total con desglose mensual si fracciona, comisiones netas para el agente (transparencia interna), bonos del cliente por contratar (descuento por antigüedad, multipóliza, no siniestro), red de hospitales/talleres/peritos aceptados, y score subjetivo de calidad de servicio por aseguradora basado en bitácora histórica del agente (tiempo de respuesta a siniestros, tasa de aprobación de reembolsos, satisfacción reportada). Cubre auto, GMM, vida, daños. Usar cuando el usuario diga "comparar pólizas", "cotización seguros para cliente", "comparativa AXA GNP Quálitas", "cuadro comparativo seguros", "best price seguro". NO usar para emisión de póliza ni para cotización individual.
allowed-tools: Read, Write, Edit
---

# Comparador de pólizas multi-aseguradora

## Estructura de la comparativa

| Aspecto | AXA | GNP | Quálitas | Mapfre |
|---|---|---|---|---|
| Suma asegurada RC | $3M | $3M | $2.5M | $3M |
| Daños materiales | Valor comercial | Valor comercial | VC + 10% | VC |
| Robo total | ✅ | ✅ | ✅ | ✅ |
| Asistencia vial | 24/7 | 24/7 | 24/7 ilimitado | 24/7 |
| Auto sustituto | 15 días | 7 días | 21 días | 10 días |
| Deducible RC | 5% s/conv | 5% s/conv | 5% s/conv | 5% |
| Prima anual | $14,500 | $13,800 | $15,200 | $14,100 |
| Prima mensual | $1,250 | $1,190 | $1,310 | $1,215 |
| Bono multipóliza | -5% | -3% | -5% | -7% |
| Bono no siniestro | -10% año 2 | -8% año 2 | -10% año 2 | -10% año 2 |
| Red talleres | 1,200 nac | 1,500 nac | 800 nac | 950 nac |
| Score calidad agente | 8.2/10 | 8.5/10 | 7.8/10 | 7.9/10 |

## Sección de exclusiones críticas

Para cada póliza, listar EXPLICITAMENTE qué NO cubre.

## Recomendación

- Detectar mejor relación cobertura/precio
- Detectar mejor calidad servicio si cliente lo valora
- Detectar promo activa de aseguradora si aplica

## Output

PDF presentable + tabla resumen + ficha de cada opción.
