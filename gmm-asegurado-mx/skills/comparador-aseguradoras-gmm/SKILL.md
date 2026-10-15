---
name: comparador-aseguradoras-gmm
description: Compara cotizaciones GMM de las aseguradoras que el usuario cotice (p. ej. GNP, AXA, MetLife, Seguros Monterrey New York Life, MAPFRE, Banorte, Allianz, BUPA). Ranquea por relación costo/cobertura considerando suma asegurada, deducible, coaseguro, red hospitales, exclusiones, beneficios extra (cobertura internacional, maternidad, dental). Usar cuando el usuario diga comparar gmm, mejor seguro medico, cotizar gmm.
allowed-tools: Read, Write
---

# Comparador aseguradoras GMM

## Factores comparados

| Factor | Importancia |
|---|---|
| Suma asegurada | Alta |
| Deducible | Media |
| Coaseguro % + tope | Media |
| Red hospitales | Alta (varía por ciudad) |
| Exclusiones (preexistentes) | Crítica |
| Beneficios extra | Variable |
| Antigüedad respetada | Alta si cambias |

## Fuentes para comparar

- Cotizaciones y **condiciones generales** de cada aseguradora (no solo el folleto).
- Registro de la aseguradora y de sus productos ante la **CNSF**.
- Índice de reclamaciones y sanciones en el **Buró de Entidades Financieras (CONDUSEF)**.

## Output ejemplo (cifras ficticias)

```json
{
  "edad_asegurado": 35,
  "ciudad": "CDMX",
  "tipo_plan": "premium",
  "comparativa": [
    {
      "aseguradora": "GNP",
      "prima_anual_mxn": "32500",
      "suma_asegurada_mxn": "5000000",
      "deducible_mxn": "30000",
      "coaseguro_pct": 0.10,
      "score_relativo": 8.5,
      "ranking": 1
    },
    {
      "aseguradora": "AXA",
      "prima_anual_mxn": "29000",
      "suma_asegurada_mxn": "4000000",
      "score_relativo": 8.2,
      "ranking": 2
    }
  ],
  "recomendacion": "GNP — mejor relación costo / red hospitales en CDMX"
}
```

## ⚠ Cambio aseguradora

Si cambias, por regla general pierdes antigüedad: periodos de espera y preexistencias vuelven a correr. Algunas aseguradoras ofrecen **reconocimiento de antigüedad** si no hay hueco de cobertura; pídelo por escrito (no es obligación legal). Solo conviene si:
- No tienes preexistentes
- Ahorro > $5,000/año
- Cobertura significativamente mejor

> La prima de GMM es deducible en la anual (Art. 151 fr. VI LISR, uso CFDI D07) para ti, cónyuge/concubino, ascendientes y descendientes en línea recta; sujeta al tope global de deducciones personales. Comparación orientativa: la decisión final requiere leer condiciones generales.
