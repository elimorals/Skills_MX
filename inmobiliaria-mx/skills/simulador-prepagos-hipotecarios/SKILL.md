---
name: simulador-prepagos-hipotecarios
description: Simula el impacto de pre-pagos a un crédito hipotecario (INFONAVIT, FOVISSSTE, bancario): ahorro de intereses futuros, reducción de plazo vs reducción de pago mensual (la primera ahorra más intereses, la segunda da liquidez), tabla original vs simulada, momento óptimo del pre-pago (rinde más en los primeros años, cuando el interés sobre saldo insoluto pesa más) y revisión de comisiones por pago anticipado en el contrato. Cubre créditos en UDIs o en veces salario mínimo. Usar cuando el usuario diga "prepagar hipoteca", "abonar a capital", "ahorro intereses hipoteca", "amortización crédito", "INFONAVIT prepago", "reducir plazo hipoteca". NO usar para refinanciamiento total (usar comparador-subrogaciones-bancarias) ni para liquidación a fin de plazo.
allowed-tools: Read, Write, Edit
---

# Simulador de pre-pagos hipotecarios

## Inputs requeridos

```yaml
credito:
  tipo: bancario|INFONAVIT|FOVISSSTE
  monto_original: 1500000
  fecha_inicio: 2020-03-01
  plazo_meses: 240
  tasa_anual_pct: 10.5
  pagos_realizados: 56
  saldo_actual: 1366994.88   # tómalo del estado de cuenta, no lo estimes
  pago_mensual: 14975.70
  esquema: tradicional|UDIs|veces_salario_minimo
prepago_propuesto:
  monto: 100000
  modalidad: reduccion_plazo|reduccion_pago_mensual
```

Pago mensual = P × i / (1 − (1 + i)^−n), con i = tasa/12. Para $1,500,000 a 10.5% y 240 meses: **$14,975.70**. Saldo tras 56 pagos: **$1,366,994.88**; quedan 184 pagos.

## Cálculo del ahorro (amortización francesa, mes a mes)

```python
def amortizar(saldo, tasa_anual_pct, pago):
    i, meses, intereses = tasa_anual_pct / 1200, 0, 0.0
    while saldo > 0.005:
        interes = saldo * i
        intereses += interes
        saldo -= min(saldo, pago - interes)
        meses += 1
    return meses, intereses

# Original:  amortizar(1_366_994.88, 10.5, 14_975.70) -> 184 meses, $1,388,533.17 de intereses
# Modalidad A: amortizar(1_266_994.88, 10.5, 14_975.70) -> 155 meses, $1,050,467.13
```

## Comparativa (ejemplo, prepago de $100,000 en el mes 57)

```
ORIGINAL                         MODALIDAD A (reduce plazo)
Saldo:        $1,366,994.88      Saldo:        $1,266,994.88
Plazo:        184 meses          Plazo:        155 meses (−29)
Pago mensual: $14,975.70         Pago mensual: $14,975.70 (igual)
Intereses:    $1,388,533.17      Intereses:    $1,050,467.13
                                 AHORRO:       $338,066.05

MODALIDAD B (reduce pago)
Plazo:        184 meses (igual)
Pago mensual: $13,880.18 (−$1,095.52)
Intereses:    $1,286,957.62
AHORRO:       $101,575.55
```

## Mejor momento del pre-pago

En amortización francesa la parte de capital crece con el tiempo. Ejemplo $1.5M, 10.5%, 20 años:

| Año | Capital en el primer pago del año | Interés |
|---|---|---|
| 1 | 12% | 88% |
| 5 | 19% | 81% |
| 10 | 32% | 68% |
| 15 | 53% | 47% |

Conclusión: pre-pagar en los primeros años maximiza el ahorro.

## Comisiones por pago anticipado

No asumas una cifra por banco. Revisa la carátula y el contrato del crédito, y el Registro de Comisiones (RECO) de CONDUSEF. INFONAVIT y FOVISSSTE permiten pagos anticipados sin penalización (confianza media; confirmar en el portal del instituto). **Si hay comisión**, réstala del ahorro.

## Créditos en UDIs o en veces salario mínimo

El saldo se actualiza con el valor de la UDI (Banxico) o del salario mínimo; simula en esa unidad y convierte a pesos con el valor vigente. El ahorro en pesos depende de la inflación futura: preséntalo como estimación.

## Validación pendiente

⚠ Ejemplo recalculado 2026-10-15 con la fórmula de arriba; usa siempre el saldo y la tasa de tu estado de cuenta.
⚠ Para créditos en UDIs: aplicar factor INPC actualizado.
