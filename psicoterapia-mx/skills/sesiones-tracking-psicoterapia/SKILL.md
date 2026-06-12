---
name: sesiones-tracking-psicoterapia
description: Tracking de sesiones de psicoterapia con notas clínicas breves (objetivo terapéutico, intervención, asignación tarea, riesgo suicida si aplica). Cifrado AES-256 obligatorio. Acceso solo terapeuta. Útil para continuidad terapéutica sin perder detalles. Usar cuando el usuario diga notas sesion, registro paciente psicologo, sesion terapia.
allowed-tools: Read, Write
---

# Tracking sesiones psicoterapia

## Schema sesión

```python
class SesionPsicoterapia(BaseModel):
    sesion_id: str
    paciente_id_hash: str       # hasheado siempre
    fecha_hora: datetime
    duracion_min: int           # típico 50
    numero_sesion: int          # 1, 2, 3, etc.
    foco_terapeutico: str
    intervenciones_usadas: list[str]  # CBT, EMDR, etc.
    avance_objetivo_pct: int    # 0-100
    asignacion_proxima_sesion: str
    riesgo_suicida_evaluado: Literal["nulo", "bajo", "medio", "alto", "inminente"]
    nota_breve_cifrada: bytes
    proxima_sesion_sugerida: datetime
```

## ⚠ Protocolo riesgo alto

Si `riesgo_suicida_evaluado` ∈ `["alto", "inminente"]`:
1. Activar protocolo prevención (no dejar solo al paciente)
2. Contactar familiar/persona de confianza con permiso
3. Derivar a urgencias psiquiátricas
4. Línea de la Vida 800-290-0024
5. Documentar exhaustivamente

## Compliance estricto

- **Cifrado AES-256-GCM** con clave del terapeuta (no en servidor)
- Notas NO mencionan diagnósticos literales sin razón clínica
- Audit log cada acceso
- Retención: 5 años post última sesión (NOM-035 + LGPDPPSO)
- Si paciente cancela tratamiento + pide eliminación: anonimizar pero conservar (obligación legal)
