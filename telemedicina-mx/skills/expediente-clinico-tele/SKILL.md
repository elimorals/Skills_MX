---
name: expediente-clinico-tele
description: Expediente clínico electrónico para consultas de telemedicina conforme NOM-004-SSA3-2012 (historia clínica y notas de evolución), NOM-024-SSA3-2012 (sistemas electrónicos) y LGS Art. 71 Septies (registro de atenciones por plataformas digitales, decreto DOF 15-01-2026). Agrega marcadores de consulta remota (qué se evaluó por video, limitaciones de exploración física, calidad de conexión). Cifrado en reposo, bitácora de accesos, conservación mínima 5 años. Usar cuando el usuario diga expediente telemedicina, historia clínica remota, notas de consulta online, nota de evolución videoconsulta.
allowed-tools: Read, Write
---

# Expediente clínico — telemedicina

> Apoyo documental. El contenido clínico y la firma son responsabilidad del médico tratante.

## Contenido mínimo (NOM-004-SSA3-2012)

**Historia clínica (6.1)**, en este orden:
1. Interrogatorio (6.1.1): ficha de identificación, grupo étnico en su caso, antecedentes heredo-familiares, personales patológicos (incluye tabaco, alcohol y otras sustancias) y no patológicos, padecimiento actual, interrogatorio por aparatos y sistemas
2. Exploración física (6.1.2): habitus exterior, signos vitales, peso y talla, segmentos corporales — **en telemedicina documentar qué se pudo evaluar y qué no**
3. Resultados de estudios de laboratorio y gabinete (6.1.3)
4. Diagnósticos o problemas clínicos (6.1.4) — CIE-10 recomendado
5. Pronóstico (6.1.5)
6. Indicación terapéutica (6.1.6)

**Nota de evolución (6.2)** en cada atención: evolución del cuadro, signos vitales según se considere necesario, resultados relevantes, diagnósticos, pronóstico, tratamiento e indicaciones (medicamento con dosis, vía y periodicidad).

Toda nota lleva fecha, hora, nombre completo y firma (autógrafa, electrónica o digital) de quien la elabora (5.10).

Cartas de consentimiento informado: obligatorias en los eventos de 10.1.2 (hospitalización, cirugía mayor, anestesia, alto riesgo, etc.). Para la modalidad a distancia, la LGS Art. 71 Septies fr. III exige además un mecanismo de consentimiento informado → ver skill `consentimiento-informado-tele`.

## Adaptaciones para telemedicina

### Exploración física limitada
- ✅ Lo que SÍ se evaluó (inspección visual, marcha, habla, estado mental, signos visibles, signos vitales reportados por el paciente con su equipo)
- ❌ Lo que NO (auscultación, palpación, exploración íntima)
- 📋 Si requiere consulta presencial complementaria

### Datos de la atención remota (LGS Art. 71 Septies fr. IV: documentación y registro)
- Plataforma usada, duración, calidad de audio/video
- Ubicación declarada del paciente (estado/país)
- Privacidad (¿estaba solo? ¿acompañante?)

## Seguridad (NOM-024-SSA3-2012 si el sistema es un SIRES)

- CURP como identificador del paciente (6.5.1)
- Gestión de seguridad con confidencialidad, integridad, disponibilidad, trazabilidad y no repudio (6.6.1)
- Documentos inalterables y firma electrónica avanzada del profesional (6.6.2)
- Autenticación de usuarios y acceso por roles (6.6.3, 6.6.4)
- Cifrado en reposo (p. ej. AES-256-GCM) y bitácora de cada lectura/escritura: buena práctica para cumplir lo anterior
- Conservación: **mínimo 5 años desde el último acto médico** (NOM-004 5.4)
- Fuga de datos: multas LFPDPPP Art. 59 (hasta ~$37.5 M MXN por infracción con UMA 2026, duplicables con datos sensibles) + responsabilidad civil → ver `compliance-lgpdppso-salud`

El decreto DOF 15-01-2026 (Salud Digital) obliga a las instituciones públicas a implementar la salud digital; no vuelve obligatorio el expediente electrónico para consultorios privados.

MCP opcional: `mp_expediente_clinico_nom024` → `ece_validar_sistema` (autoevaluación por numeral de la NOM-024; cálculo local, no certificación).

## Output

```json
{
  "expediente_id_hash": "...",
  "paciente_curp_hash": "...",
  "modalidad": "telemedicina",
  "ultima_consulta": "2026-10-12T16:30:00-06:00",
  "completitud_pct": 87,
  "elementos_faltantes": ["exploracion_fisica_complementaria"],
  "limitaciones_exploracion": ["sin_palpacion_abdominal", "sin_auscultacion"],
  "requiere_complemento_presencial": true,
  "diagnosticos_activos": ["I10", "F32.1"],
  "conservar_hasta_minimo": "2031-10-12"
}
```
