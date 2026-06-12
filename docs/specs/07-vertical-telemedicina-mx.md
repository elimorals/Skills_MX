---
spec: "vertical-telemedicina-mx"
estado: "DRAFT"
creado: "2026-06-12"
autor: "Elias"
ultima_actualizacion: "2026-06-12"
esfuerzo_estimado_horas: [350, 580]
prioridad: "tier-1"
---

# Spec 07 — Vertical `telemedicina-mx`

## 1. Propósito

Plugin para médicos, psicólogos y profesionales de la salud que ofrecen **consultas remotas** en México. Mercado potencial: ~120k profesionales (médicos + dentistas + psicólogos con consultorio privado), del cual ~25-30% migró a telemedicina post-COVID.

Resuelve los **3 dolores no resueltos** del médico que hace consulta remota:
1. Receta electrónica con cumplimiento COFEPRIS (firma vigente, cédula profesional, datos del paciente)
2. Expediente clínico electrónico conforme NOM-004-SSA3-2012 (obligatorio sin importar el formato)
3. Compliance LFPDPPP + LGPDPPSO con datos sensibles de salud (consentimiento informado + cifrado en reposo)

## 2. Contexto y por qué es novedoso

- **No existe vertical de salud en el repo**: `veterinaria-mx` cubre clínicas veterinarias pero no humanos
- **Regulación 2026 cambió**: la **Reforma a la Ley General de Salud (enero 2026)** ya reconoce expresamente la telemedicina; antes era zona gris
- **Receta electrónica**: NOM-024-SSA3-2010 + reforma 2026; **Grupos I-II controlados aún requieren receta física con código de barras** (digital NO sustituye)
- **NOM-004-SSA3-2012**: expediente clínico vigente, criterios obligatorios técnicos + administrativos + de confidencialidad
- **Diferencia vs `freelancers-mx`**: profesional de salud tiene obligaciones específicas (cédula profesional, expediente, COFEPRIS) y NO solo fiscales

## 3. Alcance

**Dentro:**
- Receta electrónica con validación COFEPRIS + cédula profesional + e.firma del médico
- Expediente clínico básico (10 elementos NOM-004) cifrado en reposo
- Consentimiento informado digital firmado por paciente (LFPDPPP Art. 16)
- Calendario consultas (integración Calendly/Zoom/Google Meet vía webhook)
- CFDI tipo I uso D01 (honorarios médicos — deducible para el paciente si paga no-efectivo)
- Cobranza recurrente para terapias (psicología) con plantillas empáticas
- Catálogo CIE-10 básico (diagnósticos)

**Fuera (decisión deliberada):**
- Medicamentos controlados Grupos I-II (requieren receta física con código de barras — pendiente piloto COFEPRIS 2026-2027)
- Telemedicina IMSS / ISSSTE / SaludDigna (sector público, otra regulación)
- Cirugías / procedimientos invasivos remotos (imposible)
- Imágenes diagnósticas (PACS) — escala distinta
- Hospitales completos (vertical aparte: `clinica-salud-mx`)

## 4. Inputs / outputs / schemas

### Setup médico

```python
class PerfilMedico(BaseModel):
    rfc: str
    cedula_profesional: str  # cédula federal SEP
    especialidad: str        # ej. "medico_general", "pediatra", "psicologo_clinico"
    cedula_especialidad: str | None  # solo si médico especialista
    licencia_sanitaria_consultorio: str | None  # COFEPRIS si aplica
    e_firma_path_cer: Path
    regimen_fiscal: Literal["612", "626"]  # PFAE o RESICO PF
```

### Receta electrónica

```python
class RecetaElectronica(BaseModel):
    paciente: PacienteInfo  # mínimo: nombre, edad, peso
    diagnostico_cie10: str
    medicamentos: list[Medicamento]
    indicaciones_no_farmacologicas: str
    fecha_emision: datetime
    proxima_consulta_sugerida: date | None
    medico_cedula: str
    medico_e_firma_signature: bytes  # firma digital del documento
    contiene_controlado_grupo: int | None  # 0/1/2/3 — si 1 o 2 → bloquea (requiere receta física)
```

### Schema expediente NOM-004

10 elementos obligatorios:
1. Ficha de identificación del paciente
2. Antecedentes (heredo-familiares, personales)
3. Padecimiento actual + interrogatorio
4. Exploración física
5. Diagnósticos
6. Plan de tratamiento
7. Pronóstico
8. Notas de evolución
9. Receta y/o solicitudes (estudios)
10. Hoja de consentimiento informado

## 5. Skills propuestos (10)

| Skill | Cuándo activa |
|---|---|
| `dashboard-consultas-semana` | Status semanal médico |
| `agendar-consulta-remota` | Crear cita + link Zoom/Meet |
| `expediente-clinico-nom004` | Crear/actualizar expediente |
| `receta-electronica-cofepris` | Generar receta + firma e.firma |
| `consentimiento-informado-digital` | Firma paciente antes 1ra consulta |
| `cfdi-honorario-medico-d01` | Emisión CFDI uso D01 |
| `cobranza-terapia-recurrente` | Cobranza mensual psicólogo |
| `recordatorios-paciente-wa` | WhatsApp consulta + medicamentos |
| `interacciones-medicamentosas` | Validación básica antes recetar |
| `compliance-lgpdppso-salud` | Auditoría datos sensibles cifrados |

## 6. Comandos (5)

```
/tele:dashboard
/tele:agendar
/tele:receta
/tele:expediente
/tele:facturar
```

## 7. Workflow

`workflow-consulta-remota-completa.md` — orquestador end-to-end:
1. Verificar paciente firmó consentimiento (sino: enviar antes)
2. Validar cédula médico vigente (registro federal)
3. Realizar consulta (videocall externo)
4. Actualizar expediente NOM-004
5. Emitir receta si aplica (con check Grupo I-II)
6. Emitir CFDI uso D01
7. Programar próxima consulta + recordatorio WA

## 8. Casos edge

| Caso | Acción |
|---|---|
| Paciente solicita medicamento controlado grupo I-II | BLOQUEAR — requiere receta física + sello COFEPRIS |
| Paciente sin RFC (XAXX...) | Permitir CFDI XAXX010101000, paciente no podrá deducir |
| Médico sin cédula vigente | BLOQUEAR — ilegal practicar |
| Datos del paciente comprometidos (filtración) | Notificar paciente + IFAI dentro de 72h (LGPDPPSO Art. 80) |
| Menor de edad | Consentimiento de padre/tutor obligatorio |
| Paciente extranjero | Validar pasaporte como ID, CFDI con XAXX |
| Urgencia médica detectada en consulta remota | Protocolo derivación a presencial inmediato |
| Receta vencida (paciente vuelve pidiendo refill) | Re-consulta requerida si pasaron > 30 días |

## 9. Dependencias

- **MCPs**: `mp_sat_portal` (validación RFC paciente, e.firma médico), `mp_facturama_extendido` (CFDI D01), `mp_meta_whatsapp` (recordatorios)
- **MCPs nuevos sugeridos** (V2):
  - `mp_cofepris_recetario` — validación cédula + reporte controlados (no existe API pública, scrape) 
  - `mp_zoom_meetings` o `mp_google_meet` — generación link videocall
- **Skills `_shared/`**: cfdi-emision, rfc-validacion, mxn-formato, compliance-lfpdppp, whatsapp-business-mx

## 10. Criterios de aceptación

- [ ] Plugin completo con plugin.json + 10 skills + 5 commands
- [ ] Receta electrónica con e.firma del médico embebida
- [ ] Bloqueo automático si receta incluye Grupo I-II
- [ ] Expediente NOM-004 cifrado en reposo (AES-256)
- [ ] Consentimiento informado se firma DIGITALMENTE por paciente
- [ ] CFDI D01 con datos del paciente para que pueda deducir
- [ ] Hashear nombre paciente + RFC en bitácora
- [ ] Tests con 5 fixtures (consulta general, psicoterapia, seguimiento, urgencia derivada, receta bloqueada)
- [ ] Lint passing

## 11. Esfuerzo estimado

- **Scaffold plugin + plugin.json**: 5-10h
- **10 skills**: 100-160h (~10-16h/skill)
- **5 comandos + 1 workflow**: 30-50h
- **Cifrado en reposo expediente**: 25-40h
- **Generación PDF receta con e.firma embed**: 30-50h
- **Validación cédula profesional contra registro federal SEP**: 20-30h (sin API pública, scrape)
- **Tests + fixtures (10+)**: 35-60h
- **Docs + compliance LGPDPPSO**: 25-40h
- **Validación legal con abogado especializado salud**: 5-10h coordinación
- **Validación con médico colegiado**: 5-10h coordinación
- **TOTAL**: **280-460 horas** (~7-12 semanas FT)

## 12. Riesgos + mitigaciones

| Riesgo | Prob | Impacto | Mitigación |
|---|---|---|---|
| Filtración de datos médicos | Baja | **CRÍTICO** (LGPDPPSO multas hasta $40M MXN) | Cifrado en reposo + acceso solo médico autorizado + audit log |
| Receta de medicamento controlado sin saberlo | Media | Alto | Catálogo COFEPRIS actualizado + bloqueo Grupo I-II hard |
| Cédula médico falsa/vencida | Baja | Crítico | Validar contra SEP cada 6 meses |
| Receta digital rechazada en farmacia | Media | Medio | QR + firma visible + nota legal "válida por LGS 2026" |
| Reformas LGS post-2026 cambien validez digital | Media | Alto | Diseño modular para adaptar |
| Diagnóstico erróneo remoto = mala praxis | Media | Alto | Disclaimer + protocolo de derivación presencial |

## 13. Decisiones pendientes

- [ ] ¿PDF receta firmada vs JSON estructurado? (PDF cumple, JSON futuro)
- [ ] ¿Cifrado de expediente: clave del médico o gestionada por sistema?
- [ ] ¿Integrar PACS para radiología o dejar fuera (V2)?
- [ ] ¿Compatibilidad con sistema HIS/RIS de hospitales (HL7 FHIR)?
- [ ] ¿Pricing: $399 MXN/mes médico individual o $1,500/mes consultorio multi-médico?

## 14. Plan de implementación

### Fase 1: Scaffold + setup (10-15h)
1. plugin.json + README
2. Estructura folders
3. Sync _shared/

### Fase 2: Compliance crítico (40-60h)
1. Cifrado AES-256 expediente en reposo
2. Consentimiento informado firmado digitalmente
3. Audit log con hashes
4. Validación cédula profesional

### Fase 3: Skills clínicos (60-100h)
1. expediente-clinico-nom004
2. receta-electronica-cofepris (con bloqueo Grupos)
3. interacciones-medicamentosas
4. consentimiento-informado-digital

### Fase 4: Skills operativos (40-60h)
5. dashboard-consultas-semana
6. agendar-consulta-remota
7. cobranza-terapia-recurrente
8. recordatorios-paciente-wa

### Fase 5: Skills fiscales (30-50h)
9. cfdi-honorario-medico-d01
10. compliance-lgpdppso-salud

### Fase 6: Comandos + workflow (30-50h)
1. 5 commands
2. workflow-consulta-remota-completa
3. Integración Zoom/Meet (link generation)

### Fase 7: PDF + e.firma (30-50h)
1. Template PDF receta profesional
2. Embed firma médico
3. QR de verificación

### Fase 8: Tests + docs (40-60h)

## 15. Links

- [Receta Médica COFEPRIS Guía 2026](https://www.marketingmedicos.com.mx/blogs/marketing-medico/como-hacer-una-receta-medica-conforme-a-cofepris-2026)
- [Receta Electrónica México - SaludTotal](https://saludtotal.mx/es/blog/receta-electronica-medica/)
- [Doc24 - Requisitos telemedicina](https://doc24.com.mx/requisitos-para-implementar-telemedicina-en-mexico/)
- [NOM-004-SSA3-2012 - Expediente clínico](http://dof.gob.mx/nota_detalle.php?codigo=5272787)
- [NOM-024-SSA3-2010 - Sistemas electrónicos](https://www.dof.gob.mx/nota_detalle.php?codigo=5103686)
- [Reforma LGS enero 2026](http://sil.gobernacion.gob.mx/Archivos/Documentos/2025/11/asun_4977043_20251119_1763080847.pdf)
