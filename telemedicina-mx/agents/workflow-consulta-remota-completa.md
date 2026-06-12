---
name: workflow-consulta-remota-completa
description: Workflow end-to-end de una consulta remota. Verifica consentimiento, valida pre-requisitos, ejecuta consulta (externa), actualiza expediente NOM-004, emite receta si aplica (con bloqueo Grupos I-II), emite CFDI uso D01, agenda próxima consulta. Garantiza compliance LGPDPPSO en cada paso. Usar al inicio de una consulta nueva o cuando el usuario diga corre flujo completo, atender paciente tele, ciclo completo telemedicina.
allowed-tools: Read, Write
---

# Workflow consulta remota completa

## Fase 0 — Pre-consulta (T-24h)

1. Verificar consentimiento del paciente firmado y vigente
2. Si nuevo paciente sin consentimiento: enviar `consentimiento-informado-tele` antes
3. Verificar pago (pre-pago obligatorio típicamente)
4. Generar link Zoom/Meet y enviar al paciente
5. Programar recordatorios (24h, 2h, post-consulta)

## Fase 1 — Inicio consulta (T+0)

1. Médico verifica e.firma vigente (`gestor-efirma-vencimientos`)
2. Cargar expediente del paciente
3. Documentar consulta en notas (NOM-004)

## Fase 2 — Durante consulta

Conducir consulta normalmente. NO automatizable.

## Fase 3 — Post-consulta

### 3.1 Actualizar expediente
Invocar `expediente-clinico-tele` con:
- Padecimiento actual
- Exploración física limitada (qué se evaluó por video)
- Diagnóstico CIE-10
- Plan tratamiento
- Pronóstico
- Notas evolución

### 3.2 Validar interacciones (si va a recetar)
Invocar `interacciones-medicamentosas-basicas` con medicamento nuevo + medicamentos crónicos del paciente.

Si severidad mayor: BLOQUEAR receta + reconsiderar.

### 3.3 Emitir receta (si aplica)
Invocar `receta-electronica-tele-cofepris`:
- Bloqueo automático si incluye Grupo I-II
- Firma e.firma médico
- QR de verificación

### 3.4 Emitir CFDI
Invocar `cfdi-honorario-medico-d01`:
- Uso D01
- Forma pago no efectivo (verificar antes)
- Total + IVA si aplica

### 3.5 Recordatorios + próxima consulta
Invocar `recordatorios-paciente-wa`:
- Resumen consulta
- Link receta
- Próxima cita sugerida (3.6)

### 3.6 Agendar próxima si aplica
Invocar `agendar-consulta-remota` con fecha + motivo + duración estimada.

## Fase 4 — Compliance check

Cada 30 consultas: invocar `compliance-lgpdppso-salud` para verificar score.

## Output final

```json
{
  "workflow": "consulta_remota_completa",
  "consulta_id": "TEL-001",
  "paciente_id_hash": "...",
  "fases_completadas": [0, 1, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6],
  "expediente_actualizado": true,
  "receta_emitida": true,
  "receta_id": "REC-TEL-001",
  "cfdi_uuid": "abc-123",
  "proxima_consulta": "2026-07-12T16:00:00",
  "tiempo_total_ms": 850,
  "exitoso": true,
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Paciente sin consentimiento previo | Pausar workflow, enviar consentimiento, esperar firma |
| e.firma médico vencida | BLOQUEAR — renovar antes |
| Receta con Grupo I-II | BLOQUEAR receta, derivar a recetario físico |
| Paciente quiere CFDI con RFC | Capturar RFC + emitir D01 |
| Paciente sin RFC | XAXX010101000 + no deducible |
| Urgencia detectada mid-consulta | Pausar workflow, derivar a presencial/urgencias |
| Paciente menor edad | Validar padre/tutor presente + firma adicional |
