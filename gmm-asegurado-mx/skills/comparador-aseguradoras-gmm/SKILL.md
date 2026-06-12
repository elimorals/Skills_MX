---
name: comparador-aseguradoras-gmm
description: Compara cotizaciones GMM entre las 5 principales aseguradoras (GNP, AXA, MetLife, MAPFRE, Banorte). Ranquea por relación costo/cobertura considerando suma asegurada, deducible, coaseguro, red hospitales, exclusiones, beneficios extra (cobertura internacional, maternidad, dental). Usar cuando el usuario diga comparar gmm, mejor seguro medico, cotizar gmm.
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

## Output ejemplo

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

Si cambias: pierdes antigüedad (excluyentes pueden volver a aplicar). Solo conviene si:
- No tienes preexistentes
- Ahorro > $5,000/año
- Cobertura significativamente mejor
