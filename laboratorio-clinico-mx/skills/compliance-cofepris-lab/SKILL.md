---
name: compliance-cofepris-lab
description: Tracking de cumplimiento sanitario del laboratorio clínico conforme NOM-007-SSA3-2011 - aviso de funcionamiento y aviso de responsable sanitario (licencia sanitaria solo si usa rayos X o isótopos), requisitos del responsable sanitario, programa de control interno de calidad y participación en al menos un programa de evaluación externa (PEEC), bitácoras de equipos y temperatura, caducidad de reactivos, manejo de RPBI (NOM-087-SEMARNAT-SSA1-2002) y expediente documental listo para visita de verificación. Genera tablero de cumplimiento y alertas. Usar cuando el usuario diga compliance COFEPRIS lab, auditoría sanitaria, responsable sanitario, NOM-007, garantía de calidad lab, PEEC, aviso de funcionamiento laboratorio, licencia sanitaria laboratorio, RPBI. NO usar para compliance fiscal SAT ni para LFPDPPP.
allowed-tools: Read, Write, Edit
---

# Compliance sanitario del laboratorio clínico

> Orientación; validar con asesor regulatorio sanitario. NOM-007-SSA3-2011 (DOF 27-03-2012) sigue vigente según el catálogo de normas de la Secretaría de Economía (consultado 2026-10-15); hay exhortos legislativos para actualizarla.

## Trámites sanitarios

| Documento | Cuándo | Fundamento |
|---|---|---|
| **Aviso de funcionamiento** | Al menos 30 días antes de iniciar; actualizar si cambian razón social, domicilio o actividad | NOM-007 4.1; LGS Art. 200 Bis |
| **Aviso de responsable sanitario** | Al iniciar y cada vez que cambie | NOM-007 4.1 |
| **Licencia sanitaria** | Solo si usa fuentes de radiación ionizante (rayos X) o isótopos radiactivos, en lugar de los avisos | NOM-007 4.1; LGS Art. 198 fr. IV |

Las autorizaciones sanitarias se otorgan por tiempo indeterminado (LGS Art. 370): no hay "renovación cada 5 años" de la licencia del establecimiento.
MCP: `mp_cofepris_aviso_funcionamiento` → `cofepris_clasificar_giro("laboratorio_clinico")` y `cofepris_requisitos_aviso`. `cofepris_consultar_aviso` no tiene consulta pública: devuelve `requiere_humano` con URL y pasos para el usuario.

## Responsable sanitario (NOM-007 4.3)

- Químico con currículum orientado a laboratorio clínico y mínimo 3 años de experiencia comprobable en el área técnica, o con especialidad, maestría o doctorado en laboratorio clínico (4.3.1); o
- Médico cirujano con especialidad en patología clínica, maestría o doctorado en el área (4.3.2)
- Firma los reportes o vigila que los firme personal autorizado, de forma autógrafa, digitalizada o electrónica (5.1.8)

La cédula profesional no "vence"; lo que hay que vigilar es que el aviso de responsable esté actualizado.

## Aseguramiento de la calidad (NOM-007 cap. 7)

- **7.1** Programa de control interno de calidad para todos los estudios, en las etapas preanalítica, analítica y postanalítica
- **7.2** Participar **al menos en un programa de evaluación externa** de la calidad que incluya los estudios que realiza. La frecuencia la fija el programa (no es "trimestral" por norma)

### Control interno diario (ejemplo)

```yaml
fecha: 2026-10-15
analizador: Cobas 6000
controles_corridos:
  - nivel: Nivel 1 (normal)
    analito: glucosa
    valor_obtenido: 95
    media_esperada: 92
    de: 4
    desviacion_en_de: 0.75     # (95-92)/4 → dentro de ±2 DE
    aceptable: true
  - nivel: Nivel 2 (alto)
    analito: glucosa
    valor_obtenido: 285
    media_esperada: 280
    aceptable: true
firma: Responsable sanitario
```

Las reglas de aceptación (±2 DE, Westgard) las define el programa de calidad del laboratorio.

## Otros registros

- Registro cronológico de estudios: fecha, usuario, estudios, resultados con nombre y firma de quien los realizó (NOM-007 4.7)
- Bitácoras de mantenimiento y calibración de equipos
- Temperatura de refrigeradores de reactivos/muestras (rango según el inserto del reactivo; típico 2-8 °C)
- Caducidad de reactivos (reactivo vencido = resultado inválido)

## RPBI (NOM-087-SEMARNAT-SSA1-2002, citada en NOM-007 2.5)

| Residuo | Envase (confianza media; verificar tabla de envasado en la NOM y su última modificación) |
|---|---|
| Punzocortantes | Recipiente rígido de polipropileno rojo |
| Sangre y no anatómicos sólidos | Bolsa de polietileno roja |
| Sangre y líquidos | Recipiente hermético rojo |
| Cultivos y cepas | Bolsa roja (inactivar según el plan de manejo) |
| Patológicos (tejidos) | Bolsa amarilla; refrigerados hasta su recolección |

- Recolección, transporte y disposición por empresa autorizada (SEMARNAT)
- Manifiestos de entrega-transporte-recepción: conservarlos (plazo: **verificar** en la NOM-087)

## Alertas automáticas

- Cambio de responsable sanitario → presentar nuevo aviso
- Calendario del PEEC contratado: recordar envíos y revisar resultados
- Diaria: bitácora de temperatura fuera de rango
- Mensual: reactivos que vencen
- Contrato RPBI: 60 días antes de vencer (política interna)

## Validación pendiente

- Tabla de envasado RPBI y plazo de conservación de manifiestos: cotejar con el DOF.
- Requisitos estatales adicionales (algunos estados tramitan avisos en su comisión estatal).
