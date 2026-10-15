---
name: consentimiento-terapia-digital
description: Consentimiento informado para terapia psicológica firmado digitalmente por el paciente antes de iniciar tratamiento. Cubre: naturaleza del tratamiento, riesgos posibles, confidencialidad y sus excepciones (riesgo suicida, daño a terceros, abuso menores), honorarios, política cancelación, consentimiento expreso para datos sensibles (LFPDPPP 2025) y, si es en línea, telesalud (LGS Art. 71 Septies). Usar cuando el usuario diga consentimiento terapia, contrato terapéutico, encuadre, primera sesión, consentimiento psicología en línea.
allowed-tools: Read, Write
---

# Consentimiento terapia digital

## Contenido mínimo

1. **Identificación**: nombre paciente, nombre terapeuta, cédula
2. **Naturaleza del tratamiento**: enfoque (CBT, psicoanalítico, EMDR, etc.)
3. **Duración esperada**: típica 12-24 sesiones, ajustable
4. **Confidencialidad + excepciones**:
   - Riesgo suicida inminente → contacto con familiar/persona de confianza y servicios de urgencia
   - Riesgo serio de daño a terceros
   - Sospecha de maltrato o abuso a niñas, niños o adolescentes → aviso a la Procuraduría de Protección de NNA o al Ministerio Público (LGDNNA; confianza media, verificar artículo). SIPINNA es un sistema de coordinación, no un canal de denuncia
   - Requerimiento de autoridad judicial o administrativa competente
5. **Honorarios + política**: $X/sesión (+ IVA 16% si es psicólogo, ver `cobranza-recurrente-terapia`), cancelación con < 24h cobro 100% (informarlo por escrito antes de iniciar)
6. **Frecuencia**: 1x/semana típico
7. **Datos personales sensibles**: consentimiento expreso y por escrito para tratar datos de salud mental (Art. 8 LFPDPPP 2025); derechos ARCO con respuesta en 20 días hábiles (Art. 31); autoridad: Secretaría Anticorrupción y Buen Gobierno (ya no INAI)
8. **Si la terapia es en línea**: plataforma usada, no grabar sin autorización, mecanismo de consentimiento para telesalud (LGS Art. 71 Septies fr. III, DOF 15-01-2026)
9. **Firma digital paciente** (firma electrónica simple con evidencia de autenticación)

> Plantilla orientativa; revisar con abogado y con el código ético de tu colegio profesional.

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
