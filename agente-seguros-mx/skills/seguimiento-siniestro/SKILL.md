---
name: seguimiento-siniestro
description: Gestiona el seguimiento de siniestros reportados por el cliente al agente con bitácora cronológica (reporte inicial, asignación de ajustador, inspección, dictamen, aprobación o rechazo, indemnización o reposición, cierre), control del plazo legal de pago (la indemnización vence 30 días después de que la aseguradora recibe los documentos e información completos, Art. 71 LSCS; si se atrasa, intereses por mora del Art. 276 LISF), prescripción (2 años, 5 en fallecimiento de vida, Art. 81 LSCS), documentación por ramo (auto, GMM, daños, vida) y escalación a CONDUSEF cuando la aseguradora rechaza sin razón válida o se excede el plazo. Documenta el historial de siniestralidad del cliente para renovaciones. Usar cuando el usuario diga "siniestro cliente", "seguir reclamación", "ajustador no llega", "tracking siniestro", "reclamación aseguradora", "aseguradora no paga". NO usar para el reporte inicial del siniestro (eso es directo a la aseguradora) ni para reembolso GMM individual del asegurado.
allowed-tools: Read, Write, Edit
---

# Seguimiento de siniestros

## Etapas del proceso

Solo el plazo de pago es legal; los demás son tiempos típicos de mercado.

| Etapa | Plazo | Acción del agente |
|---|---|---|
| Reporte inicial | Inmediato (y dentro del plazo de aviso de la póliza) | Acompañar al cliente con la aseguradora |
| Asignación de ajustador | Típico 24-48 h | Validar que sea asignado |
| Inspección | Típico 5-10 días | Coordinar acceso del ajustador |
| Documentación | Variable | Reunir según ramo; pedir acuse de recibo con fecha |
| Dictamen | Típico 15-30 días | Recibir y revisar |
| Pago | **Legal: 30 días desde la entrega completa de documentos (Art. 71 LSCS)** | Confirmar transferencia |
| Cierre | — | Documentar para historial |

Si la aseguradora no paga en plazo, debe una indemnización por mora calculada en UDIS más intereses (Art. 276 LISF). Registra la fecha del acuse de la documentación completa: de ahí corre el plazo.

## Prescripción

Las acciones del contrato de seguro prescriben en 2 años, y en 5 años la cobertura de fallecimiento en vida, contados desde el hecho que les dio origen (Art. 81 LSCS). Alerta 90 días antes.

## Documentación por ramo

### Auto
- Parte de policía o del ministerio público (si aplica)
- Fotos del siniestro
- INE del conductor, licencia y tarjeta de circulación
- Factura del vehículo (si robo total o pérdida total)

### GMM
- Informe médico y receta
- CFDI de honorarios médicos, hospital y medicamentos
- Estudios con interpretación
- Formato de reclamación de la aseguradora

### Daños
- Denuncia ante el ministerio público (si robo)
- Fotos
- Presupuesto de reparación con desglose
- Comprobante de propiedad

### Vida
- Acta de defunción
- Certificado de defunción
- Identificación oficial de los beneficiarios
- Documento que acredite el parentesco si la póliza lo exige

## Escalación a CONDUSEF

Cuándo:
1. La aseguradora rechaza sin fundamento en las condiciones generales.
2. Pasan más de 30 días desde la entrega completa de documentos sin pago.
3. Pide documentación adicional improcedente.

Primero la reclamación ante la Unidad Especializada (UNE) de la aseguradora; después, reclamación ante CONDUSEF (portal o asesoría presencial). El agente prepara el expediente; la queja la presenta el asegurado o beneficiario. Verifica los datos de la institución con `sipres_buscar_institucion` (MCP `mp_condusef_sipres`).

> No es asesoría legal: en rechazos de montos altos, recomienda abogado especializado en seguros.
