---
name: declaracion-anual-transparencia
description: Prepara las dos obligaciones anuales de una donataria autorizada - la declaración anual informativa de ingresos y egresos (a más tardar el 15 de febrero, Art. 86 LISR) y la declaración/informe de transparencia sobre patrimonio, uso y destino de donativos (en mayo, Art. 82 fr. VI LISR, programa "Transparencia de las Donatarias Autorizadas" del SAT). Usar cuando el usuario diga declaración anual transparencia, declaracion_anual_transparencia, informe de transparencia donataria, declaración informativa donataria, uso y destino de donativos, ayuda con declaración anual transparencia.
allowed-tools: Read, Write
---

# Declaración anual + transparencia (donatarias)

## Dos obligaciones distintas

| Obligación | Plazo | Fundamento | Contenido |
|---|---|---|---|
| Declaración anual informativa (Título III) | **15 de febrero** | Art. 86, penúltimo párrafo LISR | Ingresos obtenidos y erogaciones efectuadas del ejercicio anterior |
| Declaración de transparencia | **Mayo** (a más tardar el 31) | Art. 82 fr. VI LISR; RMF 2026 regla 3.10.1.12 (numeración según El Conta 2026; confianza media) | Patrimonio, donativos recibidos (dinero/especie), uso y destino, gastos de administración, operaciones con partes relacionadas y con donantes |

La de transparencia se presenta **aunque no haya habido ingresos ni erogaciones** (SAT, documento "Declaración de transparencia 2026"). Debe coincidir con la declaración anual, los CFDI y la contabilidad.

## Datos a reunir

1. Donativos recibidos: monto en dinero y en especie, nacionales y del extranjero, por tipo de donante.
2. Aplicación: monto destinado a actividades autorizadas, gastos de administración, otros.
3. Patrimonio al cierre.
4. Ingresos por actividades no relacionadas con el objeto (deben ser ≤ 10% de ingresos totales, Art. 80 LISR; el excedente paga ISR).
5. Gastos de administración (≤ 5% de los donativos, Art. 138 RLISR; verificar).
6. Operaciones con partes relacionadas y con donantes (Art. 82 fr. VIII LISR).
7. Número de beneficiarios y actividades realizadas (narrativa breve).

```python
def indicadores(ingresos_totales: D, ingresos_no_relacionados: D, donativos: D, gastos_admin: D) -> dict:
    return {
        "pct_no_relacionados": ingresos_no_relacionados / ingresos_totales,   # alerta si > 10%
        "pct_gastos_admin": gastos_admin / donativos,                          # alerta si > 5%
    }
```

## Output esperado

```json
{
  "operation": "declaracion-anual-transparencia",
  "data": {
    "ejercicio": 2025,
    "declaracion_informativa_deadline": "2026-02-16",
    "transparencia_deadline": "2026-05-31",
    "donativos_dinero_mxn": "0.00",
    "donativos_especie_mxn": "0.00",
    "pct_gastos_admin": null,
    "pct_no_relacionados": null,
    "alertas": []
  },
  "vigencia_validada": false
}
```

15-feb-2026 fue domingo: el plazo se recorrió al lunes 16. El 31-may-2026 también es domingo: presentar antes para no depender de prórrogas.

## Casos edge

- Donataria con donativos para reconstrucción por el huracán Otis (decreto DOF 30-10-2023): la regla de transparencia 2026 pide informar el saldo pendiente.
- Si no presenta transparencia, el SAT puede no renovar la autorización (Art. 82 fr. VI, segundo párrafo).
- Datos incompletos → solicitar al usuario. Modo mock por default si no hay credenciales.

## Dependencias

- `core-mexico` (CFDI, RFC, mxn-formato)
- Tracker local; contabilidad de la donataria

Valida con el contador de la donataria antes de presentar.
