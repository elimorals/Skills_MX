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
4. Línea de la Vida (CONASAMA) **800 911 2000**, 24 h; emergencia 911
5. Documentar exhaustivamente

## Compliance estricto

- **Cifrado** en reposo (p. ej. AES-256-GCM) con clave del terapeuta (no en servidor) — buena práctica de seguridad, no cifra legal
- Notas NO mencionan diagnósticos literales sin razón clínica
- Bitácora de cada acceso (NOM-024-SSA3-2012 6.6.1 si es expediente electrónico)
- Conservación: mínimo 5 años desde la última sesión (NOM-004-SSA3-2012 5.4, que aplica también a psicólogos)
- Si el paciente pide eliminar sus datos: la cancelación ARCO se limita mientras corra la obligación de conservar; bloquear y suprimir al vencer (LFPDPPP 2025)
