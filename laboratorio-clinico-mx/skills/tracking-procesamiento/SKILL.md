---
name: tracking-procesamiento
description: Tracking del estado de cada muestra a través de las etapas del proceso analítico (recepción → distribución a área correspondiente → procesamiento analítico → control de calidad interno con materiales certificados → revisión del químico responsable → liberación) con alertas cuando una muestra está estancada > tiempo esperado por tipo de estudio (química clínica 2-4 hrs, hematología 1-2 hrs, microbiología 24-72 hrs cultivos, hormonas 4-8 hrs). Diferencia entre estudios automatizados (analizador procesa con código de barras) y manuales (procesa el químico paso a paso). Detecta valores de pánico (valores críticos que requieren notificación inmediata al médico: K+ > 6.5, glucosa < 50, hemoglobina < 7, troponina elevada) y los marca para revisión urgente del médico responsable antes de liberar. Tracking del control de calidad diario con materiales QC y registro de resultados fuera de rango aceptable. Usar cuando el usuario diga "status muestra", "tracking lab", "valores de pánico", "QC lab", "control calidad". NO usar para procesamiento técnico del análisis ni para resultados finales (usar entrega-resultados).
allowed-tools: Read, Write, Edit
---

# Tracking de procesamiento de muestras

## Etapas del flujo

```
[RECEPCION] → [DISTRIBUCION] → [PROCESAMIENTO] → [QC] → [REVISION] → [LIBERACION]
```

## Estado por etapa

```yaml
codigo_muestra: LAB-2026-06-12-00342
historial:
  - etapa: recepcion
    timestamp: 2026-06-12T10:32:00
    por: QFB María González
    notas: muestra OK
  - etapa: distribucion
    timestamp: 2026-06-12T10:45:00
    area: quimica_clinica
  - etapa: procesamiento
    timestamp: 2026-06-12T11:00:00
    analizador: Cobas 6000
    resultado_crudo: {...}
  - etapa: qc
    timestamp: 2026-06-12T11:15:00
    qc_aprobado: true
    materiales_qc: [Nivel1, Nivel2]
  - etapa: revision
    timestamp: 2026-06-12T13:00:00
    revisado_por: QFB Director Técnico Juan Pérez (cédula 1234)
    notas: K+ elevado — repetir
  - etapa: re-procesamiento
    timestamp: 2026-06-12T13:30:00
    resultado_confirmado: true
  - etapa: liberacion
    timestamp: 2026-06-12T14:00:00
    firmado_por: Director Técnico
```

## Valores de pánico (notificación inmediata al médico)

| Analito | Valor pánico | Mecanismo |
|---|---|---|
| Glucosa | < 50 o > 500 mg/dL | Llamada en < 30 min |
| Potasio | < 2.5 o > 6.5 mEq/L | Llamada en < 30 min |
| Hemoglobina | < 7 o > 20 g/dL | Llamada en < 1 hr |
| Plaquetas | < 50,000 o > 1,000,000 | Llamada en < 1 hr |
| Troponina | elevada | Llamada en < 30 min |
| Calcio | < 6 o > 14 mg/dL | Llamada en < 1 hr |
| Cultivo | hemocultivo positivo | Llamada en < 1 hr |
| INR | > 5.0 | Llamada en < 1 hr |

Cualquier valor de pánico:
1. Marca muestra como "PANICO"
2. Notifica QFB de turno
3. QFB llama al médico solicitante
4. Documenta llamada (hora + a quién avisó)

## Tiempos esperados por estudio

| Categoría | Tiempo objetivo |
|---|---|
| Hematología (BHC) | 1-2 hrs |
| Química clínica básica | 2-4 hrs |
| Hormonas | 4-8 hrs |
| Microbiología — cultivo | 24-72 hrs |
| Citología | 48-72 hrs |
| Biopsia | 5-7 días |

Si una muestra excede 2x el tiempo objetivo: alerta para revisión.
