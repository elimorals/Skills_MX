---
name: tracking-medicamentos-vencimiento
description: Gestiona el pastillero del adulto mayor con polifarmacia (5-12 fármacos crónicos): existencias y días para agotarse, alerta de caducidad 30 días antes, horarios de tomas (mañana/comida/tarde/noche) con confirmación del cuidador para medir adherencia, lista básica de interacciones a revisar con el médico (warfarina + AINE, IECA + ahorrador de potasio, etc.), resurtido de receta crónica (IMSS, ISSSTE o particular) y reporte mensual al médico con adherencia y efectos adversos observados. Útil en diabetes (insulina), hipertensión, Alzheimer (donepezilo/memantina), Parkinson (levodopa). Usar cuando el usuario diga "medicamentos abuelita", "blister", "pastillero", "caducidad medicamento", "se le acaban las pastillas", "interacciones medicamentos mayor". NO usar para reembolsos de medicamentos con la aseguradora ni para alta hospitalaria.
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

Lista base de interacciones críticas (no exhaustiva; no proviene de COFEPRIS, que no publica una base de interacciones). Siempre confirmar con médico o farmacéutico:

| Combinación | Riesgo |
|---|---|
| Warfarina + AINE | Sangrado |
| IECA + Diurético ahorrador K+ | Hiperkalemia |
| Digoxina + Diurético tiazídico | Toxicidad digital |
| Antidepresivos triciclicos + Anticolinérgicos | Síndrome anticolinérgico |
| Benzodiacepinas + Opioides | Depresión respiratoria |
| Levodopa sola + Vit B6 | Reducción eficacia (con carbidopa casi no aplica) |

## Output

Reporte semanal: adherencia + próximos reabastecimientos + interacciones detectadas.
