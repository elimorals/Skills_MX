---
name: screening-inquilinos
description: Proceso completo de screening de inquilinos potenciales — verificación de ingresos (3x renta mensual mínimo), Buró de Crédito (con autorización del candidato), referencias profesionales y personales, estabilidad laboral, antecedentes (no penales), motivo de la mudanza. Genera score 1-10 y recomendación (aprobar/rechazar/condicional). Usar cuando el usuario diga screening inquilino, verificar candidato, requisitos renta, antecedentes inquilino, capacidad de pago. NO usar para contrato (otro skill) ni para inmueble (ficha-inmueble).
allowed-tools: Read, Write, Edit
---

# Screening de inquilinos

Un mal inquilino = pesadilla de meses con desalojo difícil. Screening profundo previene 90% de problemas.

## Documentos a solicitar

### Indispensables
1. **Identificación oficial** (INE/IFE, pasaporte, FM2/FM3 si extranjero)
2. **Comprobante de ingresos** (3 últimos):
   - Empleado: recibos de nómina o CFDIs nómina
   - PFAE: CFDIs honorarios + declaración SAT del año anterior
   - PM: estados financieros + declaración SAT del año anterior
3. **Comprobante de domicilio actual** (recibo luz/agua menor a 3 meses)
4. **Acta de nacimiento** (o equivalente migrante)
5. **CURP**

### Si tiene fiador
6. **Identificación del fiador**
7. **Comprobante de propiedad del fiador** (escritura, predial)
8. **Comprobante de ingresos del fiador** (debe ganar 5x la renta)

### Opcional (recomendado)
9. **Carta laboral firmada** con antigüedad
10. **Cartas de referencia** (mínimo 2: 1 personal + 1 profesional)
11. **Reporte de Buró de Crédito** (con autorización del candidato)
12. **Constancia de NO antecedentes penales** (para arrendamientos grandes)

## Verificación de ingresos

### Regla del 3x mensual
**Ingresos mensuales netos ≥ 3 × renta mensual**

Ejemplo: renta $18,500
- Ingresos mínimos: $55,500/mes
- Si gana $40k: requiere fiador con ingresos $92,500+

### Verificación

| Fuente | Verificación |
|---|---|
| Recibos nómina | 3 últimos meses sin interrupciones |
| Empresa empleadora | Llamada a RRHH para confirmar antigüedad |
| Banco | Estados de cuenta últimos 3 meses (depósitos coherentes) |
| CFDIs (PFAE) | Sumar últimos 12 meses, dividir por 12 |
| Negocio propio | Estados financieros + declaraciones SAT |

## Verificación de antigüedad laboral

- **Empleado**: mínimo 6 meses en mismo trabajo
- **PFAE**: actividad documentada > 1 año
- **PM**: empresa con > 2 años de operación

Antigüedad menor = mayor riesgo de cambio + impago.

## Buró de Crédito

Solicitar **con autorización formal por escrito** del candidato:

⚠ Consultar Buró sin autorización es DELITO (Art. 32 LFPDPPP). Ver `mp_buro_credito_personal`.

### Criterios de aceptación
- Score > 650 (bueno o excelente)
- Sin créditos en mora actual
- Sin sentencias firmes activas
- Sin EFOS (Art. 69-B SAT)

### Banderas rojas
- Score < 550 → rechazar o pedir fiador fuerte
- 3+ créditos en mora últimos 12 meses → rechazar
- Sentencia firme reciente → rechazar
- Antecedentes de evicción de departamento anterior → rechazar

## Referencias

### Personales (2 mínimo)
- Familia / amigos cercanos
- Verificar identidad por llamada
- Preguntar: "¿es buena paga? ¿llamadas constantes a cobrar?"
- ⚠ No tomar familiares más cercanos como única ref (sesgo positivo)

### Profesionales (2 mínimo)
- Jefe o supervisor actual
- Colega o cliente directo
- Verificar empleo actual + carácter profesional

### Arrendadores previos
- ¡SUPER IMPORTANTE!
- Llamar al arrendador anterior
- Preguntar:
  - ¿Pagó puntual? ¿meses tarde?
  - ¿Dejó el inmueble en buen estado?
  - ¿Tuvo problemas con vecinos?
  - ¿Lo volverías a rentar?

⚠ Si el candidato evade dar referencia del arrendador anterior → bandera roja FUERTE.

## Análisis del motivo de mudanza

Pregunta directa: "¿Por qué se está mudando?"

| Motivo | Indicador |
|---|---|
| Nuevo trabajo | Verificable, OK |
| Familia (matrimonio, divorcio) | Verificable, OK |
| Cambio de ciudad por estudios | Verificable, OK |
| "El dueño anterior subió mucho la renta" | OK pero verificar |
| "Tuvimos problemas con el dueño anterior" | 🚩 Profundizar |
| "No nos podíamos pagar la renta anterior" | 🚩 Bandera roja seria |
| "El edificio nos pedía firma de nuevo contrato" | Investigar |

## Sistema de scoring

Score 1-10 con pesos:

| Factor | Peso |
|---|---|
| Ingresos 3x verificados | 25% |
| Buró de Crédito > 650 | 20% |
| Antigüedad laboral > 1 año | 15% |
| Referencia arrendador anterior | 15% |
| Referencias profesionales | 10% |
| Documentos completos | 10% |
| Estabilidad de domicilio (años en anterior) | 5% |

### Decisión
- **Score 8-10**: APROBAR
- **Score 6-7**: APROBAR con fiador fuerte o depósito 2 meses
- **Score 4-5**: RECHAZAR con explicación amable
- **Score < 4**: RECHAZAR rápido

## Output estructurado

```json
{
  "screening_candidato": {
    "candidato": "Ana Martínez",
    "rfc_hash": "abc123",
    "fecha_evaluacion": "2026-03-15",
    "factores": {
      "ingresos_3x": {
        "verificado": true,
        "ingreso_mensual_mxn": 60000,
        "renta_evaluada_mxn": 18500,
        "ratio_ingreso_renta": 3.24,
        "score": 9
      },
      "buro_credito": {
        "consultado_con_autorizacion": true,
        "score": 712,
        "categoria": "bueno",
        "score_skill": 8
      },
      "antiguedad_laboral_meses": 24,
      "antiguedad_laboral_score": 9,
      "referencia_arrendador_anterior": {
        "verificable": true,
        "calificacion_anterior": 9.0,
        "score_skill": 10
      },
      "referencias_profesionales": {
        "count_obtenidas": 3,
        "calidad_promedio": 8.5,
        "score": 9
      },
      "documentos_completos": true,
      "documentos_score": 10,
      "estabilidad_domicilio_anios": 4,
      "estabilidad_score": 8
    },
    "score_total": 8.6,
    "decision_recomendada": "APROBAR",
    "condiciones_sugeridas": [],
    "alertas": [],
    "siguientes_pasos": [
      "Enviar contrato para revisión",
      "Programar firma + entrega de inmueble"
    ]
  }
}
```

## Validación pendiente

- Compliance LFPDPPP en uso de Buró
- Casos típicos de evicción en CDMX y cómo prevenir
- Mejores referencias para verificar candidato
- Software de tracking (Sumaprop, Apolo, etc.)

## Ver también

- `mp_buro_credito_personal` para consulta Buró
- `contrato-arrendamiento-mx` para formalizar
- `compliance-lfpdppp` para tratamiento datos
