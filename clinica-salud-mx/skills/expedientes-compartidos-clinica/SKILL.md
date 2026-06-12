---
name: expedientes-compartidos-clinica
description: Expedientes pacientes accesibles por todos los médicos autorizados de la clínica con audit log obligatorio (LGPDPPSO). Cada acceso queda registrado (quién, cuándo, qué). Útil cuando paciente ve a varios médicos (médico general + especialista) y necesitan compartir información clínica. Usar cuando el usuario diga compartir expediente, expediente compartido, otro medico vea historial.
allowed-tools: Read, Write
---

# Expedientes compartidos clínica

## Control de acceso

Por defecto cada médico ve **solo expedientes de pacientes que él atendió**. Para compartir:

1. Paciente firma autorización explícita LFPDPPP
2. Médico A (que tiene relación con paciente) marca expediente como "compartido con clínica"
3. Otros médicos autorizados pueden leer (no modificar) las notas previas

## Audit log obligatorio

```json
{
  "ts": "2026-06-12T10:30:00",
  "medico_accesor_id": "M-002",
  "expediente_paciente_hash": "abc123",
  "accion": "lectura",
  "duracion_segundos": 145,
  "ip_origen": "192.168.1.10",
  "motivo_clinico": "interconsulta_cardio"
}
```

## Notificación al paciente

Si un médico distinto al primario accede al expediente: paciente recibe email/WhatsApp dentro de 24h informando.

## Casos edge

- Urgencia médica: acceso permitido aún sin autorización + reportar al paciente después
- Médico fuera de la clínica: no puede acceder (token revocado)
- Paciente revoca autorización: acceso bloqueado inmediato
