---
name: comparador-seguros-automotrices
description: Compara cotizaciones de seguro vehicular que el usuario ya obtuvo de aseguradoras autorizadas en México (GNP, Quálitas, AXA, HDI, MAPFRE, Chubb u otras) considerando cobertura amplia vs limitada, deducible, suma asegurada, asistencias, y precio. Verifica que la aseguradora esté autorizada (CONDUSEF SIPRES) y sugiere la mejor relación cobertura/precio según el perfil. No cotiza por sí sola. Usar cuando el usuario diga comparar seguros auto, cuál seguro comprar, mejor seguro vehicular, cotizar seguro carro.
allowed-tools: Read, Write
---

# Comparador seguros automotrices

## Cobertura típica

| Tipo | Qué cubre | Costo relativo |
|---|---|---|
| Responsabilidad Civil (RC) | Solo daños a terceros (obligatoria para circular en caminos federales y en varias entidades) | $$ |
| Limitado | RC + Robo total | $$$ |
| Amplio | RC + Robo + Daños materiales propios | $$$$ |
| Plus / Premium | Amplio + Asistencias adicionales | $$$$$ |

## Aseguradoras principales MX

No uses opiniones genéricas de "pros/contras" por marca: no tienen fuente. Compara con datos verificables:

1. **Autorización**: `sipres_verificar_autorizada(nombre)` (`mp_condusef_sipres`, consulta real). Si no está autorizada, descártala.
2. **Quejas y sanciones**: Buró de Entidades Financieras de CONDUSEF (consulta manual en buro.gob.mx).
3. **Póliza**: suma asegurada (valor comercial vs valor factura), deducibles de daños y robo, límite de RC, gastos médicos a ocupantes, asistencias, red de talleres o agencia.
4. **Prima**: anual de contado; si es en mensualidades, incluir el recargo por pago fraccionado.

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
      "pros": ["Prima más baja"],
      "cons": ["Deducible de robo 5% vs 3% de GNP"],
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
      "pros": ["Deducible de robo 3% ($13,500)"],
      "cons": ["$2,400 más cara que la más barata"]
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
- Confirmar que la póliza cubre la RC obligatoria (caminos federales y reglamento de tránsito local)
- `prima_mensual_mxn` es prima anual / 12; un pago fraccionado real cuesta más (recargo)
- La recomendación es orientativa; no sustituye la asesoría de un agente con cédula CNSF
