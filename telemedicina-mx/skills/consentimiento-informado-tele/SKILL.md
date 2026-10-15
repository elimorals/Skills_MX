---
name: consentimiento-informado-tele
description: Consentimiento informado específico para telemedicina, firmado electrónicamente por el paciente ANTES de la primera consulta remota. Fundamento LGS Art. 71 Septies fr. III (mecanismo de consentimiento informado en telesalud, DOF 15-01-2026) y consentimiento expreso por escrito para datos de salud (Art. 8 LFPDPPP 2025). Incluye limitaciones de la consulta remota, cuándo acudir en persona, confidencialidad y sus excepciones, honorarios, política de cancelación y derechos ARCO. Usar cuando el usuario diga consentimiento telemedicina, primera consulta online, autorización paciente remoto, carta de consentimiento videoconsulta.
allowed-tools: Read, Write
---

# Consentimiento informado — telemedicina

> Plantilla orientativa; revisar con abogado sanitario antes de usarla.

## Fundamento

- **LGS Art. 71 Septies fr. III** (DOF 15-01-2026): los servicios de telesalud deben incorporar mecanismos de consentimiento informado que garanticen comprensión y voluntariedad.
- **LFPDPPP 2025 Art. 8**: datos de salud = sensibles → consentimiento expreso y por escrito (firma autógrafa, electrónica o mecanismo de autenticación).
- **NOM-004-SSA3-2012 10.1**: cartas de consentimiento obligatorias para los eventos de 10.1.2 (hospitalización, cirugía, anestesia, alto riesgo); se pueden recabar cartas adicionales (10.1.3).

## Contenido mínimo

1. **Identificación**: paciente (nombre completo + CURP o identificación), médico (nombre, cédula profesional y de especialidad si aplica), fecha.
2. **Naturaleza**: atención a distancia por videollamada; no sustituye la consulta presencial cuando sea clínicamente necesaria.
3. **Limitaciones**: sin auscultación, palpación ni exploración íntima; la calidad depende de la conexión.
4. **Cuándo acudir en persona**: urgencias, sospecha que requiere examen físico, procedimientos.
5. **Confidencialidad y excepciones**:
   - Riesgo inminente para la vida del paciente o de terceros
   - Sospecha de maltrato o abuso a niñas, niños o adolescentes → aviso a la Procuraduría de Protección de NNA o al Ministerio Público (LGDNNA; confianza media, verificar artículo)
   - Requerimiento de autoridad judicial o administrativa competente (NOM-004 5.6)
   - Notificación epidemiológica obligatoria
6. **Datos personales**: aviso de privacidad, plataforma usada, si la sesión se graba (solo con autorización expresa), conservación del expediente mínimo 5 años (NOM-004 5.4).
7. **Honorarios y política**: costo, prepago si aplica, cancelación (p. ej. < 12 h se cobra 100%; informarlo antes de contratar, LFPC).
8. **Derechos ARCO** (LFPDPPP 2025): acceso, rectificación, cancelación (limitada por la obligación de conservar), oposición; respuesta en 20 días hábiles (Art. 31).
9. **Firma electrónica del paciente**: firma electrónica simple con evidencia de autenticación (correo/teléfono verificado, sello de tiempo). No requiere e.firma SAT.

## Output

```json
{
  "consentimiento_id": "CONS-TEL-001",
  "paciente_id_hash": "...",
  "medico_cedula": "1234567",
  "fecha_firma": "2026-10-15T15:00:00-06:00",
  "version_documento": "telemedicina-v2.0-2026",
  "pdf_path": "~/.local/share/plugins-mx/consentimientos/CONS-TEL-001.pdf",
  "incluye_limitaciones_exploracion": true,
  "incluye_excepciones_confidencialidad": true,
  "consentimiento_datos_sensibles": true,
  "metodo_firma": "firma_electronica_simple",
  "vigencia_validada": false
}
```

## ⚠ Sin consentimiento firmado: no iniciar la atención remota

Atender sin él deja al médico sin evidencia del cumplimiento del Art. 71 Septies y del Art. 8 LFPDPPP (multas de la SABG) y debilita su defensa ante una queja en CONAMED (que concilia y arbitra, no sanciona) o una demanda civil. Excepción: urgencia, según el Art. 81 del Reglamento de la LGS en materia de prestación de servicios de atención médica (NOM-004 10.1.4).
