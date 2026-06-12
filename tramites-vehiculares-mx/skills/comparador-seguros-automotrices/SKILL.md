---
name: comparador-seguros-automotrices
description: Compara cotizaciones de seguro vehicular entre las 5 principales aseguradoras de México (GNP, Qualitas, AXA, HDI, MAPFRE) considerando cobertura amplia vs limitada, deducible, suma asegurada, asistencias, y precio. Sugiere mejor relación cobertura/precio según perfil del usuario. Usar cuando el usuario diga comparar seguros auto, cuál seguro comprar, mejor seguro vehicular, cotizar seguro carro.
allowed-tools: Read, Write
---

# Comparador seguros automotrices

## Cobertura típica

| Tipo | Qué cubre | Costo relativo |
|---|---|---|
| Responsabilidad Civil (RC) | Solo daños a terceros (obligatorio) | $$ |
| Limitado | RC + Robo total | $$$ |
| Amplio | RC + Robo + Daños materiales propios | $$$$ |
| Plus / Premium | Amplio + Asistencias adicionales | $$$$$ |

## Aseguradoras principales MX

| Aseguradora | Pros | Cons |
|---|---|---|
| GNP | Servicio rápido, buena reputación | Cara |
| Qualitas | Líder mercado, talleres extensa red | Trámite siniestros lento |
| AXA | Tarifas competitivas, app moderna | Asistencia variable |
| HDI | Buen costo, talleres oficiales | Cobertura limitada en ciertos modelos |
| MAPFRE | Multinacional, descuentos por antigüedad | Pago siniestro lento |

## Inputs

```json
{
  "vehiculo": {
    "marca": "Honda",
    "modelo": "Civic",
    "anio": 2020,
    "valor_factura_mxn": "450000",
    "uso": "particular"
  },
  "conductor": {
    "edad": 35,
    "antiguedad_licencia_anos": 15,
    "historial_siniestros": 0
  },
  "cobertura_deseada": "amplio",
  "cotizaciones_recibidas": [
    {"aseguradora": "Qualitas", "prima_anual_mxn": "11500", "deducible_robo_pct": 5},
    {"aseguradora": "AXA", "prima_anual_mxn": "10800", "deducible_robo_pct": 5},
    {"aseguradora": "GNP", "prima_anual_mxn": "13200", "deducible_robo_pct": 3}
  ]
}
```

## Output

```json
{
  "vehiculo": "Honda Civic 2020",
  "cobertura_solicitada": "amplio",
  "comparativa": [
    {
      "aseguradora": "AXA",
      "prima_anual_mxn": "10800",
      "prima_mensual_mxn": "900",
      "deducible_robo_total_mxn": "22500",
      "asistencias_incluidas": ["grúa", "vehículo sustituto 24h"],
      "score": 8.2,
      "pros": ["Más barato", "App moderna"],
      "cons": ["Asistencia variable"],
      "ranking": 1
    },
    {
      "aseguradora": "Qualitas",
      "prima_anual_mxn": "11500",
      "score": 7.8,
      "ranking": 2
    },
    {
      "aseguradora": "GNP",
      "prima_anual_mxn": "13200",
      "score": 7.5,
      "ranking": 3,
      "pros": ["Servicio premium"],
      "cons": ["Más cara $2.4k vs mejor opción"]
    }
  ],
  "recomendacion": "AXA",
  "ahorro_vs_mas_cara_anual_mxn": "2400.00",
  "advertencias": [
    "Confirmar suma asegurada coincide con valor factura",
    "Pedir desglose de coberturas — limitado vs amplio",
    "Verificar red de talleres autorizados cerca del domicilio"
  ],
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Conductor < 25 años | Prima 30-50% más alta |
| Vehículo > 10 años | Algunos aseguradoras no cubren amplio |
| Robo previo | Algunas aseguradoras rechazan |
| Uso comercial (Uber, repartos) | Cobertura específica más cara |
| Vehículo eléctrico | Cobertura especializada (Tesla, etc.) |

## ⚠ Compliance

- Primas cambian frecuentemente
- `vigencia_validada: false`
- Confirmar póliza incluye RC obligatoria mínima legal por estado
