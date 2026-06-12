---
name: consentimiento-terapia-digital
description: Consentimiento informado para terapia psicológica firmado digitalmente por el paciente antes de iniciar tratamiento. Cubre: naturaleza del tratamiento, riesgos posibles, confidencialidad y sus excepciones (riesgo suicida, daño a terceros, abuso menores), honorarios, política cancelación, derechos LFPDPPP. Usar cuando el usuario diga consentimiento terapia, contrato terapia, primera sesion.
allowed-tools: Read, Write
---

# Consentimiento terapia digital

## Contenido mínimo

1. **Identificación**: nombre paciente, nombre terapeuta, cédula
2. **Naturaleza del tratamiento**: enfoque (CBT, psicoanalítico, EMDR, etc.)
3. **Duración esperada**: típica 12-24 sesiones, ajustable
4. **Confidencialidad + excepciones**:
   - Riesgo suicida inminente → contacto familiar + autoridades
   - Daño a terceros confirmado → reporte legal
   - Abuso a menores detectado → reporte SIPINNA
   - Orden judicial específica
5. **Honorarios + política**: $X/sesión, cancelación con < 24h cobro 100%
6. **Frecuencia**: 1x/semana típico
7. **Derechos LFPDPPP**: acceso, rectificación, cancelación, oposición
8. **Firma digital paciente**

## Salida

```json
{
  "consentimiento_id": "CONS-001",
  "paciente_id_hash": "...",
  "fecha_firma": "2026-06-12",
  "version_documento": "v1.2",
  "incluye_excepciones_confidencialidad": true,
  "pdf_firmado_path": "...",
  "vigencia_indefinida": true,
  "vigencia_validada": false
}
```

## ⚠ Sin consentimiento firmado: NO iniciar tratamiento
