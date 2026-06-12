---
name: interacciones-medicamentosas-basicas
description: Validación básica de interacciones medicamentosas antes de prescribir. Cruza el medicamento nuevo a recetar contra los medicamentos crónicos del paciente registrados en su expediente, y alerta si hay interacciones documentadas (mayor, moderada, menor). NO sustituye juicio clínico ni catálogo Vademécum profesional — es triage de primer nivel. Usar cuando el usuario diga interacciones medicamentos, antes de recetar, validar farmaco.
allowed-tools: Read, Write
---

# Interacciones medicamentosas básicas

## Catálogo (subset Vademécum MX)

```python
INTERACCIONES_CONOCIDAS = {
    # (medicamento_A, medicamento_B): {severidad, descripcion, accion}
    ("warfarina", "aspirina"): {
        "severidad": "mayor",
        "descripcion": "Riesgo de sangrado aumentado significativamente",
        "accion": "Evitar combinación o monitoreo INR estricto",
    },
    ("losartan", "potasio"): {
        "severidad": "moderada",
        "descripcion": "Hiperkalemia potencial",
        "accion": "Monitorear electrolitos",
    },
    ("metformina", "yodo_contraste"): {
        "severidad": "mayor",
        "descripcion": "Riesgo acidosis láctica si insuficiencia renal",
        "accion": "Suspender metformina 48h antes/después de contraste",
    },
    ("ssri", "tramadol"): {
        "severidad": "mayor",
        "descripcion": "Riesgo síndrome serotoninérgico",
        "accion": "Evitar combinación",
    },
    ("benzodiacepina", "opioide"): {
        "severidad": "mayor",
        "descripcion": "Depresión respiratoria, riesgo muerte",
        "accion": "EVITAR combinación. FDA black box warning.",
    },
    # ... ~200 interacciones más
}
```

## Algoritmo

```python
def validar_interacciones(nuevo_med: str, medicamentos_actuales: list[str]) -> dict:
    alertas = []
    for med in medicamentos_actuales:
        key = tuple(sorted([nuevo_med.lower(), med.lower()]))
        if key in INTERACCIONES_CONOCIDAS:
            interaccion = INTERACCIONES_CONOCIDAS[key]
            alertas.append({
                "medicamentos": [nuevo_med, med],
                "severidad": interaccion["severidad"],
                "descripcion": interaccion["descripcion"],
                "accion_sugerida": interaccion["accion"],
            })
    return {
        "interacciones_encontradas": len(alertas),
        "tiene_severidad_mayor": any(a["severidad"] == "mayor" for a in alertas),
        "alertas": alertas,
        "permite_prescribir": not any(a["severidad"] == "mayor" for a in alertas),
        "disclaimer": "Validación básica — consultar Vademécum profesional siempre"
    }
```

## Output

```json
{
  "medicamento_nuevo": "aspirina",
  "medicamentos_paciente": ["warfarina", "losartan", "metformina"],
  "interacciones_encontradas": 1,
  "tiene_severidad_mayor": true,
  "alertas": [
    {
      "medicamentos": ["aspirina", "warfarina"],
      "severidad": "mayor",
      "descripcion": "Riesgo de sangrado aumentado",
      "accion_sugerida": "Evitar o INR estricto"
    }
  ],
  "permite_prescribir": false,
  "siguiente_paso": "Reconsiderar prescripción o documentar justificación clínica"
}
```

## ⚠ Disclaimer obligatorio

Este skill es **triage de primer nivel**. NO sustituye:
- Vademécum profesional (Drugs.com, Micromedex)
- Juicio clínico del médico
- Consulta con farmacéutico clínico en casos complejos
