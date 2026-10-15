---
name: autorizacion-medica-pre-evento
description: Gestión de pre-autorización médica antes de hospitalización / procedimiento mayor (programación de cirugía/servicios; el umbral y los casos los fija cada póliza). Solicitud + documentos + tiempos respuesta + escalación si se niega. Usar cuando el usuario diga pre-autorizacion gmm, autorizacion aseguradora, cirugia programada.
allowed-tools: Read, Write
---

# Autorización médica pre-evento

## Cuándo aplica

- Hospitalización programada
- Cirugía mayor (apéndice, vesícula, etc.)
- Estudios de alto costo (p. ej. resonancia magnética), según condiciones generales
- Tratamiento oncológico
- Maternidad (si póliza la cubre)

## Documentos típicos

- Diagnóstico médico con CIE-10
- Resumen clínico
- Presupuesto hospital
- Plan de tratamiento
- Solicitud médico tratante (membretado + firma + cédula)

## Tiempos respuesta

Plazos típicos de mercado (no son legales; revisa tus condiciones generales):
- Programación rutinaria: 3-5 días hábiles
- Urgencia: 24-48 h con justificación médica
- Emergencia: se atiende primero; da **aviso del siniestro** a la aseguradora en cuanto puedas — la Ley sobre el Contrato de Seguro (Art. 66) fija 5 días salvo caso fortuito o fuerza mayor

## Output

```json
{
  "solicitud_id": "PRE-AUT-001",
  "evento": "cirugia_apendice",
  "presupuesto_mxn": "180000.00",
  "documentos_subidos": ["diagnostico", "resumen_clinico", "presupuesto"],
  "documentos_faltantes": ["plan_tratamiento_detallado"],
  "estado": "esperando_documentos",
  "fecha_solicitud": "2026-10-15",
  "fecha_estimada_respuesta": "2026-10-21"
}
```

## Si niega

1. Pedir el rechazo y su fundamento **por escrito** (cláusula de la póliza que invocan).
2. Reconsideración con el médico tratante + estudios o argumentos nuevos.
3. Reclamación ante la **Unidad Especializada de Atención a Usuarios (UNE)** de la aseguradora (Art. 50 Bis Ley de Protección y Defensa al Usuario de Servicios Financieros; responde en ≤ 30 días hábiles).
4. Reclamación ante **CONDUSEF** (gratuita; conciliación y, en su caso, dictamen). Plazo para reclamar: 2 años desde el hecho (verificar Art. 65 LPDUSF).
5. Vía judicial o arbitraje. Las acciones del contrato de seguro prescriben en 2 años (Art. 81 LSCS) — no dejes pasar el plazo.

Para confirmar que la aseguradora está autorizada: registro de la **CNSF** (supervisor conforme a la Ley de Instituciones de Seguros y de Fianzas).

> Orientación general; para montos altos o negativas reiteradas, asesórate con abogado o con CONDUSEF.
