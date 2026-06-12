---
spec: "<nombre-kebab>"
estado: "DRAFT | IN_PROGRESS | IMPLEMENTED | DEPRECATED"
creado: "YYYY-MM-DD"
autor: "<nombre>"
ultima_actualizacion: "YYYY-MM-DD"
esfuerzo_estimado_horas: [min, max]
prioridad: "tier-1 | tier-2 | tier-3"
---

# Spec NN — <título humano>

## 1. Propósito

Un párrafo: qué problema resuelve, para qué usuario, qué cambio mensurable produce.

## 2. Contexto y por qué es novedoso

- Qué existe ya en el repo relacionado
- Por qué los patrones existentes no aplican directamente
- Referencias a planeación original (sección X del doc)

## 3. Alcance

**Dentro de scope:**
- Bullet 1
- Bullet 2

**Fuera de scope (decisión deliberada):**
- Bullet 1 — razón
- Bullet 2 — razón

## 4. Inputs / outputs / schemas

```python
# Schemas Pydantic o JSON Schema o ejemplo de I/O
```

## 5. Tools / endpoints / triggers expuestos

| Tool / endpoint | Propósito | Auth | Idempotencia |
|---|---|---|---|
| ... | ... | ... | ... |

## 6. Casos edge (mínimo 5)

| Caso | Comportamiento esperado |
|---|---|
| Sin credenciales | Mock con `simulated: true` |
| Auth inválida | `AuthError` 401 con mensaje claro |
| Timeout upstream | Retry 1 vez, después `UpstreamError` |
| Payload malformado | `ValidationError` antes de tocar red |
| (caso específico del dominio) | ... |

## 7. Dependencias

**MCPs**: `mp_x`, `mp_y`
**Skills**: `skill-a`, `skill-b`
**Librerías Python nuevas**: `lib-z` (justificar por qué)
**Servicios externos**: (URL, docs)

## 8. Criterios de aceptación

- [ ] Tests unitarios: cobertura ≥ 80% de happy paths
- [ ] Tests de integración mock: todos los tools responden con shape esperado
- [ ] Lint passing (`lint-skills.sh` si aplica)
- [ ] Documentación: README.md + entry en STATUS.md actualizado
- [ ] Bitácora con hash de identificadores sensibles
- [ ] Mock-first verificado (sin credenciales → respuesta plausible)
- [ ] (criterios específicos del dominio)

## 9. Esfuerzo estimado

- **Diseño + setup**: X horas
- **Implementación core**: Y horas
- **Tests + fixtures**: Z horas
- **Docs**: W horas
- **TOTAL**: [min, max] horas

## 10. Riesgos + mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| ... | alta/media/baja | alto/medio/bajo | ... |

## 11. Decisiones pendientes

- [ ] ¿Pregunta 1?
- [ ] ¿Pregunta 2?

## 12. Plan de implementación

### Fase 1: Foundation
1. Paso ...
2. Paso ...

### Fase 2: Core
1. Paso ...

### Fase 3: Integración + tests
1. Paso ...

### Fase 4: Documentación
1. Paso ...

## 13. Links

- Issue / commit relacionado: (al implementar)
- Doc de planeación original: `/Users/elias/Downloads/plugins-mx-*.md` sección X
- Referencia externa: (docs API, libro, etc.)
