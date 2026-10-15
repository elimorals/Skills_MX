---
name: expedientes-compartidos-clinica
description: Expedientes de pacientes accesibles por los médicos autorizados de la clínica con bitácora de accesos (quién, cuándo, qué, por qué), conforme NOM-004-SSA3-2012 (confidencialidad), NOM-024-SSA3-2012 (trazabilidad y roles en expediente electrónico) y LFPDPPP 2025 (datos sensibles; la LGPDPPSO solo aplica a instituciones públicas). Útil cuando el paciente ve a varios médicos (médico general + especialista) y necesitan compartir información clínica. Usar cuando el usuario diga compartir expediente, expediente compartido, otro médico vea historial, interconsulta, permisos de expediente.
allowed-tools: Read, Write
---

# Expedientes compartidos clínica

## Control de acceso

Por defecto cada médico ve **solo expedientes de pacientes que él atendió**. Para compartir:

1. Paciente otorga consentimiento expreso y por escrito para que su información de salud se comparta entre los médicos de la clínica (Art. 8 LFPDPPP 2025; mencionarlo en el aviso de privacidad)
2. Médico A (que tiene relación con paciente) marca expediente como "compartido con clínica"
3. Otros médicos autorizados pueden leer (no modificar) las notas previas; cada quien firma sus propias notas (NOM-004 5.10)

El expediente es propiedad del establecimiento y debe conservarse mínimo 5 años desde el último acto médico (NOM-004 5.4); confidencialidad para todo el personal (5.7).

## Bitácora de accesos (NOM-024 6.6.1 trazabilidad, 6.6.4 roles)

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

- Urgencia médica: acceso permitido aún sin autorización (la LFPDPPP exceptúa el consentimiento cuando es necesario para atención médica en emergencia; **verificar** artículo en la ley 2025) + registrar motivo e informar al paciente después
- Médico fuera de la clínica: no puede acceder (token revocado)
- Paciente revoca autorización: acceso bloqueado inmediato
