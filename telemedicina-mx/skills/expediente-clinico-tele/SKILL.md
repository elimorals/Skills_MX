---
name: expediente-clinico-tele
description: Expediente clínico electrónico conforme NOM-004-SSA3-2012 adaptado para telemedicina. Mismos 10 elementos obligatorios del expediente regular, con marcadores adicionales para identificar consultas remotas (limitaciones de exploración física, qué se evaluó por video). Cifrado AES-256 en reposo, audit log obligatorio LGPDPPSO. Usar cuando el usuario diga expediente telemedicina, historia clinica remota, notas consulta online.
allowed-tools: Read, Write
---

# Expediente clínico telemedicina

## 10 elementos NOM-004 (mismos que consultorio presencial)

1. Ficha identificación
2. Antecedentes
3. Padecimiento actual
4. Exploración física (LIMITADA en telemedicina — documentar qué se evaluó por video)
5. Diagnósticos CIE-10
6. Plan tratamiento
7. Pronóstico
8. Notas evolución
9. Receta/solicitudes
10. Consentimiento informado

## Adaptaciones específicas para telemedicina

### Exploración física limitada
Documentar explícitamente:
- ✅ Lo que SÍ se pudo evaluar (inspección visual, marcha, habla, estado emocional, signos visibles)
- ❌ Lo que NO se pudo (auscultación, palpación, exploración íntima)
- 📋 Si requiere consulta presencial complementaria

### Calidad de la consulta
- Calidad video (HD vs baja)
- Calidad audio
- Privacidad del paciente (¿estaba solo? ¿familiar presente?)
- Cooperación del paciente

## ⚠ Compliance crítico

- **Cifrado AES-256-GCM** en reposo (clave del médico, no en servidor)
- **Audit log** obligatorio: cada lectura/escritura registrada
- **Acceso restringido** solo médico tratante
- **Retención mínima**: 5 años post última consulta (NOM-004)
- **Filtración** = sanción LGPDPPSO hasta $40M MXN + responsabilidad civil

## Output

```json
{
  "expediente_id_hash": "...",
  "paciente_rfc_hash": "...",
  "modalidad": "telemedicina",
  "ultima_consulta": "2026-06-12T16:30:00-06:00",
  "completitud_pct": 87,
  "elementos_faltantes": ["exploracion_fisica_complementaria"],
  "limitaciones_exploracion": ["sin_palpacion_abdominal", "sin_auscultacion"],
  "requiere_complemento_presencial": true,
  "diagnosticos_activos": ["I10", "F32.1"]
}
```
