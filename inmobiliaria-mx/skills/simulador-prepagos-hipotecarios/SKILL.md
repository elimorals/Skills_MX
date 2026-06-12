---
name: simulador-prepagos-hipotecarios
description: Simula impacto de pre-pagos a crédito hipotecario (INFONAVIT, FOVISSSTE, bancarios) mostrando ahorro real en intereses futuros (un pre-pago de $100k MXN puede ahorrar $400k-1.5M MXN en intereses según plazo y tasa), reducción de plazo vs reducción de pago mensual (la primera ahorra más intereses, la segunda da liquidez mensual), tabla de amortización original vs simulada con visualización clara del antes/después, comparativa de momento óptimo del pre-pago (más rentable en primeros años cuando el interés sobre saldo insoluto es mayor), y advertencia sobre comisiones por pre-pago anticipado que algunos bancos cobran (típicamente 1-3% del monto pre-pagado los primeros 3 años — INFONAVIT y FOVISSSTE generalmente sin comisión). Cubre fórmula UDIs para créditos hipotecarios denominados en UDIs (factor de actualización por INPC). Usar cuando el usuario diga "prepagar hipoteca", "abonar a capital", "ahorro intereses hipoteca", "amortización crédito", "INFONAVIT prepago", "reducir plazo hipoteca". NO usar para refinanciamiento total (usar comparador-subrogaciones-bancarias) ni para liquidación a fin de plazo.
allowed-tools: Read, Write, Edit
---

# Simulador de pre-pagos hipotecarios

## Inputs requeridos

```yaml
credito:
  tipo: bancario|INFONAVIT|FOVISSSTE
  banco: ...
  monto_original: 1500000
  fecha_inicio: 2020-03-01
  plazo_meses: 240
  tasa_anual_pct: 10.5
  pagos_realizados: 56
  saldo_actual: 1380000  # aprox 92% si tasa alta y pocos años
  pago_mensual: 14580
  esquema: tradicional|UDIs|fija_inflacion
prepago_propuesto:
  monto: 100000
  modalidad: reduccion_plazo|reduccion_pago_mensual
fecha_prepago: 2026-07-15
```

## Cálculo del ahorro

### Modalidad A: Reducción de plazo (recomendada para ahorrar)

```
saldo_nuevo = saldo_actual - prepago = 1,380,000 - 100,000 = 1,280,000
pago_mensual: igual ($14,580)
plazo_nuevo: se calcula con fórmula amortización francesa hasta agotar saldo
ahorro_intereses_futuros: (pagos_originales_restantes - pagos_nuevos) * pago_mensual - (saldo_nuevo)
```

### Modalidad B: Reducción de pago mensual (más liquidez)

```
saldo_nuevo: 1,280,000
plazo_restante_original: 184 meses
pago_mensual_nuevo: amortización de 1,280,000 en 184 meses a 10.5%
ahorro_mensual: pago_original - pago_nuevo
ahorro_total_intereses_futuros: menor que modalidad A
```

## Comparativa visual

```
ORIGINAL                       CON PRE-PAGO MODALIDAD A
Saldo:        $1,380,000       Saldo:        $1,280,000
Plazo:        184 meses        Plazo:        163 meses (-21)
Pago mensual: $14,580          Pago mensual: $14,580 (igual)
Total a pagar: $2,682,720      Total a pagar: $2,376,540
Intereses:    $1,302,720       Intereses:    $1,096,540 (-$206k)
                                AHORRO NETO:  $206,180

vs MODALIDAD B
Saldo:        $1,280,000
Plazo:        184 meses (igual)
Pago mensual: $13,524 (-$1,056)
Total a pagar: $2,488,416
Intereses:    $1,208,416 (-$94k)
AHORRO NETO:  $94,304
```

## Mejor momento del pre-pago

Para amortización francesa: **más rentable al inicio del crédito** porque el interés sobre saldo insoluto es mayor.

| Año | Capital amortizado por pago | Interés |
|---|---|---|
| Año 1 | ~10% del pago | 90% |
| Año 5 | ~25% | 75% |
| Año 10 | ~50% | 50% |
| Año 15 | ~75% | 25% |

Conclusión: si tienes el dinero, pre-pagar en años 1-7 maximiza ahorro.

## Comisiones por pre-pago (validar con tu banco)

| Banco | Comisión típica | Plazo |
|---|---|---|
| INFONAVIT | $0 | Sin comisión |
| FOVISSSTE | $0 | Sin comisión |
| BBVA | 1% del monto | Primeros 3 años |
| Banamex | Variable | Revisar contrato |
| Santander | 1-2% | Primeros 5 años |

**SI hay comisión**: ajustar cálculo restándola del ahorro.

## Validación pendiente

⚠ Fórmulas verificadas — confirmar tasas vigentes con tu banco.
⚠ Para créditos en UDIs: aplicar factor INPC actualizado.
