---
name: compliance-lgpdppso-salud
description: Auditoría continua de protección de datos personales sensibles de salud en telemedicina. Para médicos y clínicas privadas aplica la LFPDPPP 2025 (autoridad Secretaría Anticorrupción y Buen Gobierno, ya no INAI); la LGPDPPSO solo aplica a instituciones públicas (IMSS, ISSSTE, hospitales públicos). Verifica consentimiento expreso por escrito, aviso de privacidad, medidas de seguridad (cifrado, bitácora de accesos), conservación del expediente (NOM-004), sistemas NOM-024, derechos ARCO y respuesta a vulneraciones. Usar cuando el usuario diga compliance salud, lgpdppso, lfpdppp telemedicina, protección de datos del paciente, datos sensibles salud, aviso de privacidad consultorio, fuga de datos de pacientes.
allowed-tools: Read, Write
---

# Compliance de datos de salud (LFPDPPP / LGPDPPSO) — telemedicina

> Orientación, no asesoría legal. Validar con abogado en protección de datos antes de publicar avisos o responder a la autoridad.

## Marco legal aplicable (vigente a oct-2026)

| Norma | Aplica a | Autoridad / sanción |
|---|---|---|
| **LFPDPPP** (DOF 20-03-2025, reforma 14-11-2025) | Médico, consultorio, clínica, plataforma de telemedicina **privados** | Secretaría Anticorrupción y Buen Gobierno (SABG). Multas Art. 59 en UMA (ver abajo) |
| **LGPDPPSO** (nueva, DOF 20-03-2025) | Sujetos obligados **públicos** (IMSS, ISSSTE, SSA, hospitales públicos) | Autoridad garante del sector público según la LGPDPPSO 2025 — **verificar** cuál corresponde a cada orden de gobierno |
| **LGS Arts. 71 Bis–71 Octies** (Salud Digital, DOF 15-01-2026) | Servicios de telesalud | Art. 71 Septies fr. II: sistemas seguros que garanticen confidencialidad, integridad y disponibilidad |
| **NOM-004-SSA3-2012** | Expediente clínico | Conservación mínima 5 años desde el último acto médico (5.4); confidencialidad (5.5, 5.7) |
| **NOM-024-SSA3-2012** | Sistemas de expediente electrónico (SIRES) | Seguridad, trazabilidad, roles, firma electrónica avanzada (6.6.1–6.6.6) |

El INAI se extinguió: no se notifica ni se acude al INAI.

## Datos sensibles

Los datos de salud son **sensibles** (diagnósticos, tratamientos, resultados, historial psicológico/psiquiátrico, información genética, VIH/ITS, embarazo, discapacidad). Su tratamiento requiere **consentimiento expreso y por escrito** (firma autógrafa, firma electrónica o mecanismo de autenticación) — Art. 8 LFPDPPP 2025. Detalle de avisos y ARCO: skill compartida `compliance-lfpdppp`.

## Checklist de auditoría

```python
def auditar_compliance() -> dict:
    checks = {
        "consentimiento_expreso_escrito_datos_salud": validar_consentimientos(),   # Art. 8 LFPDPPP
        "aviso_privacidad_integral_publicado": existe_aviso_privacidad(),
        "cifrado_en_reposo_y_transito": verificar_cifrado(),                      # medida de seguridad, no cifra legal
        "bitacora_accesos_activa": verificar_audit_log(),                         # NOM-024 6.6.1 trazabilidad
        "acceso_por_roles": verificar_rbac(),                                     # NOM-024 6.6.4
        "conservacion_minimo_5_anios": verificar_retencion(),                     # NOM-004 5.4
        "bloqueo_y_supresion_post_conservacion": verificar_borrado(),
        "procedimiento_arco_documentado": existe_procedimiento(),
        "plan_respuesta_vulneraciones": existe_plan(),
        "personal_capacitado": verificar_capacitacion(),
    }
    return {
        "score_compliance": sum(checks.values()) / len(checks) * 100,
        "checks": checks,
        "pendientes": [k for k, v in checks.items() if not v],
    }
```

El score es una métrica interna de avance, no una certificación de cumplimiento.

## Vulneración de seguridad (fuga de datos)

- LFPDPPP 2025 Art. 19: informar **de forma inmediata** al titular cuando la vulneración afecte de forma significativa sus derechos patrimoniales o morales. La ley no fija un plazo en horas ni obliga a notificar a la SABG (fuente: skill compartida `compliance-lfpdppp`).
- Si el responsable es institución pública, revisar el régimen de notificación de la LGPDPPSO 2025 (**verificar**).
- Si hay delito (acceso ilícito a sistemas, extorsión): denuncia ante Ministerio Público.

Documentar: qué datos, cuándo se detectó, a quién afecta, mitigación aplicada, medidas preventivas.

## Derechos ARCO del paciente

Acceso, Rectificación, Cancelación (limitada: el expediente se conserva 5 años por NOM-004 5.4; procede bloqueo, no borrado inmediato) y Oposición.
Plazo: **20 días hábiles** para responder y **15 días hábiles** para hacerlo efectivo (Art. 31 LFPDPPP 2025). El resumen clínico se solicita por escrito (NOM-004 5.6).

## Multas (LFPDPPP Art. 59, impuestas por la SABG)

100 a 320,000 UMA según la infracción (más hasta 320,000 UMA si es reiterada); con datos sensibles pueden duplicarse. Con UMA 2026 = $117.31: de **$11,731** a **~$37.5 M MXN** por infracción (hasta ~$75 M con datos sensibles).

## Output auditoría

```json
{
  "fecha_auditoria": "2026-10-15",
  "marco": "LFPDPPP 2025 (privado)",
  "autoridad": "Secretaría Anticorrupción y Buen Gobierno",
  "score_compliance_pct": 90,
  "items_aprobados": 9,
  "items_pendientes": 1,
  "pendientes_detalle": [
    {
      "item": "plan_respuesta_vulneraciones",
      "criticidad": "alta",
      "accion": "Documentar protocolo de aviso inmediato al titular (Art. 19) y entrenar al equipo",
      "deadline_sugerido": "2026-11-15"
    }
  ],
  "audit_log_entries_mes": 1248,
  "vulneraciones_registradas_anio": 0
}
```
