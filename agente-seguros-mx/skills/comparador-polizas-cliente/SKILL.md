---
name: comparador-polizas-cliente
description: Genera una comparativa de pólizas de distintas aseguradoras para presentar al cliente en el proceso de venta, normalizando suma asegurada por cobertura para comparar manzanas con manzanas, deducibles, exclusiones que el cliente debe conocer (preexistencias y periodos de espera en GMM, deducibles de daños materiales y robo en auto, antigüedad en daños), prima total con desglose si fracciona (incluido el recargo por pago fraccionado), comisión del agente (uso interno), descuentos para el cliente (multipóliza, no siniestro), red de hospitales/talleres y una calificación de servicio basada en la bitácora del agente. Cubre auto, GMM, vida, daños. Usar cuando el usuario diga "comparar pólizas", "cotización seguros para cliente", "comparativa aseguradoras", "cuadro comparativo seguros", "qué seguro me conviene", "mejor precio seguro". NO usar para emisión de póliza ni para cotización individual.
allowed-tools: Read, Write, Edit
---

# Comparador de pólizas multi-aseguradora

## Estructura de la comparativa

Ejemplo ilustrativo con cifras ficticias (no son tarifas reales de ninguna aseguradora):

| Aspecto | Aseguradora A | Aseguradora B | Aseguradora C | Aseguradora D |
|---|---|---|---|---|
| Suma asegurada RC | $3M | $3M | $2.5M | $3M |
| Daños materiales | Valor comercial | Valor comercial | VC + 10% | VC |
| Deducible daños materiales | 5% | 5% | 5% | 3% |
| Deducible robo total | 10% | 10% | 10% | 10% |
| Asistencia vial | 24/7 | 24/7 | 24/7 ilimitado | 24/7 |
| Auto sustituto | 15 días | 7 días | 21 días | 10 días |
| Prima anual (contado) | $14,500 | $13,800 | $15,200 | $14,100 |
| Prima mensual (12 recibos) | $1,250 ($15,000/año) | $1,190 ($14,280/año) | $1,310 ($15,720/año) | $1,215 ($14,580/año) |
| Desc. multipóliza | −5% | −3% | −5% | −7% |
| Desc. no siniestro | −10% año 2 | −8% año 2 | −10% año 2 | −10% año 2 |
| Red de talleres | 1,200 | 1,500 | 800 | 950 |
| Calificación servicio (bitácora) | 8.2 | 8.5 | 7.8 | 7.9 |

Muestra siempre el costo anual total del pago fraccionado: la diferencia contra el contado es el recargo por fraccionar.

## Exclusiones críticas

Para cada póliza, lista EXPLÍCITAMENTE qué NO cubre, tomado de las condiciones generales vigentes de la aseguradora (registradas ante la CNSF). No resumas de memoria.

## Datos externos

- Verifica que cada aseguradora esté autorizada con `sipres_verificar_autorizada` (MCP `mp_condusef_sipres`).
- Las primas salen del cotizador de cada aseguradora; no hay MCP de cotización. Pide al usuario las cotizaciones o los PDF.

## Recomendación

- Mejor relación cobertura/precio
- Mejor calidad de servicio si el cliente lo valora
- Promoción vigente de alguna aseguradora, si aplica

La comisión del agente es dato interno; no la uses como criterio para recomendar.

## Output

PDF presentable + tabla resumen + ficha de cada opción.
