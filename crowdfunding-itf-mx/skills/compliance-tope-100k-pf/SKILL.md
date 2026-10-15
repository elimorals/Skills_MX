---
name: compliance-tope-100k-pf
description: Valida los límites reales de inversión por inversionista en instituciones de financiamiento colectivo (IFC) según los Arts. 49 y 50 de las Disposiciones de la CNBV para ITF - porcentaje máximo por solicitud (7.5% PF en préstamos personales, 15% PF en empresariales/inmobiliarios/capital, 20% PM), excepciones para montos pequeños (2,000/8,300 UDIS) y exclusión para inversionistas relacionados o experimentados. Corrige el mito del "tope de $100k". Usar cuando el usuario diga compliance tope 100k pf, compliance_tope_100k_pf, cuánto puedo invertir en crowdfunding, límite de inversión IFC, inversionista experimentado, tope por proyecto, ayuda con compliance tope 100k pf.
allowed-tools: Read, Write
---

# Límites de inversión por inversionista en IFC

**No existe un tope legal de $100,000 por proyecto.** Los límites son porcentajes de la cartera del inversionista en la propia IFC.

Fuente primaria: Disposiciones de carácter general aplicables a las Instituciones de Tecnología Financiera (CNBV, DOF 10-09-2018, última modificación DOF 06-07-2026), Arts. 47-50; consultadas el 2026-10-15.

## Art. 49: porcentaje máximo por solicitud

| Operación | Inversionista PF | Inversionista PM |
|---|---|---|
| Deuda de préstamos personales entre personas | 7.5% | 20% |
| Deuda de préstamos empresariales o desarrollo inmobiliario | 15% | 20% |
| Capital, copropiedad o regalías | 15% | 20% |

Fórmula: NCI ÷ (IE + CI + NCI) ≤ porcentaje, donde NCI = nuevo compromiso en la solicitud, IE = inversiones efectivas vigentes en la IFC (saldo insoluto en deuda; monto invertido en capital), CI = compromisos previos en otras solicitudes. El texto publicado muestra la fórmula como imagen: el denominador "suma IE y CI" (Art. 49); la inclusión de NCI en el denominador es la lectura usual — confianza media, confírmala con la IFC.

## Art. 50: cuándo no aplican los porcentajes

1. Cartera total en la IFC ≤ **2,000 UDIS**: hasta **667 UDIS** por solicitud (deuda personal o empresarial).
2. Cartera total ≤ **8,300 UDIS**: hasta **4,150 UDIS** por solicitud (inmobiliario, capital, copropiedad o regalías).
3. Plataforma con 25 o menos solicitudes publicadas: máximo el mayor entre 5% del monto solicitado o 167,000 UDIS por inversionista y solicitante.
4. Si la IFC coinvierte (riesgo compartido): el % del Art. 49 sube en lo que invierta la IFC, máximo +25%.
5. **Inversionistas relacionados y experimentados**: sin límites (la IFC recaba el Anexo 9 y comprobantes).

Límites del solicitante (contexto): 50,000 UDIS en préstamos personales y 1,670,000 UDIS en las demás operaciones por IFC (hasta 6,700,000 con autorización), y 7,370,000 UDIS en total entre IFC (Arts. 47-48).

Convierte UDIS a pesos con el valor de la UDI del día que publica Banxico (el MCP `mp_banxico` no tiene tool de UDIS: pide el valor al usuario o consúltalo en banxico.org.mx).

## Algoritmo

```python
LIMITES = {("personal", "PF"): D("0.075"), ("personal", "PM"): D("0.20"),
           ("empresarial", "PF"): D("0.15"), ("empresarial", "PM"): D("0.20"),
           ("capital", "PF"): D("0.15"), ("capital", "PM"): D("0.20")}

def max_compromiso(tipo, persona, ie, ci):
    p = LIMITES[(tipo, persona)]
    return (p * (ie + ci) / (1 - p)).quantize(D("0.01"))   # despeje de NCI/(IE+CI+NCI) <= p
```

Ejemplo: PF con $200,000 invertidos en préstamos empresariales en la IFC (IE + CI) → NCI máx = 0.15 × 200,000 / 0.85 = **$35,294.12** por solicitud.

## Output esperado

```json
{
  "operation": "compliance-tope-100k-pf",
  "data": {
    "tipo_operacion": "empresarial",
    "tipo_inversionista": "PF",
    "cartera_en_ifc_mxn": "200000.00",
    "pct_limite": 0.15,
    "max_por_solicitud_mxn": "35294.12",
    "excepcion_aplicable": null,
    "fuente": "CUITF CNBV Arts. 49-50, DOF 06-07-2026"
  },
  "vigencia_validada": true
}
```

## Casos edge

- Inversionista que se declara experimentado sin acreditarlo: la IFC debe aplicar límites.
- Varias IFC: los límites se calculan por IFC.
- Datos incompletos → solicitar al usuario.

## Dependencias

- `core-mexico` (mxn-formato); MCP `mp_cnbv_fintech` para confirmar que la IFC está autorizada

No es asesoría de inversión: confirma con la IFC y un asesor.
