---
name: consentimiento-informado-tele
description: Consentimiento informado especifico para telemedicina, firmado digitalmente por paciente ANTES de primera consulta. Incluye limitaciones de la consulta remota (sin exploración física completa), riesgos de la modalidad, confidencialidad LFPDPPP/LGPDPPSO, excepciones (riesgo suicida, daño a terceros), honorarios, política cancelación, y derechos del paciente. Usar cuando el usuario diga consentimiento telemedicina, primera consulta online, autorizacion paciente remoto.
allowed-tools: Read, Write
---

# Consentimiento informado — telemedicina

## Contenido mínimo

### 1. Identificación
- Paciente (nombre completo + CURP o ID)
- Médico (nombre + cédula profesional + cédula especialidad si aplica)
- Fecha y firma electrónica

### 2. Naturaleza de la telemedicina
> La telemedicina es una modalidad de atención a distancia mediante videollamada. NO sustituye una consulta presencial cuando ésta sea clínicamente requerida.

### 3. Limitaciones reconocidas
- Sin auscultación
- Sin palpación
- Sin exploración íntima
- Calidad depende de conexión

### 4. Cuándo requiere consulta presencial
- Urgencia médica
- Sospecha de patología que requiere examen físico
- Procedimientos invasivos
- Cirugía

### 5. Confidencialidad y sus excepciones
- Datos protegidos por LGPDPPSO
- Excepciones para revelar info SIN consentimiento:
  - Riesgo suicida inminente del paciente
  - Daño confirmado a terceros
  - Abuso a menores detectado (reporte SIPINNA obligatorio)
  - Orden judicial específica

### 6. Honorarios y política
- Costo por consulta: $X
- Pre-pago obligatorio antes de la cita
- Política cancelación: con < 12h cobro 100%

### 7. Derechos del paciente (LFPDPPP)
- Acceso a su expediente
- Rectificación de datos
- Cancelación (con limitaciones legales)
- Oposición a tratamientos de datos secundarios

### 8. Firma electrónica del paciente
PDF firmado digitalmente (puede ser firma simple legalmente vinculante en MX, no requiere e.firma SAT del paciente).

## Output

```json
{
  "consentimiento_id": "CONS-TEL-001",
  "paciente_id_hash": "...",
  "medico_cedula": "1234567",
  "fecha_firma": "2026-06-12T15:00:00",
  "version_documento": "telemedicina-v1.2-2026",
  "pdf_path": "~/.local/share/plugins-mx/consentimientos/CONS-TEL-001.pdf",
  "incluye_limitaciones_exploracion": true,
  "incluye_excepciones_confidencialidad": true,
  "vigencia_indefinida": true,
  "metodo_firma": "firma_electronica_simple",
  "vigencia_validada": false
}
```

## ⚠ SIN consentimiento firmado: NO iniciar atención

El consentimiento es requisito legal previo. Si se atiende sin él:
- Demanda civil del paciente
- Sanción Comisión Conamed
- Posible cancelación cédula
