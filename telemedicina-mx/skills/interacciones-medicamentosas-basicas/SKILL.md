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
        "accion": "Revisar función renal; suspender al momento del estudio y 48 h después si TFG < 30 o lesión renal aguda (criterio ACR; confianza media)",
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
    # ... ampliar con una fuente profesional; esta lista es solo ilustrativa
}

# Las claves pueden ser fármaco o clase: mapear cada fármaco a sus clases.
CLASES = {
    "sertralina": {"ssri"}, "fluoxetina": {"ssri"}, "escitalopram": {"ssri"},
    "alprazolam": {"benzodiacepina"}, "clonazepam": {"benzodiacepina"}, "diazepam": {"benzodiacepina"},
    "tramadol": {"opioide"}, "morfina": {"opioide"}, "oxicodona": {"opioide"},
}
# Índice sin orden: (A, B) y (B, A) son la misma interacción.
INDICE = {frozenset(k): v for k, v in INTERACCIONES_CONOCIDAS.items()}
```

## Algoritmo

```python
def _nombres(med: str) -> set[str]:
    m = med.strip().lower()
    return {m} | CLASES.get(m, set())

def validar_interacciones(nuevo_med: str, medicamentos_actuales: list[str]) -> dict:
    alertas = []
    for med in medicamentos_actuales:
        pares = {frozenset((a, b)) for a in _nombres(nuevo_med) for b in _nombres(med) if a != b}
        for key in pares & INDICE.keys():
            interaccion = INDICE[key]
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
