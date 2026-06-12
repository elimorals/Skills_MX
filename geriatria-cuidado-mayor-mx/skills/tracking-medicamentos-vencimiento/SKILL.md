---
name: tracking-medicamentos-vencimiento
description: Gestiona el blister/pastillero del adulto mayor con tracking detallado de medicamentos crónicos múltiples (típico polifarmacia 5-12 fármacos en mayores 75+), alerta cuando un medicamento se acerca a su fecha de vencimiento de caducidad (30 días antes para reabastecer), recordatorio diario de tomas distribuido en horarios (mañana/comida/tarde/noche) con confirmación del cuidador para tracking de adherencia, detección automática de interacciones medicamentosas (warfarina + AINEs, IECA + diuréticos K+, etc.) usando base de datos COFEPRIS, control de reabastecimiento con recetario crónico (cuando aplica receta resurtible IMSS o particular), y reporte mensual al médico tratante con tasa de adherencia + efectos adversos observados por cuidadores. Crítico para diabetes (insulina), hipertensión (varios fármacos), alzheimer (memantina/donepezilo), parkinson (levodopa). Usar cuando el usuario diga "medicamentos abuelita", "blister", "pastillero", "vencimiento medicamento", "interacciones medicamentos mayor". NO usar para reembolsos de medicamentos (usar gestor-reembolso de gmm) ni para alta de enfermedad.
allowed-tools: Read, Write, Edit
---

# Tracking de medicamentos en adulto mayor

## Estructura por medicamento

```yaml
nombre_generico: metformina
marca_comercial: Glucophage
presentacion: 850mg tableta
indicacion: Diabetes mellitus tipo 2
posologia:
  dosis: 1 tableta
  veces_dia: 2
  horarios: ["08:00", "20:00"]
  con_comida: true
duracion: cronico_resurtible
receta_id: RX-2026-042
fecha_inicio: 2024-03-15
ultima_compra: 2026-06-01
existencia_actual: 18  # tabletas
caducidad_lote: 2027-08-31
dias_para_agotarse: 9  # calculado: 18 / (1*2)
alerta_reabastecer: 14  # umbral en días
alerta_caducidad_dias: 30
ajustado_por: Dr. Ramírez Cardiología
```

## Alertas automáticas

- 14 días antes de agotarse → comprar siguiente caja
- 30 días antes de caducidad → revisar fecha vs existencia
- Si se omite ≥ 2 tomas → alerta al cuidador principal
- Si se omite ≥ 5 tomas/semana → alerta al médico

## Detección de interacciones

Lista base de interacciones críticas (no exhaustiva — requiere actualización periódica):

| Combinación | Riesgo |
|---|---|
| Warfarina + AINE | Sangrado |
| IECA + Diurético ahorrador K+ | Hiperkalemia |
| Digoxina + Diurético tiazídico | Toxicidad digital |
| Antidepresivos triciclicos + Anticolinérgicos | Síndrome anticolinérgico |
| Benzodiacepinas + Opioides | Depresión respiratoria |
| Levodopa + Vit B6 | Reducción eficacia |

## Output

Reporte semanal: adherencia + próximos reabastecimientos + interacciones detectadas.
