---
name: autorizacion-medica-pre-evento
description: Gestión de pre-autorización médica antes de hospitalización / procedimiento mayor (la aseguradora suele requerir si costo > $10k). Solicitud + documentos + tiempos respuesta + escalación si se niega. Usar cuando el usuario diga pre-autorizacion gmm, autorizacion aseguradora, cirugia programada.
allowed-tools: Read, Write
---

# Autorización médica pre-evento

## Cuándo aplica

- Hospitalización programada
- Cirugía mayor (apéndice, vesícula, etc.)
- Estudios costosos (resonancia magnética > $5k)
- Tratamiento oncológico
- Maternidad (si póliza la cubre)

## Documentos típicos

- Diagnóstico médico con CIE-10
- Resumen clínico
- Presupuesto hospital
- Plan de tratamiento
- Solicitud médico tratante (membretado + firma + cédula)

## Tiempos respuesta

- Rutina: 3-5 días hábiles
- Urgencia: 24-48h (con justificación médica)
- Emergencia: post-evento, dentro de 48h

## Output

```json
{
  "solicitud_id": "PRE-AUT-001",
  "evento": "cirugia_apendice",
  "presupuesto_mxn": "180000.00",
  "documentos_subidos": ["diagnostico", "resumen_clinico", "presupuesto"],
  "documentos_faltantes": ["plan_tratamiento_detallado"],
  "estado": "esperando_documentos",
  "fecha_solicitud": "2026-06-12",
  "fecha_estimada_respuesta": "2026-06-17"
}
```

## Si niega

- Pedir motivo por escrito
- Apelar con médico tratante + nuevos argumentos
- Si segundo niega: queja CONDUSEF
