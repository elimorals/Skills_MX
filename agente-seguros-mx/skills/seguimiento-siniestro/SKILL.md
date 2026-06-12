---
name: seguimiento-siniestro
description: Gestiona seguimiento end-to-end de siniestros reportados por el cliente al agente con bitácora cronológica (reporte inicial, asignación de ajustador por aseguradora, inspección, dictamen, aprobación o rechazo, indemnización o reposición, cierre), tracking de plazos legales (CNSF establece 30 días naturales para resolver tras documentos completos, 90 días para complejos), recordatorios al ajustador cuando excede plazos, gestión de documentación requerida por ramo (auto: parte de policía, fotos, INE, factura; GMM: receta, CFDI, estudios, etiquetas medicamento, hoja de evolución; daños: parte ministerial, fotos, presupuesto reparación; vida: acta defunción, certificado médico de defunción, identificación beneficiarios), y escalación a CONDUSEF cuando aseguradora rechaza sin razón válida o se excede el plazo legal. Documenta historial de siniestralidad del cliente para impacto en renovaciones. Usar cuando el usuario diga "siniestro cliente", "seguir reporte AXA", "ajustador GNP", "tracking siniestro", "reclamación aseguradora". NO usar para reporte inicial del siniestro (eso es directo a la aseguradora) ni para reembolso GMM individual del asegurado.
allowed-tools: Read, Write, Edit
---

# Seguimiento de siniestros

## Etapas del proceso

| Etapa | Plazo CNSF | Acción del agente |
|---|---|---|
| Reporte inicial | Inmediato | Acompañar al cliente con la aseguradora |
| Asignación de ajustador | 24-48h | Validar que sea asignado |
| Inspección | 5-10 días | Coordinar acceso del ajustador |
| Documentación | Variable | Reunir según ramo |
| Dictamen | 15-30 días | Recibir y revisar |
| Aprobación/rechazo | 30 días | Si rechazo: analizar causa |
| Indemnización | 5-15 días post-aprobación | Confirmar transferencia |
| Cierre | — | Documentar para historial |

## Documentación por ramo

### Auto
- Parte de policía o ministerio público
- Fotos del siniestro
- INE del conductor + tarjeta de circulación
- Factura del vehículo (si robo total)

### GMM
- Receta médica
- CFDI de honorarios + medicamentos
- Estudios + interpretación
- Etiquetas de medicamentos
- Hoja de evolución
- Carta autorización si requiere reembolso

### Daños
- Parte ministerial
- Fotos
- Presupuesto de reparación con desglose
- Comprobante propiedad

### Vida
- Acta de defunción
- Certificado médico de defunción
- INE de beneficiarios
- Acta de nacimiento (relación con asegurado)

## Escalación a CONDUSEF

Cuando:
1. Aseguradora rechaza sin base legal
2. Excede plazo de 30 días naturales
3. Solicita documentación adicional improcedente

Output: queja formal en plataforma CONDUSEF + seguimiento.
