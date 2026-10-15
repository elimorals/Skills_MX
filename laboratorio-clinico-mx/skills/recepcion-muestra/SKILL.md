---
name: recepcion-muestra
description: Recepción de muestras biológicas (sangre, orina, heces, esputo, citologías, biopsias) en laboratorio clínico conforme NOM-007-SSA3-2011 y manejo de residuos NOM-087-SEMARNAT-SSA1-2002. Asigna código de barras único ligado a paciente, médico solicitante y estudios; registra hora de toma y recepción (ventanas de estabilidad), tubo y aditivo correcto (rojo/amarillo química, morado EDTA hematología, gris fluoruro glucosa), validación preanalítica (hemólisis, lipemia, coágulos, volumen, ayuno) y cadena de custodia cuando aplica. Detecta etiquetas duplicadas o pacientes confundidos. Usar cuando el usuario diga recepcionar muestra, registrar tubo, etiquetar muestra, ingresar paciente al lab, toma de muestra. NO usar para entrega de resultados (usar entrega-resultados) ni para el procesamiento analítico.
allowed-tools: Read, Write, Edit
---

# Recepción de muestras en laboratorio clínico

## Datos obligatorios por muestra

```yaml
codigo_unico: LAB-2026-06-12-00342
paciente:
  rfc_o_curp: ABC...
  nombre: ...
  fecha_nacimiento: ...
  genero: H|M
medico_solicitante:
  nombre: Dr. ...
  cedula: ...
  contacto: ...
estudios_solicitados:
  - codigo_estudio: BHC
    nombre: Biometría Hemática Completa
    clave_sat_prodserv: "85121800"
    tubo_requerido: morado_edta
    volumen_min_ml: 2
fecha_hora_recepcion: 2026-06-12T10:32:00-06:00
ayuno_horas: 12
tomado_por: QFB María González (cédula 5432)
condicion_muestra:
  hemolizada: false
  lipemica: false
  coagulada: false
  volumen_suficiente: true
cadena_custodia: false  # true si toxicológico legal
prioridad: rutina  # urgente|rutina|preferente
fecha_estimada_resultados: 2026-06-12T14:00:00-06:00
```

## Validaciones críticas pre-aceptación

1. **Tubo correcto vs estudio solicitado** (error frecuente)
2. **Volumen mínimo** para procesar
3. **Sin hemólisis visible** (altera potasio, LDH, AST, entre otros; rechazar o reportar con nota según el procedimiento del lab)
4. **Sin coágulos en tubo con anticoagulante** (invalida hematología)
5. **Identificación legible** del tubo
6. **Ayuno cumplido** si requiere (glucosa, perfil lípidos)
7. **Tiempo desde toma** dentro de la ventana de estabilidad definida por el lab para cada estudio

## Información y consentimiento (NOM-007-SSA3-2011)

- Informar al paciente en términos comprensibles el procedimiento, requisitos y riesgos (4.4.2); carta de consentimiento en procedimientos de alto riesgo
- Si la muestra se usará en investigación o docencia: consentimiento por escrito ante dos testigos (4.5)
- Confidencialidad de toda la información del paciente (4.4.3); son datos sensibles (LFPDPPP 2025)

## Cadena de custodia (estudios con valor legal)

Para toxicológicos laborales, pruebas periciales o de paternidad:
- Firma del paciente
- Firma del recolector
- Foto del envase sellado
- Custodios sucesivos hasta resultado
- Resultado firmado por perito

## Output

```
muestras/<año>/<mes>/<dia>/<codigo>.json
muestras/cadena-custodia/<codigo>/  (si aplica)
```
