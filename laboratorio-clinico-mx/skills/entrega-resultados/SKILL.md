---
name: entrega-resultados
description: Entrega de resultados de laboratorio al paciente y/o al médico solicitante conforme NOM-007-SSA3-2011 - hoja membretada con razón social, domicilio, nombre y cédula del responsable sanitario; valores o intervalos de referencia según método, sexo y grupo de edad; marcador de fuera de rango; firma autógrafa, digitalizada o electrónica. Genera PDF para paciente (lenguaje claro) y para médico (detalle técnico), con interpretación combinada cuando aplica (perfil tiroideo, anemia). Entrega por portal, email, WhatsApp Business o impreso, cuidando confidencialidad de datos sensibles. Usar cuando el usuario diga entregar resultados, reporte lab, PDF de resultados, enviar resultados al médico, interpretación de resultados. NO usar para tracking previo (usar tracking-procesamiento) ni para liberar resultados sin firma.
allowed-tools: Read, Write, Edit
---

# Entrega de resultados de laboratorio

## Estructura del informe

### Cabecera

Obligatorio en informes impresos (NOM-007-SSA3-2011, hoja membretada):
- Nombre o razón social del laboratorio
- Domicilio del establecimiento
- Nombre y cédula profesional del **responsable sanitario**

Recomendado:
- Teléfono, datos del paciente, médico solicitante, fecha de toma y de informe
- No existe un "registro COFEPRIS" del laboratorio: el establecimiento opera con aviso de funcionamiento (o licencia si usa rayos X)

### Cuerpo

Por cada analito:
- Nombre del analito
- Resultado obtenido
- Unidades
- Valores o intervalos de referencia **impresos**, conforme al método usado, indicando sexo y grupo de edad a que corresponden (NOM-007 4.8)
- Marcador si fuera de rango (* o ↑↓)
- Método/equipo usado

### Pie

- Firma del responsable sanitario o personal autorizado: autógrafa, digitalizada o electrónica (NOM-007 5.1.8)
- Disclaimer: "Los resultados deben ser interpretados por su médico tratante"

## Confidencialidad del envío

Los resultados son datos sensibles: confidencialidad obligatoria (NOM-007 4.4.3) y consentimiento expreso del paciente para el canal de entrega (Art. 8 LFPDPPP 2025). Por WhatsApp/email preferir link con autenticación o PDF protegido; enviar al médico solo con autorización del paciente. Plantillas de WhatsApp: skill compartida `whatsapp-business-mx`.

## Rangos de referencia por demografía

Crítico: los rangos cambian y dependen del método. Valores **ilustrativos**; imprimir siempre los validados por el propio laboratorio:

| Analito | Hombre adulto | Mujer adulta | Niño 1-5 años |
|---|---|---|---|
| Hemoglobina g/dL | 13.5-17.5 | 12-15.5 | 11.5-14.5 |
| Creatinina mg/dL | 0.7-1.3 | 0.6-1.1 | 0.3-0.7 |
| FSH UI/L | 1.5-12.4 | varía ciclo / menopausia | <2 |
| Glucosa ayuno | 70-100 | 70-100 | 60-100 |

## Interpretación combinada (cuando aplica)

Algunos perfiles necesitan interpretación conjunta:

### Perfil tiroideo
- TSH ↑ + T4 ↓ → hipotiroidismo primario
- TSH ↓ + T4 ↑ → hipertiroidismo
- TSH normal + T4 normal → eutiroideo
- TSH ↑ + T4 normal → hipotiroidismo subclínico

### Perfil lípidos
- Riesgo cardiovascular según colesterol total + LDL + HDL + triglicéridos

### Anemia
- Hb baja + VCM bajo → ferropénica probable
- Hb baja + VCM normal → mixta o crónica
- Hb baja + VCM alto → megaloblástica (B12 o folato)

## Canales de entrega

| Destinatario | Canal | Formato |
|---|---|---|
| Paciente | WhatsApp + portal | PDF amigable |
| Médico solicitante | WhatsApp + email | PDF técnico |
| Paciente impresión | Recogiendo en lab | Papel firmado |

## Valores de pánico — notificación reforzada

Si hay valor de pánico:
1. NO esperar a que el paciente recoja
2. Llamar al médico solicitante en <30 min
3. Documentar llamada con timestamp + a quién
4. Si médico no responde: llamar a paciente + contacto de emergencia
