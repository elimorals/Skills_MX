---
name: entrega-resultados
description: Entrega de resultados al paciente y/o al médico solicitante con firma del químico responsable (QFB con cédula profesional vigente — requisito legal) y validación previa de que valores fuera de rango llevan asterisco de alerta + comentario explicativo + rangos de referencia por edad y sexo (los rangos cambian: hemoglobina mujer ≠ hombre, creatinina niño ≠ adulto, hormonas embarazada ≠ no embarazada). Genera reporte PDF presentable con logo del lab + datos del paciente + cuadro de resultados con valores y rangos + interpretación cuando aplica (perfil tiroideo necesita interpretación combinada TSH+T3+T4). Diferencia entre entrega a paciente (con explicación amigable) y a médico (con detalle técnico). Soporta entrega vía WhatsApp Business con PDF adjunto + email + impresión + portal del paciente. Cumple NOM-007-SSA3 sobre informe de resultados. Notifica al médico cuando un valor de pánico requiere intervención inmediata. Usar cuando el usuario diga "entregar resultados", "reporte lab", "PDF resultados paciente", "enviar lab a médico", "interpretación resultados". NO usar para tracking previo (usar tracking-procesamiento) ni para resultados patológicos críticos sin firma.
allowed-tools: Read, Write, Edit
---

# Entrega de resultados de laboratorio

## Estructura del informe

### Cabecera (obligatoria NOM-007)

- Nombre completo del laboratorio
- Dirección y teléfono
- Cédula del director técnico (QFB)
- Registro COFEPRIS
- Datos del paciente
- Médico solicitante
- Fecha de toma y de informe

### Cuerpo

Por cada analito:
- Nombre del analito
- Resultado obtenido
- Unidades
- Rango de referencia (¡por edad y sexo!)
- Marcador si fuera de rango (* o ↑↓)
- Método/equipo usado

### Pie

- Firma electrónica del QFB responsable
- Sello digital del lab
- Disclaimer: "Los resultados deben ser interpretados por su médico tratante"

## Rangos de referencia por demografía

Crítico: los rangos cambian. Ejemplos:

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
