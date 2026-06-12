---
name: recepcion-muestra
description: Recepción de muestras biológicas (sangre, orina, heces, esputo, citologías, biopsias) en laboratorio clínico con etiquetado robusto de tubos y contenedores siguiendo NOM-007-SSA3 (laboratorios clínicos) y NOM-087-ECOL-SSA1 (residuos biológico-infecciosos). Cada muestra recibe identificador único (código de barras) vinculado al paciente, médico solicitante, examen requerido (con clave SAT del procedimiento), fecha y hora exacta de recepción crítica para muestras con caducidad corta (hemograma 4-8 hrs, gasometría 30 min, cultivos inmediato), tipo de tubo y aditivo correcto (rojo sin anticoagulante para química, morado EDTA para hematología, gris fluoruro para glucosa), validación pre-analítica de calidad (hemólisis, lipemia, coágulos visibles que invalidan resultado), y cadena de custodia documentada cuando aplica (toxicológicos legales). Detecta automáticamente etiquetas duplicadas o pacientes confundidos. Usar cuando el usuario diga "recepcionar muestra", "registrar tubo lab", "etiquetar muestra", "ingresar paciente lab". NO usar para entrega de resultados (usar entrega-resultados) ni para procesamiento del análisis.
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
3. **Sin hemólisis visible** (invalida química clínica)
4. **Sin coágulos en tubo con anticoagulante** (invalida hematología)
5. **Identificación legible** del tubo
6. **Ayuno cumplido** si requiere (glucosa, perfil lípidos)
7. **Tiempo desde toma** dentro de ventana de procesamiento

## Cadena de custodia (toxicológicos legales)

Para análisis con valor legal (laborales, divorcio, paternidad):
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
