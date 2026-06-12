---
name: gestion-pacientes-confidencial
description: Directorio pacientes con acceso restringido al terapeuta titular y a un suplente designado en caso de emergencia. Cifrado, audit log obligatorio LGPDPPSO. Pacientes pueden ser referidos a otro terapeuta sin compartir notas (solo derivación formal). Usar cuando el usuario diga pacientes terapia, directorio psicologia.
allowed-tools: Read, Write
---

# Gestión pacientes psicología

## Niveles de acceso

| Quien | Qué ve |
|---|---|
| Terapeuta titular | Todo |
| Terapeuta suplente designado (caso emergencia) | Solo datos contacto + alergias + medicación |
| Recepcionista | Solo agenda + pago (NO notas clínicas) |
| Paciente mismo | Sus datos + puede solicitar copia |
| Otros | NADA |

## Output

```json
{
  "total_pacientes_activos": 32,
  "altas_mes": 4,
  "bajas_mes": 2,
  "ultimo_acceso_pacientes": [
    {"paciente_hash": "...", "ultimo_acceso": "2026-06-12T15:30", "accesor": "terapeuta_titular"}
  ],
  "audit_log_entries_mes": 245
}
```

## Datos NO mencionables en logs/exports

- Diagnóstico explícito
- Nombre paciente en claro
- Contenido específico de sesiones
- Cualquier identificador derivado (ej. "ese señor del divorcio")
