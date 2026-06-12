---
name: calculadora-isr-anual
description: Calcula el ISR anual para una persona física en México aplicando la tarifa progresiva del Art. 96 LISR (vigente del ejercicio fiscal correspondiente) sobre la base gravable resultante de restar gastos acumulables y deducciones personales a los ingresos acumulables del año. Soporta los 3 regímenes PFAE (612), RESICO PF (626) con su escala simplificada, y asalariado + honorarios (605+612 mixto). Compara contra pagos provisionales acumulados y retenciones del año para determinar saldo a pagar o saldo a favor. Usar cuando el usuario pida calcula mi ISR anual, cuanto pago de ISR este año, dame el cálculo final, simulador anual ISR. NO usar para pago provisional mensual (eso es cierre-fiscal-mensual del core).
allowed-tools: Read, Write
---

# Calculadora ISR anual — PF México

## Trigger

- "calcula mi ISR anual"
- "¿cuánto pago / cuánto me devuelven?"
- "dame el cálculo final del año"
- "simula mi declaración"

## Inputs requeridos

Idealmente vienen de skills previos del workflow:

- `regimen` ∈ {PFAE_612, RESICO_PF_626, ASALARIADO_HONORARIOS_605}
- `ejercicio` (int, ej. 2025)
- `ingresos_acumulables_mxn` (de `recopilar-cfdis-anuales`)
- `deducciones_acumulables_mxn` (gastos de actividad empresarial)
- `deducciones_personales_aplicables_mxn` (de `identificar-deducciones-personales`)
- `pagos_provisionales_acumulados_mxn` (del tracker `cierre-fiscal-mensual`)
- `isr_retenido_acumulado_mxn` (de CFDIs tipo I con retención)

## Algoritmo por régimen

### A. PFAE — Régimen 612

Base flujo: cuenta ingresos cobrados y gastos pagados.

```
Utilidad fiscal = ingresos_acumulables - deducciones_acumulables - deducciones_personales_aplicables
ISR anual = aplicar tarifa Art. 96 LISR a utilidad_fiscal
```

**Tarifa Art. 96 LISR (mensual) — convertida a anual multiplicando × 12**

Ver `references/tarifa-art-96-anual-2025.json` (cuando esté disponible). Estructura:

```json
[
  {"limite_inferior": 0,         "limite_superior": 8952.49,    "cuota_fija": 0,       "tasa_excedente": 0.0192},
  {"limite_inferior": 8952.50,   "limite_superior": 75984.55,   "cuota_fija": 171.88,  "tasa_excedente": 0.0640},
  ...
]
```

⚠ Estos números son ejemplo. La tarifa **vigente del ejercicio** debe consultarse en la RMF.

### B. RESICO PF — Régimen 626

Base flujo + escala simplificada (NO aplica tarifa Art. 96).

**Escala mensual RESICO PF (sumar acumulados de los 12 meses)**:

| Rango ingresos cobrados/año | Tasa |
|---|---|
| Hasta $300,000 | 1.00% |
| $300,001 a $600,000 | 1.10% |
| $600,001 a $1,000,000 | 1.50% |
| $1,000,001 a $2,500,000 | 2.00% |
| $2,500,001 a $3,500,000 | 2.50% |

```
Si ingresos_año_cobrados > 3,500,000 MXN → ya no aplica RESICO, recalcular como PFAE
ISR anual = ingresos_año_cobrados × tasa_aplicable
- En RESICO NO se restan deducciones acumulables (régimen simplificado)
- En RESICO PF SÍ se permiten deducciones personales desde 2023
```

### C. Asalariado + honorarios (605 + 612)

Combinar ambos:
- Cap. I (Salarios): tarifa Art. 96 sobre ingresos por salarios - prestaciones exentas
- Cap. II (Actividad empresarial / profesional): tarifa Art. 96 sobre utilidad fiscal de honorarios

Sumar ambas bases, aplicar tarifa una vez al total acumulado.

## Cálculo de saldo

```
ISR causado anual
- Pagos provisionales acumulados (Cap II)
- Retenciones de ISR (banco, clientes que retuvieron, salarios)
= Diferencia
```

- Si diferencia > 0: **saldo a pagar**
- Si diferencia < 0: **saldo a favor** (puede solicitarse devolución vía DeclaraSAT)

## Output

```json
{
  "ejercicio": 2025,
  "rfc_hash": "...",
  "regimen": "PFAE_612",
  "ingresos_acumulables_mxn": "1500000.00",
  "deducciones_acumulables_mxn": "250000.00",
  "deducciones_personales_mxn": "60000.00",
  "tope_aplicado": "5_UMAs_anuales",
  "utilidad_fiscal_mxn": "1190000.00",
  "tarifa_aplicada": "Art_96_LISR_2025_anualizada",
  "isr_anual_causado_mxn": "238250.00",
  "pagos_provisionales_acumulados_mxn": "215000.00",
  "isr_retenido_acumulado_mxn": "12500.00",
  "diferencia_mxn": "10750.00",
  "resultado": "SALDO_A_PAGAR",
  "linea_captura_estimada": null,
  "fecha_limite_presentacion": "2026-04-30",
  "advertencias": [
    "Tarifa Art. 96 2025 debe confirmarse con RMF vigente",
    "Si solicita devolución > $50,000 SAT puede pedir auditoría"
  ],
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| RESICO PF que cruzó $3.5M mid-año | Recalcular como PFAE desde mes de salida |
| Asalariado con 2 patrones | Sumar ingresos de ambos, retención total |
| Saldo a favor > $100,000 | Alerta crítica — alto riesgo de auditoría |
| Ingresos en USD | Convertir a MXN con TC promedio o TC del día (criterio FIFO) |
| Pérdida fiscal del año (utilidad negativa) | Acumular como pérdida fiscal años subsecuentes |
| Año con cambio de régimen mid-año | Calcular cada periodo por separado y sumar |

## Dependencias

- `mp_banxico` — UMA + INPC vigente
- Output de `recopilar-cfdis-anuales` + `identificar-deducciones-personales`
- Tracker local de pagos provisionales (del `core-mexico/cierre-fiscal-mensual`)

## ⚠ Compliance crítico

- Tarifa Art. 96 cambia cada enero — validar
- Escala RESICO PF puede cambiar en RMF — validar
- `vigencia_validada: false` SIEMPRE
- **NUNCA presentar sin revisión de contador certificado**
