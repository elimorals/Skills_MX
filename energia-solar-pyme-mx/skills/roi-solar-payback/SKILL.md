---
name: roi-solar-payback
description: Calcula el retorno (ROI) y el periodo de recuperación (payback) de un sistema solar fotovoltaico para PyME o casa con el costo por kWh del recibo CFE, la generación estimada, la degradación de los paneles y el aumento anual de tarifa que el usuario suponga. Considera la deducción del 100% para equipo de energía renovable (Art. 34 fr. XIII LISR) y si la central entra como generación exenta (< 0.7 MW, Ley del Sector Eléctrico 2025). Usar cuando el usuario diga roi solar payback, cuánto tarda en pagarse, retorno de paneles solares, conviene poner paneles, recuperación de inversión solar, deducir paneles solares.
allowed-tools: Read, Write
---

# ROI y payback solar

## Datos de entrada

| Dato | Fuente |
|---|---|
| Inversión (sin IVA si la empresa acredita el IVA) | Cotización del instalador |
| kW instalados | Cotización |
| Generación mensual estimada (kWh) | Cotización o kW × horas solares pico × 30 × eficiencia (supuesto, decirlo) |
| Costo por kWh | Recibo CFE (importe de energía / kWh); no uses promedios nacionales |
| Esquema de contrato | Medición neta, facturación neta o venta total (ver `credito-kwh-tracking`) |
| Degradación anual | Ficha técnica del panel; si no la hay, supuesto declarado |
| Aumento anual de tarifa | Supuesto del usuario; si no da uno, calcula con 0% y dilo |

## Flujo

1. Clasifica la central: `cfe_solar_solicitar(rpu, kw_instalados, tarifa_actual)` (`mp_cfe_interconexion_solar`). Si es < 0.7 MW, es generación exenta sin permiso de la CNE; el tool devuelve los pasos como **handoff** (no presenta nada ante CFE).
2. Ahorro mensual: `cfe_solar_simular_ahorro(costo_kwh_mxn, kwh_consumo_promedio_mensual, kwh_generacion_solar_estimada, esquema)`. Usa su `ahorro_anual_mxn` y copia sus `supuestos`.
3. Payback simple = inversión / ahorro anual. Payback con degradación y aumento de tarifa: acumula año por año `ahorro_año_n = ahorro_1 × (1 − degradación)^(n−1) × (1 + aumento)^(n−1)` hasta igualar la inversión.
4. Reporta ambos y los supuestos. No uses un rango "típico" de años: depende de la tarifa (DAC y GDMTH recuperan más rápido que tarifa 1 subsidiada).

## Efecto fiscal (contribuyentes con actividad empresarial)

- **Art. 34 fr. XIII LISR**: deducción del 100% de la inversión en maquinaria y equipo para generar energía de fuentes renovables, si el equipo se mantiene en operación al menos 5 años después del ejercicio de la deducción; si no, se paga el ISR de la diferencia.
- Aplica a PM del régimen general y a PF con actividad empresarial (Art. 104 LISR remite a estas tasas). RESICO PF no deduce; RESICO PM tiene sus propias reglas de inversiones (verificar con contador).
- El beneficio es de flujo: deduces todo en el primer año en vez de depreciarlo. Ojo: el ahorro en luz también reduce un gasto deducible, así que no sumes el beneficio fiscal como ahorro extra sin hacer el cálculo después de impuestos.
- IVA de la inversión: acreditable si la actividad está gravada.

## Ejemplo

Sistema de 20 kW, inversión $300,000 sin IVA. Generación supuesta: 20 kW × 5 h × 30 días × 0.8 = 2,400 kWh/mes, todo autoconsumido. Costo del recibo: $3.00/kWh.

- Ahorro mensual = 2,400 × 3.00 = $7,200; anual = $86,400.
- Payback simple = 300,000 / 86,400 = **3.47 años**.
- Con PM al 30%: el ahorro después de ISR es 86,400 × 0.70 = $60,480 y el costo después de la deducción del 100% es 300,000 × 0.70 = $210,000; payback después de impuestos = 210,000 / 60,480 = 3.47 años. La deducción mejora la caja del año 1, no el plazo simple.

## Output

```json
{
  "kw_instalados": 20,
  "clasificacion": "generacion_distribuida_exenta",
  "inversion_mxn": 300000.00,
  "ahorro_anual_mxn": 86400.00,
  "payback_simple_anios": 3.47,
  "supuestos": ["5 horas solares pico", "eficiencia 0.8", "costo kWh del recibo $3.00", "aumento de tarifa 0%"],
  "deduccion_art34_xiii": {"aplica": true, "condicion": "operar 5 años"},
  "requiere_validacion": ["contador", "instalador certificado"]
}
```

## Advertencias

- Proyección con supuestos, no garantía de ahorro. Validar la generación con el instalador y el efecto fiscal con un contador.
- Precios de CFE: los del recibo del usuario; el MCP no publica tarifas (`cfe_solar_listar_tarifas` solo da nombres).
