---
name: tracking-procesamiento
description: Tracking del estado de cada muestra por etapa (recepción → distribución → procesamiento → control de calidad interno → revisión del químico responsable → liberación) con alertas cuando una muestra excede el tiempo objetivo de su tipo de estudio. Distingue estudios automatizados y manuales. Detecta valores críticos o de pánico (según la lista del propio laboratorio) y fuerza aviso inmediato al médico antes de liberar. Registra el control interno de calidad diario (NOM-007-SSA3-2011 7.1). Usar cuando el usuario diga status muestra, tracking lab, dónde va mi muestra, valores de pánico, valores críticos, QC lab, control de calidad. NO usar para procesamiento técnico del análisis ni para resultados finales (usar entrega-resultados).
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

> Lista ilustrativa: ninguna NOM fija estos umbrales. Cada laboratorio define y aprueba su propia lista de valores críticos con su responsable sanitario y los médicos que atiende; cargar esa lista antes de usar la skill.

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

Si una muestra excede 2x el tiempo objetivo: alerta para revisión. Tiempos orientativos; usar los comprometidos por el laboratorio con sus clientes.

## Control interno de calidad (NOM-007-SSA3-2011 7.1)

- El programa cubre etapas preanalítica, analítica y postanalítica
- Si el control del día está fuera de criterio: no liberar resultados de esa corrida, corregir, repetir controles y reprocesar
- Registrar en la bitácora la corrida, el lote de control, el resultado y quién aprobó
- Liberación firmada por el responsable sanitario o personal autorizado (NOM-007 5.1.8)
