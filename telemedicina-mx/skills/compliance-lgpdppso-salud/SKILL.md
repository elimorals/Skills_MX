---
name: compliance-lgpdppso-salud
description: Auditoría continua de cumplimiento LGPDPPSO (Ley General de Protección de Datos Personales en Posesión de Sujetos Obligados) y LFPDPPP para datos sensibles de salud manejados en telemedicina. Verifica cifrado en reposo, audit log activo, consentimientos vigentes, retención de datos, derechos ARCO del paciente, manejo de filtraciones. Usar cuando el usuario diga compliance salud, lgpdppso, lfpdppp telemedicina, proteccion datos paciente.
allowed-tools: Read, Write
---

# Compliance LGPDPPSO/LFPDPPP — datos sensibles salud

## Marco legal aplicable

| Ley | Aplica a | Sanciones |
|---|---|---|
| **LFPDPPP** (privada) | Médico privado, clínica privada | Multas $300k-$50M MXN |
| **LGPDPPSO** (pública) | IMSS, ISSSTE, hospitales públicos | Multas + responsabilidad servidores públicos |
| **NOM-024-SSA3** | Sistemas registro electrónico salud | Sanción SSA / COFEPRIS |
| **NOM-004-SSA3** | Expediente clínico | Sanción SSA / COFEPRIS |

## Datos personales sensibles (Art. 3 fr. VI LFPDPPP)

Datos de salud son **sensibles** — máxima protección:
- Diagnósticos
- Tratamientos
- Resultados estudios
- Historial psicológico/psiquiátrico
- Información genética
- VIH, ETS, embarazo, abortos
- Discapacidades

Tratamiento requiere **consentimiento expreso por escrito** (Art. 9 LFPDPPP).

## Checklist auditoría continua

```python
def auditar_compliance() -> dict:
    checks = {
        "cifrado_aes256_en_reposo": verificar_cifrado_expedientes(),
        "audit_log_activo": verificar_audit_log(),
        "consentimientos_vigentes": validar_consentimientos_todos_pacientes(),
        "retencion_minimo_5_anios": verificar_retencion(),
        "borrado_seguro_post_retencion": verificar_borrado(),
        "aviso_privacidad_publicado": existe_aviso_privacidad(),
        "responsable_datos_designado": verificar_designacion(),
        "procedimiento_arco_documentado": existe_procedimiento(),
        "plan_respuesta_filtracion": existe_plan(),
        "personal_capacitado_lfpdppp": verificar_capacitacion(),
    }
    return {
        "score_compliance": sum(checks.values()) / len(checks) * 100,
        "checks": checks,
        "pendientes": [k for k, v in checks.items() if not v]
    }
```

## En caso de filtración (data breach)

**Plazo legal**: 72h para notificar (Art. 80 LGPDPPSO + RLFPDPPP).

Notificar a:
1. **Pacientes afectados** (individualmente)
2. **INAI** (Instituto Nacional de Acceso a la Información)
3. **Si penal**: Ministerio Público

Documentar:
- Qué se filtró
- Cuándo se detectó
- Qué se hizo para mitigar
- Medidas preventivas futuras

## Output auditoría

```json
{
  "fecha_auditoria": "2026-06-12",
  "score_compliance_pct": 90,
  "items_aprobados": 9,
  "items_pendientes": 1,
  "pendientes_detalle": [
    {
      "item": "plan_respuesta_filtracion",
      "criticidad": "alta",
      "accion": "Documentar protocolo + entrenar al equipo",
      "deadline_sugerido": "2026-07-15"
    }
  ],
  "riesgo_general": "BAJO",
  "ultimo_consentimiento_vencido": null,
  "audit_log_entries_mes": 1248,
  "filtraciones_reportadas_anio": 0
}
```

## Derechos ARCO del paciente

Paciente puede ejercer:
- **A**cceso: ver su expediente
- **R**ectificación: corregir datos erróneos
- **C**ancelación: solicitar borrado (con limitaciones legales)
- **O**posición: oponerse a usos secundarios (estudios, publicidad)

Plazo de respuesta: **20 días hábiles** (Art. 32 LFPDPPP).
